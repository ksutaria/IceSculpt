"""Algorithmic pixmap generation for IceWM theme elements.

Generates XPM images for:
  - Window buttons (close, maximize, minimize, etc.) in active/inactive/rollover states
  - Frame border pieces (8 positions × active/inactive)
  - Title bar segments
  - LED clock digits
"""

from . import xpm_codec
from . import color_utils


def generate_button(button_type, size, bg_color, fg_color, state="A"):
    """Generate a window title bar button.

    Args:
        button_type: One of 'close', 'maximize', 'minimize', 'restore',
                     'rollup', 'rolldown', 'hide', 'depth', 'menu'.
        size: Button size in pixels (square).
        bg_color: Background color as #RRGGBB.
        fg_color: Foreground/symbol color as #RRGGBB.
        state: 'A' (active), 'I' (inactive), 'O' (rollover).

    Returns:
        XpmImage instance.
    """
    img = xpm_codec.XpmImage(size, size, cpp=1, _empty=True)

    # Colors: background, foreground, highlight (lighter bg), shadow (darker bg)
    highlight = color_utils.lighten(bg_color, 0.3)
    shadow = color_utils.darken(bg_color, 0.3)

    img.colors["."] = bg_color
    img.colors["X"] = fg_color
    img.colors["h"] = highlight
    img.colors["s"] = shadow

    # Fill with background
    img.pixels = ["." * size for _ in range(size)]

    # Draw 3D border effect
    for x in range(size):
        img.set_pixel(x, 0, "h")           # Top highlight
        img.set_pixel(x, size - 1, "s")     # Bottom shadow
    for y in range(size):
        img.set_pixel(0, y, "h")            # Left highlight
        img.set_pixel(size - 1, y, "s")     # Right shadow

    # Draw the symbol
    margin = max(3, size // 4)
    _draw_button_symbol(img, button_type, margin, size - margin - 1)

    return img


def _draw_button_symbol(img, button_type, lo, hi):
    """Draw the button symbol within the given bounds."""
    if button_type == "close":
        # X shape
        for i in range(hi - lo + 1):
            img.set_pixel(lo + i, lo + i, "X")
            img.set_pixel(hi - i, lo + i, "X")

    elif button_type == "maximize":
        # Rectangle outline
        for x in range(lo, hi + 1):
            img.set_pixel(x, lo, "X")
            img.set_pixel(x, lo + 1, "X")  # Thick top
            img.set_pixel(x, hi, "X")
        for y in range(lo, hi + 1):
            img.set_pixel(lo, y, "X")
            img.set_pixel(hi, y, "X")

    elif button_type == "minimize":
        # Underscore bar
        for x in range(lo, hi + 1):
            img.set_pixel(x, hi, "X")
            img.set_pixel(x, hi - 1, "X")

    elif button_type == "restore":
        # Two overlapping rectangles
        mid = (lo + hi) // 2
        offset = max(2, (hi - lo) // 4)
        # Back rectangle (offset)
        for x in range(lo + offset, hi + 1):
            img.set_pixel(x, lo, "X")
        for y in range(lo, hi - offset + 1):
            img.set_pixel(hi, y, "X")
        # Front rectangle
        for x in range(lo, hi - offset + 1):
            img.set_pixel(x, lo + offset, "X")
            img.set_pixel(x, hi, "X")
        for y in range(lo + offset, hi + 1):
            img.set_pixel(lo, y, "X")
            img.set_pixel(hi - offset, y, "X")

    elif button_type == "rollup":
        # Upward triangle/chevron
        mid_x = (lo + hi) // 2
        for i in range(0, (hi - lo) // 2 + 1):
            img.set_pixel(mid_x - i, hi - i, "X")
            img.set_pixel(mid_x + i, hi - i, "X")

    elif button_type == "rolldown":
        # Downward triangle/chevron
        mid_x = (lo + hi) // 2
        for i in range(0, (hi - lo) // 2 + 1):
            img.set_pixel(mid_x - i, lo + i, "X")
            img.set_pixel(mid_x + i, lo + i, "X")

    elif button_type == "hide":
        # Horizontal line in middle
        mid_y = (lo + hi) // 2
        for x in range(lo, hi + 1):
            img.set_pixel(x, mid_y, "X")

    elif button_type == "depth":
        # Two overlapping squares (like alt-tab)
        mid = (lo + hi) // 2
        for x in range(lo, mid + 1):
            img.set_pixel(x, lo, "X")
            img.set_pixel(x, mid, "X")
        for y in range(lo, mid + 1):
            img.set_pixel(lo, y, "X")
            img.set_pixel(mid, y, "X")
        for x in range(mid, hi + 1):
            img.set_pixel(x, mid, "X")
            img.set_pixel(x, hi, "X")
        for y in range(mid, hi + 1):
            img.set_pixel(mid, y, "X")
            img.set_pixel(hi, y, "X")

    elif button_type == "menu":
        # Three horizontal lines (hamburger menu)
        span = hi - lo
        for i in range(3):
            row_y = lo + (span * i) // 2
            for x in range(lo, hi + 1):
                img.set_pixel(x, row_y, "X")


def generate_frame_piece(position, width, height, bg_color, active=True):
    """Generate a frame border piece.

    Args:
        position: One of 'TL', 'T', 'TR', 'L', 'R', 'BL', 'B', 'BR'
                  (TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight).
        width: Piece width.
        height: Piece height.
        bg_color: Base color as #RRGGBB.
        active: True for active window, False for inactive.

    Returns:
        XpmImage instance.
    """
    highlight = color_utils.lighten(bg_color, 0.25)
    shadow = color_utils.darken(bg_color, 0.25)

    img = xpm_codec.XpmImage(width, height, cpp=1, _empty=True)
    img.colors["."] = bg_color
    img.colors["h"] = highlight
    img.colors["s"] = shadow

    img.pixels = ["." * width for _ in range(height)]

    # Draw 3D bevels based on position
    if position in ("TL", "T", "TR"):
        # Top edge highlight
        for x in range(width):
            img.set_pixel(x, 0, "h")
    if position in ("BL", "B", "BR"):
        # Bottom edge shadow
        for x in range(width):
            img.set_pixel(x, height - 1, "s")
    if position in ("TL", "L", "BL"):
        # Left edge highlight
        for y in range(height):
            img.set_pixel(0, y, "h")
    if position in ("TR", "R", "BR"):
        # Right edge shadow
        for y in range(height):
            img.set_pixel(width - 1, y, "s")

    return img


def generate_title_segment(segment, width, height, color1, color2=None):
    """Generate a title bar segment.

    Args:
        segment: Segment identifier (e.g. 'T', 'B', 'L', 'R', 'M', 'J', 'P', 'Q', 'S').
        width: Segment width.
        height: Segment height.
        color1: Primary color as #RRGGBB.
        color2: Optional secondary color for gradient. If None, solid fill.

    Returns:
        XpmImage instance.
    """
    if color2 and color2 != color1:
        return xpm_codec.create_gradient_h(width, height, color1, color2)
    return xpm_codec.create_solid(width, height, color1)


def generate_all_buttons(size, theme_model):
    """Generate a complete set of title bar buttons using theme colors.

    Args:
        size: Button size (typically TitleBarHeight - 4).
        theme_model: ThemeModel instance to read colors from.

    Returns:
        Dict mapping filename (e.g. 'closeA.xpm') to XpmImage.
    """
    m = theme_model
    results = {}

    button_types = {
        'close': 'x',
        'maximize': 'm',
        'minimize': 'i',
        'restore': 'r',
        'rollup': 'u',
        'rolldown': 'd',
        'hide': 'h',
        'depth': 'e',
        'menu': 'n',
    }

    states = {
        'A': {
            'bg': m.get_color_hex("ColorActiveButton", "#4C566A"),
            'fg': m.get_color_hex("ColorActiveTitleBarText", "#ECEFF4"),
        },
        'I': {
            'bg': m.get_color_hex("ColorNormalButton", "#3B4252"),
            'fg': m.get_color_hex("ColorNormalTitleBarText", "#D8DEE9"),
        },
    }

    # Add rollover state if supported
    if m.get_bool("RolloverButtonsSupported", False):
        states['O'] = {
            'bg': color_utils.lighten(states['A']['bg'], 0.15),
            'fg': states['A']['fg'],
        }

    for btn_name in button_types:
        for state_key, colors in states.items():
            img = generate_button(btn_name, size, colors['bg'], colors['fg'], state_key)
            filename = f"{btn_name}{state_key}.xpm"
            results[filename] = img

    return results


def generate_all_frames(border_x, border_y, corner_x, corner_y, theme_model):
    """Generate a complete set of frame border pieces.

    Args:
        border_x: Horizontal border width.
        border_y: Vertical border height.
        corner_x: Corner width.
        corner_y: Corner height.
        theme_model: ThemeModel instance.

    Returns:
        Dict mapping filename to XpmImage.
    """
    m = theme_model
    results = {}

    for active in (True, False):
        prefix = "A" if active else "I"
        color_key = "ColorActiveBorder" if active else "ColorNormalBorder"
        bg = m.get_color_hex(color_key, "#5E81AC" if active else "#4C566A")

        pieces = {
            f"frame{prefix}TL.xpm": ("TL", corner_x, corner_y),
            f"frame{prefix}T.xpm": ("T", border_x, border_y),
            f"frame{prefix}TR.xpm": ("TR", corner_x, corner_y),
            f"frame{prefix}L.xpm": ("L", border_x, border_y * 4),
            f"frame{prefix}R.xpm": ("R", border_x, border_y * 4),
            f"frame{prefix}BL.xpm": ("BL", corner_x, corner_y),
            f"frame{prefix}B.xpm": ("B", border_x, border_y),
            f"frame{prefix}BR.xpm": ("BR", corner_x, corner_y),
        }

        for filename, (position, w, h) in pieces.items():
            w = max(1, w)
            h = max(1, h)
            results[filename] = generate_frame_piece(position, w, h, bg, active)

    return results
