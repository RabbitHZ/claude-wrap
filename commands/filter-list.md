# /filter-list

Lists the input filters currently registered in the claude-wrap plugin registry.

## Behavior

Scans the `claude_wrap/plugins/` directory and prints the plugins registered in the `PluginRegistry`.

## Execution

```bash
python -c "
from claude_wrap.plugins import registry
from claude_wrap.main import _setup_default_plugins

_setup_default_plugins()
plugins = registry.list_plugins()

if not plugins:
    print('No filters registered.')
else:
    print(f'Active filters ({len(plugins)}):')
    for i, name in enumerate(plugins, 1):
        print(f'  {i}. {name}')
"
```

## Example Output

```
Active filters (1):
  1. KittyKeyboardFilter
```
