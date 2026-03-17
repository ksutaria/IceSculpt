"""Read, write, and generate XPM (X PixMap) image files.

XPM is a text-based image format used extensively by IceWM for theme
pixmaps (buttons, borders, title bars). This codec handles XPM2 and
XPM3 formats without any external image library dependencies.

XPM3 format structure:
    /* XPM */
    static char *name[] = {
    "width height ncolors cpp",
    "char  c #RRGGBB",
    ...
    "pixel_row",
    ...
    };
"""

import os
import re


class XpmImage:
    """An XPM image in memory.

    Attributes:
        width: Image width in pixels.
        height: Image height in pixels.
        colors: Dict mapping character(s) to color string (#RRGGBB or "None" for transparent).
        pixels: List of strings, each string is one row of pixel characters.
        cpp: Characters per pixel.
    """

    def __init__(self, width=1, height=1, cpp=1, _empty=False):
        self.width = width
        self.height = height
        self.cpp = cpp
        self.colors = {}  # char(s) -> color string
        if _empty:
            # Used by parsers/generators that populate pixels themselves
            self.pixels = []
        else:
            # Default to a filled image so accessors never hit an empty list
            self.colors[" " * cpp] = "#C0C0C0"
            self.pixels = [(" " * cpp) * width] * height

    def get_pixel(self, x, y):
        """Get the color character(s) at position (x, y)."""
        if 0 <= y < self.height and 0 <= x < self.width and y < len(self.pixels):
            start = x * self.cpp
            row = self.pixels[y]
            if start + self.cpp <= len(row):
                return row[start:start + self.cpp]
        return None

    def set_pixel(self, x, y, char):
        """Set the color character(s) at position (x, y)."""
        if 0 <= y < self.height and 0 <= x < self.width and y < len(self.pixels):
            row = self.pixels[y]
            start = x * self.cpp
            if start + self.cpp <= len(row):
                self.pixels[y] = row[:start] + char + row[start + self.cpp:]

    def get_color_at(self, x, y):
        """Get the color string (#RRGGBB or None) at position (x, y)."""
        char = self.get_pixel(x, y)
        if char is not None:
            color = self.colors.get(char, "#000000")
            if color.lower() == "none":
                return None
            return color
        return None

    def to_xpm3(self, name="image"):
        """Generate XPM3 format string.

        Args:
            name: Variable name in the XPM header.

        Returns:
            Complete XPM3 file content as a string.
        """
        lines = []
        lines.append("/* XPM */")
        lines.append(f"static char *{name}[] = {{")
        lines.append(f'"{self.width} {self.height} {len(self.colors)} {self.cpp}",')

        for char, color in self.colors.items():
            if color is None or color.lower() == "none":
                lines.append(f'"{char}\tc None",')
            else:
                lines.append(f'"{char}\tc {color}",')

        for i, row in enumerate(self.pixels):
            comma = "," if i < self.height - 1 else ""
            lines.append(f'"{row}"{comma}')

        lines.append("};")
        return "\n".join(lines)

    def clone(self):
        """Create a deep copy of this image."""
        img = XpmImage(self.width, self.height, self.cpp, _empty=True)
        img.colors = dict(self.colors)
        img.pixels = list(self.pixels)
        return img


# Characters for color allocation (single cpp)
_ALLOC_CHARS = (
    " .+@#$%&*=-;:>,<1234567890"
    "qwertyuiopasdfghjklzxcvbnm"
    "QWERTYUIOPASDFGHJKLZXCVBNM"
    "!~^/()_{}|[]`"
)


def _allocate_char(used_chars, cpp=1):
    """Allocate the next unused character(s) for a color entry."""
    if cpp == 1:
        for c in _ALLOC_CHARS:
            if c not in used_chars:
                return c
        raise ValueError("Ran out of single characters for XPM colors")
    else:
        # Multi-char allocation
        for c1 in _ALLOC_CHARS:
            for c2 in _ALLOC_CHARS:
                key = c1 + c2
                if key not in used_chars:
                    return key
        raise ValueError("Ran out of character pairs for XPM colors")


def create_solid(width, height, color="#000000"):
    """Create a solid-color XPM image.

    Args:
        width: Image width.
        height: Image height.
        color: Fill color as #RRGGBB, or None for transparent.

    Returns:
        XpmImage instance.
    """
    img = XpmImage(width, height, cpp=1, _empty=True)
    if color is None:
        img.colors["."] = "None"
    else:
        img.colors["."] = color
    img.pixels = ["." * width] * height
    return img


