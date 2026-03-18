"""Convert between IceWM color formats and GTK RGBA.

IceWM uses several color formats:
  - rgb:RR/GG/BB  (hex pairs separated by slashes, e.g. rgb:FF/FF/FF)
  - #RRGGBB       (standard hex)
  - named X11 colors (e.g. "black", "white")

GTK uses Gdk.RGBA with float components 0.0–1.0.
"""

import re

# Common X11 color names used in IceWM themes
X11_COLORS = {
    "black": "#000000",
    "white": "#FFFFFF",
    "red": "#FF0000",
    "green": "#00FF00",
    "blue": "#0000FF",
    "yellow": "#FFFF00",
    "cyan": "#00FFFF",
    "magenta": "#FF00FF",
    "gray": "#BEBEBE",
    "grey": "#BEBEBE",
    "darkgray": "#A9A9A9",
    "darkgrey": "#A9A9A9",
    "lightgray": "#D3D3D3",
    "lightgrey": "#D3D3D3",
    "darkblue": "#00008B",
    "darkred": "#8B0000",
    "darkgreen": "#006400",
    "navy": "#000080",
    "maroon": "#800000",
    "olive": "#808000",
    "teal": "#008080",
    "silver": "#C0C0C0",
    "purple": "#800080",
    "orange": "#FFA500",
    "pink": "#FFC0CB",
    "brown": "#A52A2A",
    "gold": "#FFD700",
    "ivory": "#FFFFF0",
    "beige": "#F5F5DC",
    "coral": "#FF7F50",
    "salmon": "#FA8072",
    "khaki": "#F0E68C",
    "plum": "#DDA0DD",
    "orchid": "#DA70D6",
    "tan": "#D2B48C",
    "chocolate": "#D2691E",
    "firebrick": "#B22222",
    "sienna": "#A0522D",
    "indianred": "#CD5C5C",
    "peru": "#CD853F",
    "linen": "#FAF0E6",
    "lavender": "#E6E6FA",
    "lightblue": "#ADD8E6",
    "lightgreen": "#90EE90",
    "lightyellow": "#FFFFE0",
    "lightcyan": "#E0FFFF",
    "lightpink": "#FFB6C1",
    "lightsalmon": "#FFA07A",
    "lightcoral": "#F08080",
    "lightsteelblue": "#B0C4DE",
    "lightskyblue": "#87CEFA",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "darkslategray": "#2F4F4F",
    "darkslategrey": "#2F4F4F",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "slategray": "#708090",
    "slategrey": "#708090",
    "steelblue": "#4682B4",
    "royalblue": "#4169E1",
    "midnightblue": "#191970",
    "dodgerblue": "#1E90FF",
    "cornflowerblue": "#6495ED",
    "deepskyblue": "#00BFFF",
    "skyblue": "#87CEEB",
    "cadetblue": "#5F9EA0",
    "darkturquoise": "#00CED1",
    "mediumturquoise": "#48D1CC",
    "turquoise": "#40E0D0",
    "aquamarine": "#7FFFD4",
    "mediumaquamarine": "#66CDAA",
    "mediumseagreen": "#3CB371",
    "seagreen": "#2E8B57",
    "forestgreen": "#228B22",
    "limegreen": "#32CD32",
    "darkseagreen": "#8FBC8F",
    "yellowgreen": "#9ACD32",
    "springgreen": "#00FF7F",
    "mediumspringgreen": "#00FA9A",
    "lawngreen": "#7CFC00",
    "chartreuse": "#7FFF00",
    "greenyellow": "#ADFF2F",
    "darkolivegreen": "#556B2F",
    "olivedrab": "#6B8E23",
    "darkkhaki": "#BDB76B",
    "palegoldenrod": "#EEE8AA",
    "cornsilk": "#FFF8DC",
    "wheat": "#F5DEB3",
    "moccasin": "#FFE4B5",
    "navajowhite": "#FFDEAD",
    "peachpuff": "#FFDAB9",
    "bisque": "#FFE4C4",
    "blanchedalmond": "#FFEBCD",
    "papayawhip": "#FFEFD5",
    "oldlace": "#FDF5E6",
    "floralwhite": "#FFFAF0",
    "seashell": "#FFF5EE",
    "mistyrose": "#FFE4E1",
    "snow": "#FFFAFA",
    "mintcream": "#F5FFFA",
    "azure": "#F0FFFF",
    "ghostwhite": "#F8F8FF",
    "aliceblue": "#F0F8FF",
    "honeydew": "#F0FFF0",
    "whitesmoke": "#F5F5F5",
    "gainsboro": "#DCDCDC",
    "antiquewhite": "#FAEBD7",
    "lemonchiffon": "#FFFACD",
    "tomato": "#FF6347",
    "orangered": "#FF4500",
    "deeppink": "#FF1493",
    "hotpink": "#FF69B4",
    "mediumvioletred": "#C71585",
    "palevioletred": "#DB7093",
    "crimson": "#DC143C",
    "darkmagenta": "#8B008B",
    "darkorchid": "#9932CC",
    "darkviolet": "#9400D3",
    "blueviolet": "#8A2BE2",
    "mediumpurple": "#9370DB",
    "mediumorchid": "#BA55D3",
    "mediumslateblue": "#7B68EE",
    "slateblue": "#6A5ACD",
    "darkslateblue": "#483D8B",
    "indigo": "#4B0082",
    "rosybrown": "#BC8F8F",
    "sandybrown": "#F4A460",
    "goldenrod": "#DAA520",
    "darkgoldenrod": "#B8860B",
    "saddlebrown": "#8B4513",
}

