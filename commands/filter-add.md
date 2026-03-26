# /filter-add

Creates a new input filter plugin file under `claude_wrap/plugins/`.

## Usage

```
/filter-add <plugin_name> <description>
```

## Example

```
/filter-add BracketPasteFilter "Remove bracket paste mode sequences"
```

## Behavior

1. Parses the plugin name and description from `$ARGUMENTS`.
2. Creates `claude_wrap/plugins/<snake_case_name>.py` using the template below.
3. Asks whether to add a registration line to `_setup_default_plugins()` in `main.py`.

## Generated Template

```python
import re
from claude_wrap.plugins import FilterPlugin


class $PluginClassName(FilterPlugin):
    """$description"""

    _PATTERN = re.compile(rb"")  # TODO: replace with actual pattern

    def filter(self, data: bytes) -> bytes:
        return self._PATTERN.sub(b"", data)
```

## Notes

- The class name is automatically converted to PascalCase.
- The filename is automatically converted to snake_case.
- After creation, fill in `_PATTERN` with the actual regex.
