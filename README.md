# claude-wrap

> PTY wrapper for [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) that filters **Kitty Keyboard Protocol** sequences interfering with IME input.

## Problem

Recent versions of Claude Code CLI began requesting the [Kitty Keyboard Protocol](https://sw.kovidgoyal.net/kitty/keyboard-protocol/) from the terminal. When using **macOS Terminal.app** (which does not fully support this protocol), pressing keys like **Caps Lock for Korean/Japanese IME switching** causes raw escape sequences to appear in the prompt:

```
> [57358u
```

This happens because Terminal.app partially forwards the Kitty sequences (`\x1b[57358u`, etc.) instead of silently dropping them.

## Solution

`claude-wrap` sits between your terminal and Claude Code as a PTY relay. It intercepts all keystrokes and **strips Kitty escape sequences** before they reach Claude Code — while passing everything else through transparently.

```
Terminal.app  ──stdin──▶  claude-wrap (filters \x1b[…u)  ──▶  claude
              ◀─stdout──                                  ◀────
```

## Requirements

- macOS or Linux
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed

## Installation

Register the marketplace and install the plugin inside Claude Code:

```
# Add to marketplace
/plugin marketplace add RabbitHZ/claude-wrap

# Install the plugin
/plugin install claude-wrap
```

Once installed, the following slash commands are available inside Claude Code:

| Command | Description |
|---|---|
| `/filter-list` | List active filter plugins |
| `/filter-add` | Scaffold a new filter plugin |
| `/filter-test` | Test bytes through the filter pipeline |

## How It Works

1. Forks a child process running `claude` inside a **pseudo-terminal (PTY)**
2. Relays all I/O between your terminal and the child process
3. On the **stdin path** (keystrokes going to Claude), applies a regex filter:
   ```
   \x1b\[[\d;:]*u  →  (removed)
   ```
   This removes sequences like `\x1b[57358u` (Caps Lock) while leaving normal input intact
4. Forwards **SIGWINCH** (terminal resize) to keep window sizing correct

## Filtered Sequences

| Sequence | Key |
|---|---|
| `\x1b[57358u` | Caps Lock |
| `\x1b[57359u` | Shift |
| `\x1b[57361u` | Ctrl |
| Any `\x1b[<digits>u` | Other Kitty-reported modifier keys |

## Affected Environments

| Terminal | Status |
|---|---|
| macOS Terminal.app | ✅ Fixed by claude-wrap |
| iTerm2 | ⚠️ Disable "CSI u" in Preferences instead |
| Kitty | ✅ Native support — not affected |
| WezTerm | ✅ Native support — not affected |

## Contributing

Issues and PRs welcome! If you use a non-Korean IME and encounter similar problems, please open an issue with your terminal app and OS version.

## License

MIT