_RGB_RE = re.compile(r'^rgb:([0-9a-fA-F]{1,2})/([0-9a-fA-F]{1,2})/([0-9a-fA-F]{1,2})$')
_HEX_RE = re.compile(r'^#([0-9a-fA-F]{6})$')
_HEX3_RE = re.compile(r'^#([0-9a-fA-F]{3})$')


def icewm_to_hex(color_str):
    """Convert an IceWM color string to #RRGGBB hex format.

    Args:
        color_str: Color in rgb:XX/XX/XX, #RRGGBB, #RGB, or X11 name format.

    Returns:
        Color as #RRGGBB string.

    Raises:
        ValueError: If the color string cannot be parsed.
    """
    s = color_str.strip()

    # rgb:XX/XX/XX format
    m = _RGB_RE.match(s)
    if m:
        r, g, b = m.groups()
        # Pad single-char hex values (e.g. rgb:F/0/0 -> rgb:FF/00/00)
        r = r.ljust(2, r[-1]) if len(r) == 1 else r
        g = g.ljust(2, g[-1]) if len(g) == 1 else g
        b = b.ljust(2, b[-1]) if len(b) == 1 else b
        return f"#{r.upper()}{g.upper()}{b.upper()}"

    # #RRGGBB format
    m = _HEX_RE.match(s)
    if m:
        return s.upper()

    # #RGB shorthand
    m = _HEX3_RE.match(s)
    if m:
        h = m.group(1)
        return f"#{h[0]}{h[0]}{h[1]}{h[1]}{h[2]}{h[2]}".upper()

    # X11 named color
    name = s.lower().replace(" ", "")
    if name in X11_COLORS:
        return X11_COLORS[name]

    raise ValueError(f"Cannot parse color: {color_str!r}")


def hex_to_icewm(hex_color):
    """Convert #RRGGBB to IceWM rgb:XX/XX/XX format.

    Args:
        hex_color: Color as #RRGGBB string.

    Returns:
        Color as rgb:XX/XX/XX string (uppercase hex).
    """
    h = hex_color.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"rgb:{r.upper()}/{g.upper()}/{b.upper()}"


