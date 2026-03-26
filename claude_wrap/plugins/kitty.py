"""
Built-in plugin: Kitty Keyboard Protocol filter.

Strips escape sequences of the form  ESC [ <digits/semicolons/colons> u
that Terminal.app leaks when it partially supports the Kitty protocol.

Examples of filtered sequences:
    \\x1b[57358u  — Caps Lock (Korean/Japanese IME switch)
    \\x1b[57359u  — Shift modifier report
    \\x1b[57361u  — Ctrl modifier report
"""

import re

from claude_wrap.plugins import FilterPlugin


class KittyKeyboardFilter(FilterPlugin):
    """Remove Kitty Keyboard Protocol escape sequences from stdin."""

    # Matches:  ESC [  <one-or-more digits, semicolons, or colons>  u
    _PATTERN = re.compile(rb"\x1b\[[\d;:]+u")

    def filter(self, data: bytes) -> bytes:
        return self._PATTERN.sub(b"", data)
