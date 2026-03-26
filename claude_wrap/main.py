"""
claude-wrap entry point.

Registers built-in filter plugins, then starts the PTY relay.
To add a custom plugin before launch, import this module and call
    claude_wrap.plugins.registry.register(YourPlugin())
before invoking main().
"""

import sys

from claude_wrap.core import PTYRelay
from claude_wrap.plugins import registry
from claude_wrap.plugins.kitty import KittyKeyboardFilter


def main() -> None:
    registry.register(KittyKeyboardFilter())
    relay = PTYRelay(registry)
    sys.exit(relay.run(sys.argv[1:]))


if __name__ == "__main__":
    main()