def create_gradient_h(width, height, color1, color2):
    """Create a horizontal gradient XPM (left to right).

    Args:
        width: Image width.
        height: Image height.
        color1: Start color (#RRGGBB).
        color2: End color (#RRGGBB).

    Returns:
        XpmImage instance.
    """
    # Determine cpp needed
    cpp = 1 if width <= len(_ALLOC_CHARS) else 2
    img = XpmImage(width, height, cpp, _empty=True)

    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)

    used = set()
    col_chars = []
    for x in range(width):
        t = x / max(1, width - 1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        hex_color = f"#{r:02X}{g:02X}{b:02X}"

        char = _allocate_char(used, cpp)
        used.add(char)
        img.colors[char] = hex_color
        col_chars.append(char)

    row = "".join(col_chars)
    img.pixels = [row] * height
    return img


def create_gradient_v(width, height, color1, color2):
    """Create a vertical gradient XPM (top to bottom).

    Args:
        width: Image width.
        height: Image height.
        color1: Start color (#RRGGBB).
        color2: End color (#RRGGBB).

    Returns:
        XpmImage instance.
    """
    cpp = 1 if height <= len(_ALLOC_CHARS) else 2
    img = XpmImage(width, height, cpp, _empty=True)

    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)

    used = set()
    for y in range(height):
        t = y / max(1, height - 1)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        hex_color = f"#{r:02X}{g:02X}{b:02X}"

        char = _allocate_char(used, cpp)
        used.add(char)
        img.colors[char] = hex_color
        img.pixels.append(char * width)

    return img


def _hex_to_rgb(hex_color):
    """Convert #RRGGBB to (r, g, b) integers."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r, g, b):
    """Convert (r, g, b) integers to #RRGGBB."""
    return f"#{r:02X}{g:02X}{b:02X}"


# -- Parsing --

_HEADER_RE = re.compile(r'"(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"')
_COLOR_RE = re.compile(r'"(.+?)\s+c\s+(.+?)"', re.IGNORECASE)


def parse_xpm(text):
    """Parse XPM3 format text into an XpmImage.

    Args:
        text: XPM file content as a string.

    Returns:
        XpmImage instance.

    Raises:
        ValueError: If the format cannot be parsed.
    """
    # Extract all quoted strings
    strings = re.findall(r'"([^"]*)"', text)
    if not strings:
        raise ValueError("No quoted strings found in XPM data")

    # First string is the header: "width height ncolors cpp"
    header = strings[0]
    parts = header.split()
    if len(parts) < 4:
        raise ValueError(f"Invalid XPM header: {header!r}")

    width = int(parts[0])
    height = int(parts[1])
    ncolors = int(parts[2])
    cpp = int(parts[3])

    img = XpmImage(width, height, cpp, _empty=True)

    # Next ncolors strings are color definitions
    for i in range(1, 1 + ncolors):
        if i >= len(strings):
            raise ValueError(f"Expected {ncolors} color entries, got {i - 1}")
        color_str = strings[i]
        # The character(s) are the first cpp characters
        char = color_str[:cpp]
        # Find the color value after 'c' key
        rest = color_str[cpp:]
        m = re.search(r'\bc\s+(\S+)', rest, re.IGNORECASE)
        if m:
            color_val = m.group(1)
            if color_val.lower() == "none":
                img.colors[char] = "None"
            else:
                img.colors[char] = color_val
        else:
            img.colors[char] = "#000000"

    # Remaining strings are pixel rows
    pixel_start = 1 + ncolors
    for i in range(pixel_start, pixel_start + height):
        if i >= len(strings):
            raise ValueError(f"Expected {height} pixel rows, got {i - pixel_start}")
        img.pixels.append(strings[i])

    return img


def read_xpm_file(filepath):
    """Read an XPM file from disk.

    Args:
        filepath: Path to the .xpm file.

    Returns:
        XpmImage instance.
    """
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        return parse_xpm(f.read())


def write_xpm_file(filepath, image, name=None):
    """Write an XpmImage to an XPM3 file.

    Args:
        filepath: Output file path.
        image: XpmImage instance.
        name: Variable name (defaults to filename stem).
    """
    if name is None:
        name = os.path.splitext(os.path.basename(filepath))[0]
        # Sanitize for C identifier
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)

    dir_path = os.path.dirname(filepath)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(image.to_xpm3(name))
        f.write("\n")
