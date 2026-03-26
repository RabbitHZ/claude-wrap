"""
PTY relay engine for claude-wrap.

PTYRelay forks the real `claude` binary inside a pseudo-terminal,
then relays I/O between the user's terminal and the child process.
On the stdin path each chunk passes through the plugin registry so
registered FilterPlugins can strip or transform bytes before they
reach Claude Code.
"""

import fcntl
import os
import pty
import select
import shutil
import signal
import struct
import sys
import termios
import tty

from claude_wrap.plugins import PluginRegistry


class PTYRelay:
    """Relay between the user's terminal and a Claude Code child process."""

    def __init__(self, registry: PluginRegistry) -> None:
        self._registry = registry

    def _propagate_winsize(self, src_fd: int, dst_fd: int) -> None:
        try:
            size = fcntl.ioctl(src_fd, termios.TIOCGWINSZ, b"\x00" * 8)
        except OSError:
            size = struct.pack("HHHH", 24, 80, 0, 0)
        try:
            fcntl.ioctl(dst_fd, termios.TIOCSWINSZ, size)
        except OSError:
            pass

    def run(self, claude_args: list[str]) -> int:
        """
        Fork `claude` inside a PTY, relay I/O, and return its exit code.
        stdin bytes are passed through the plugin registry before forwarding.
        """
        claude_bin = shutil.which("claude")
        if not claude_bin:
            print("claude-wrap: 'claude' command not found in PATH.", file=sys.stderr)
            return 1

        master_fd, slave_fd = pty.openpty()

        pid = os.fork()
        if pid == 0:
            self._run_child(master_fd, slave_fd, claude_bin, claude_args)

        # Parent process
        os.close(slave_fd)
        return self._run_parent(pid, master_fd)

    def _run_child(
        self,
        master_fd: int,
        slave_fd: int,
        claude_bin: str,
        claude_args: list[str],
    ) -> None:
        os.close(master_fd)
        os.setsid()
        fcntl.ioctl(slave_fd, termios.TIOCSCTTY, 0)
        for std_fd in (0, 1, 2):
            os.dup2(slave_fd, std_fd)
        if slave_fd > 2:
            os.close(slave_fd)
        os.execv(claude_bin, [claude_bin] + claude_args)
        sys.exit(1)  # execv failed

    def _run_parent(self, pid: int, master_fd: int) -> int:
        stdin_fd = sys.stdin.fileno()
        stdout_fd = sys.stdout.fileno()

        self._propagate_winsize(stdout_fd, master_fd)

        def on_resize(signum: int, frame: object) -> None:
            self._propagate_winsize(stdout_fd, master_fd)

        signal.signal(signal.SIGWINCH, on_resize)

        old_attr = termios.tcgetattr(stdin_fd)
        tty.setraw(stdin_fd)

        exit_code = 0
        try:
            while True:
                try:
                    r, _, _ = select.select([stdin_fd, master_fd], [], [], 0.05)
                except (select.error, ValueError):
                    break

                # stdin → master  (user keystrokes → Claude, filtered)
                if stdin_fd in r:
                    try:
                        data = os.read(stdin_fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    filtered = self._registry.apply(data)
                    if filtered:
                        try:
                            os.write(master_fd, filtered)
                        except OSError:
                            break

                # master → stdout  (Claude output → terminal, unmodified)
                if master_fd in r:
                    try:
                        data = os.read(master_fd, 4096)
                    except OSError:
                        break
                    if not data:
                        break
                    os.write(stdout_fd, data)

                # Check if child has exited
                waited_pid, status = os.waitpid(pid, os.WNOHANG)
                if waited_pid != 0:
                    exit_code = os.waitstatus_to_exitcode(status)
                    break

        finally:
            termios.tcsetattr(stdin_fd, termios.TCSADRAIN, old_attr)
            try:
                os.waitpid(pid, 0)
            except ChildProcessError:
                pass

        return exit_code
