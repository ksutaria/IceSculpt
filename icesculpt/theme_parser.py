"""Parse and write IceWM default.theme files with round-trip fidelity.

IceWM theme files are key=value text files. Lines may be:
  - blank
  - comments (starting with #)
  - key=value pairs (with optional surrounding whitespace)
  - key="quoted value"

The parser preserves comments, blank lines, and ordering so that
saving a file after loading produces minimal diffs.
"""

import os
import re


class ThemeLine:
    """A single line from a theme file, preserving its original text."""

    __slots__ = ("raw", "key", "value", "comment_only", "blank")

    def __init__(self, raw, key=None, value=None, comment_only=False, blank=False):
        self.raw = raw
        self.key = key
        self.value = value
        self.comment_only = comment_only
        self.blank = blank

    def to_string(self):
        """Reconstruct the line for writing."""
        if self.blank:
            return ""
        if self.comment_only:
            return self.raw
        if self.key is not None:
            # Preserve quoting for values that need it
            if self._needs_quoting(self.value):
                return f'{self.key}="{self.value}"'
            return f"{self.key}={self.value}"
        return self.raw

    @staticmethod
    def _needs_quoting(value):
        """Check if a value needs quoting (contains spaces, commas, or special chars)."""
        if not value:
            return False
        # Quote if value contains spaces (unless it looks like a file path or color)
        if " " in value and not value.startswith("rgb:") and not value.startswith("/"):
            return True
        if '"' in value:
            return False  # Already has quotes internally, don't double-quote
        return False


_KV_RE = re.compile(r'^(\s*)([A-Za-z][A-Za-z0-9_]*)\s*=\s*(.*)$')


def parse_theme_file(filepath):
    """Parse a theme file into a list of ThemeLine objects.

    Args:
        filepath: Path to the default.theme file.

    Returns:
        List of ThemeLine objects preserving file structure.

    Raises:
        FileNotFoundError: If the file doesn't exist.
    """
    lines = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for raw_line in f:
            raw = raw_line.rstrip("\n\r")
            stripped = raw.strip()

            # Blank line
            if not stripped:
                lines.append(ThemeLine(raw, blank=True))
                continue

            # Comment line
            if stripped.startswith("#"):
                lines.append(ThemeLine(raw, comment_only=True))
                continue

            # Key=value line
            m = _KV_RE.match(raw)
            if m:
                key = m.group(2)
                value = m.group(3).strip()
                # Remove surrounding quotes
                if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                    value = value[1:-1]
                lines.append(ThemeLine(raw, key=key, value=value))
                continue

            # Unparseable line — preserve as-is
            lines.append(ThemeLine(raw))

    return lines


def extract_values(lines):
    """Extract a key→value dict from parsed lines.

    Args:
        lines: List of ThemeLine objects.

    Returns:
        Dict mapping key names to their string values.
    """
    result = {}
    for line in lines:
        if line.key is not None:
            result[line.key] = line.value
    return result


def update_value(lines, key, new_value):
    """Update a key's value in the parsed lines, or append if not found.

    Args:
        lines: List of ThemeLine objects (modified in place).
        key: The setting key name.
        new_value: The new string value.

    Returns:
        True if an existing line was updated, False if a new line was appended.
    """
    for line in lines:
        if line.key == key:
            line.value = new_value
            return True
    # Key not found — append
    lines.append(ThemeLine(f"{key}={new_value}", key=key, value=new_value))
    return False


def remove_key(lines, key):
    """Remove a key from the parsed lines.

    Args:
        lines: List of ThemeLine objects (modified in place).
        key: The key to remove.

    Returns:
        True if the key was found and removed.
    """
    for i, line in enumerate(lines):
        if line.key == key:
            lines.pop(i)
            return True
    return False


def write_theme_file(filepath, lines):
    """Write parsed theme lines back to a file.

    Args:
        filepath: Output file path.
        lines: List of ThemeLine objects.
    """
    dir_path = os.path.dirname(filepath)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line.to_string() + "\n")


def create_empty_theme(theme_name="New Theme", author=""):
    """Create a minimal set of ThemeLine objects for a new theme.

    Args:
        theme_name: Theme description/name.
        author: Theme author name.

    Returns:
        List of ThemeLine objects for a minimal valid theme.
    """
    raw_lines = [
        f'# {theme_name}',
        '#',
        f'ThemeDescription="{theme_name}"',
        f'ThemeAuthor="{author}"',
        'License="GPL-2.0-or-later"',
        '',
        '# Look style',
        'Look=flat',
        '',
        '# Title bar colors',
        'ColorActiveTitleBar="rgb:00/00/80"',
        'ColorActiveTitleBarText="rgb:FF/FF/FF"',
        'ColorNormalTitleBar="rgb:C0/C0/C0"',
        'ColorNormalTitleBarText="rgb:00/00/00"',
        '',
        '# Border colors',
        'ColorActiveBorder="rgb:00/00/80"',
        'ColorNormalBorder="rgb:C0/C0/C0"',
        '',
        '# Menu colors',
        'ColorNormalMenu="rgb:C0/C0/C0"',
        'ColorNormalMenuItemText="rgb:00/00/00"',
        'ColorActiveMenuItem="rgb:00/00/80"',
        'ColorActiveMenuItemText="rgb:FF/FF/FF"',
        '',
        '# Taskbar colors',
        'ColorDefaultTaskBar="rgb:C0/C0/C0"',
        '',
        '# Dimensions',
        'BorderSizeX=6',
        'BorderSizeY=6',
        'TitleBarHeight=20',
        'CornerSizeX=24',
        'CornerSizeY=24',
    ]
    return parse_theme_file_from_string("\n".join(raw_lines))


def parse_theme_file_from_string(text):
    """Parse theme data from a string instead of a file.

    Args:
        text: Theme file content as a string.

    Returns:
        List of ThemeLine objects.
    """
    lines = []
    for raw_line in text.split("\n"):
        raw = raw_line.rstrip("\r")
        stripped = raw.strip()

        if not stripped:
            lines.append(ThemeLine(raw, blank=True))
            continue

        if stripped.startswith("#"):
            lines.append(ThemeLine(raw, comment_only=True))
            continue

        m = _KV_RE.match(raw)
        if m:
            key = m.group(2)
            value = m.group(3).strip()
            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
            lines.append(ThemeLine(raw, key=key, value=value))
            continue

        lines.append(ThemeLine(raw))

    return lines
