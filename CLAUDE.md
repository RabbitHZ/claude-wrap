# CLAUDE.md

This file provides guidance for Claude Code when working in this repository.

## Project Overview

`claude-wrap` is a PTY wrapper for the Claude Code CLI. It intercepts stdin keystrokes and strips **Kitty Keyboard Protocol** escape sequences (e.g. `\x1b[57358u`) that macOS Terminal.app leaks, causing raw garbage to appear in the prompt when using IME input (Korean, Japanese, etc.).

```
Terminal.app  ──stdin──▶  claude-wrap (filters \x1b[…u)  ──▶  claude
              ◀─stdout──                                  ◀────
```

## Project Structure

```
claude_wrap/
  core.py          # PTYRelay — forks claude in a PTY, relays I/O
  main.py          # Entry point — registers default plugins, starts relay
  plugins/
    __init__.py    # FilterPlugin base class + PluginRegistry
    kitty.py       # KittyKeyboardFilter (built-in, active by default)
commands/          # Claude Code slash command definitions
  filter-add.md
  filter-list.md
  filter-test.md
agents/            # Claude Code agent definitions
  filter-manager.md
```

## Architecture

- **`PTYRelay`** (`core.py`) — PTY engine. Never touch this to add filter logic; it must stay filter-agnostic.
- **`FilterPlugin`** (`plugins/__init__.py`) — Abstract base class. Subclass it to create a new filter.
- **`PluginRegistry`** (`plugins/__init__.py`) — Ordered pipeline. Plugins are applied in registration order on every stdin chunk.
- **`main.py`** — Registers `KittyKeyboardFilter` and starts the relay. Add new default plugins here via `registry.register()` inside `main()`.

## Adding a New Filter Plugin

1. Create `claude_wrap/plugins/<name>.py` with one `FilterPlugin` subclass.
2. Use the template:
   ```python
   import re
   from claude_wrap.plugins import FilterPlugin

   class MyFilter(FilterPlugin):
       """One-line description of what this filter removes."""
       _PATTERN = re.compile(rb"<pattern>")

       def filter(self, data: bytes) -> bytes:
           return self._PATTERN.sub(b"", data)
   ```
3. To activate by default, add `registry.register(MyFilter())` in `main.py`.

## Key Rules

- **Never edit `core.py`** for filter-related changes.
- **One plugin per file** in `claude_wrap/plugins/`.
- **Test after any plugin change:**
  ```bash
  python -c "
  from claude_wrap.plugins import registry
  from claude_wrap.plugins.kitty import KittyKeyboardFilter
  registry.register(KittyKeyboardFilter())
  print(repr(registry.apply(b'hello\x1b[57358uworld')))
  "
  ```

## Git Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short summary>
```

**Types:**

| Type | When to use |
|---|---|
| `feat` | New feature or plugin |
| `fix` | Bug fix |
| `refactor` | Code change with no feature or fix |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Build, config, dependency updates |

**Examples:**

```
feat(plugins): add BracketPasteFilter
fix(core): handle OSError on PTY close
docs(readme): update installation instructions
chore: bump version to 0.3.0
```

**Rules:**
- Summary in lowercase, no period at the end
- Keep the summary under 72 characters
- Use the body for explaining *why*, not *what*

## Development Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Slash Commands

| Command | Description |
|---|---|
| `/filter-list` | List active filter plugins |
| `/filter-add` | Scaffold a new filter plugin file |
| `/filter-test` | Test input bytes through the filter pipeline |
