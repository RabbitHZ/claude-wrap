# /filter-test

Passes an arbitrary byte string through the registered filter pipeline and shows the result.

## Usage

```
/filter-test <input_string>
```

Escape sequences should be provided in Python literal format.

## Example

```
/filter-test "hello\x1b[57358uworld"
```

## Behavior

Interprets `$ARGUMENTS` as Python bytes, passes it through the entire active filter pipeline,
and prints the input and output side by side.

```bash
python -c "
import sys
from claude_wrap.plugins import registry
from claude_wrap.main import _setup_default_plugins

_setup_default_plugins()

raw = b'$ARGUMENTS'
result = registry.apply(raw)

print('input:', repr(raw))
print('output:', repr(result))
removed = len(raw) - len(result)
print(f'bytes removed: {removed}')
"
```

## Example Output

```
input:  b'hello\x1b[57358uworld'
output: b'helloworld'
bytes removed: 9
```
