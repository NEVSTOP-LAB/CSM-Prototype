"""Safe string conversion utilities.

This module provides two functions:
- make_string_arguments_safe: CSM - Make String Arguments Safe.vi equivalent.
- revert_arguments_safe_string: CSM - Revert Arguments-Safe String.vi equivalent.

The escaping behavior follows CSM keyword-safe conventions:
- Escape CSM keyword characters using ``%HH`` uppercase hex.
- ``%`` is also escaped to keep decoding unambiguous.
"""

from __future__ import annotations

_HEX_DIGITS = set("0123456789ABCDEFabcdef")
_ESCAPE = "%"
_SAFE_STRING_TYPE = "<SAFESTR>"

# Character-based conservative escaping for CSM keyword safety.
# We escape all characters that appear in documented keyword patterns
# (->, ->|, -@, -&, <-, \r, \n, //, >>, >>>, ;, ,), regardless of context.
_CSM_KEYWORD_CHARS = set("-|@&<>\r\n/;,")
_ESCAPED_CHARS = _CSM_KEYWORD_CHARS | {_ESCAPE}


def make_string_arguments_safe(argument_string: str, ignore_argument_type: bool = False) -> str:
    """CSM - Make String Arguments Safe.vi equivalent.

    Args:
        argument_string: String argument.
        ignore_argument_type: If True, do not prepend ``<SAFESTR>``.

    Returns:
        Safe argument string.
    """
    if not isinstance(argument_string, str):
        raise TypeError("argument_string must be str")
    if not isinstance(ignore_argument_type, bool):
        raise TypeError("ignore_argument_type must be bool")

    encoded_parts: list[str] = []
    for ch in argument_string:
        if ch in _ESCAPED_CHARS:
            encoded_parts.append(f"{_ESCAPE}{ord(ch):02X}")
        else:
            encoded_parts.append(ch)
    safe_argument_string = "".join(encoded_parts)
    if ignore_argument_type:
        return safe_argument_string
    return f"{_SAFE_STRING_TYPE}{safe_argument_string}"


def revert_arguments_safe_string(safe_argument_string: str, force_convert: bool = False) -> str:
    """CSM - Revert Arguments-Safe String.vi equivalent.

    Args:
        safe_argument_string: Safe string argument.
        force_convert: Convert even when argument type is not ``SAFESTR``.

    Returns:
        Origin argument string.

    Raises:
        ValueError: If input is malformed.
    """
    if not isinstance(safe_argument_string, str):
        raise TypeError("safe_argument_string must be str")
    if not isinstance(force_convert, bool):
        raise TypeError("force_convert must be bool")

    encoded_text = safe_argument_string
    if safe_argument_string.startswith(_SAFE_STRING_TYPE):
        encoded_text = safe_argument_string[len(_SAFE_STRING_TYPE) :]
    elif not force_convert:
        return safe_argument_string

    result: list[str] = []
    i = 0
    length = len(encoded_text)

    while i < length:
        ch = encoded_text[i]
        if ch == _ESCAPE:
            if i + 2 >= length:
                raise ValueError("Malformed safe string: incomplete escape sequence")
            h1, h2 = encoded_text[i + 1], encoded_text[i + 2]
            if h1 not in _HEX_DIGITS or h2 not in _HEX_DIGITS:
                raise ValueError("Malformed safe string: invalid hex escape")
            result.append(chr(int(h1 + h2, 16)))
            i += 3
            continue

        result.append(ch)
        i += 1

    return "".join(result)


def to_safe_string(text: str) -> str:
    """Backward-compatible alias without SAFESTR type prefix."""
    return make_string_arguments_safe(argument_string=text, ignore_argument_type=True)


def from_safe_string(safe_text: str) -> str:
    """Backward-compatible alias that always converts."""
    return revert_arguments_safe_string(safe_argument_string=safe_text, force_convert=True)