def hex_to_rgba(hex_color):
    """Convert #RRGGBB to a (r, g, b, a) tuple with float 0.0–1.0 components.

    Returns:
        Tuple of (red, green, blue, alpha) floats.
        Falls back to mid-gray (0.5, 0.5, 0.5, 1.0) for malformed input.
    """
    try:
        h = hex_color.lstrip("#")
        if len(h) < 6:
            return (0.5, 0.5, 0.5, 1.0)
        r = int(h[0:2], 16) / 255.0
        g = int(h[2:4], 16) / 255.0
        b = int(h[4:6], 16) / 255.0
        return (r, g, b, 1.0)
    except (ValueError, TypeError, AttributeError):
        return (0.5, 0.5, 0.5, 1.0)


def rgba_to_hex(r, g, b, a=1.0):
    """Convert float RGBA components to #RRGGBB hex string.

    Args:
        r, g, b: Float components 0.0–1.0.
        a: Alpha (ignored in output).

    Returns:
        Color as #RRGGBB string.
    """
    ri = max(0, min(255, int(round(r * 255))))
    gi = max(0, min(255, int(round(g * 255))))
    bi = max(0, min(255, int(round(b * 255))))
    return f"#{ri:02X}{gi:02X}{bi:02X}"


def icewm_to_rgba(color_str):
    """Convert an IceWM color string directly to (r, g, b, a) floats."""
    return hex_to_rgba(icewm_to_hex(color_str))


def rgba_to_icewm(r, g, b, a=1.0):
    """Convert float RGBA to IceWM rgb:XX/XX/XX format."""
    return hex_to_icewm(rgba_to_hex(r, g, b, a))


def darken(hex_color, factor=0.2):
    """Darken a hex color by the given factor (0.0–1.0).

    factor=0.0 returns the original, factor=1.0 returns black.
    """
    r, g, b, a = hex_to_rgba(hex_color)
    r *= (1 - factor)
    g *= (1 - factor)
    b *= (1 - factor)
    return rgba_to_hex(r, g, b)


def lighten(hex_color, factor=0.2):
    """Lighten a hex color by the given factor (0.0–1.0).

    factor=0.0 returns the original, factor=1.0 returns white.
    """
    r, g, b, a = hex_to_rgba(hex_color)
    r += (1 - r) * factor
    g += (1 - g) * factor
    b += (1 - b) * factor
    return rgba_to_hex(r, g, b)


def blend(hex_color1, hex_color2, ratio=0.5):
    """Blend two hex colors. ratio=0.0 returns color1, ratio=1.0 returns color2."""
    r1, g1, b1, _ = hex_to_rgba(hex_color1)
    r2, g2, b2, _ = hex_to_rgba(hex_color2)
    r = r1 + (r2 - r1) * ratio
    g = g1 + (g2 - g1) * ratio
    b = b1 + (b2 - b1) * ratio
    return rgba_to_hex(r, g, b)


def get_luminance(hex_color):
    """Calculate the relative luminance of a color.
    
    Formula based on W3C relative luminance definition.
    """
    r, g, b, _ = hex_to_rgba(hex_color)

    def adjust(c):
        if c <= 0.03928:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    r = adjust(r)
    g = adjust(g)
    b = adjust(b)

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def get_contrast_ratio(hex1, hex2):
    """Calculate the contrast ratio between two colors (1.0 to 21.0)."""
    l1 = get_luminance(hex1)
    l2 = get_luminance(hex2)

    if l1 < l2:
        l1, l2 = l2, l1

    return (l1 + 0.05) / (l2 + 0.05)


def get_hls(hex_color):
    """Convert hex to HLS (0.0-1.0)."""
    import colorsys
    r, g, b, _ = hex_to_rgba(hex_color)
    return colorsys.rgb_to_hls(r, g, b)


def hls_to_hex(h, lum, s):
    """Convert HLS to hex."""
    import colorsys
    r, g, b = colorsys.hls_to_rgb(h, lum, s)
    return rgba_to_hex(r, g, b)
