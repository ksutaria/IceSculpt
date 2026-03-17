#!/usr/bin/env python3
"""Render all generated XPM buttons and frame pieces into a labeled grid PNG."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cairo
from icesculpt.theme_model import ThemeModel
from icesculpt.pixmap_generator import generate_all_buttons, generate_all_frames
from icesculpt.color_utils import hex_to_rgba


def xpm_to_surface(xpm_img):
    """Convert an XpmImage to a Cairo ImageSurface."""
    w, h = xpm_img.width, xpm_img.height
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    cr = cairo.Context(surface)

    for y in range(h):
        for x in range(w):
            color_hex = xpm_img.get_color_at(x, y)
            if color_hex is None:
                continue  # transparent
            r, g, b, a = hex_to_rgba(color_hex)
            cr.set_source_rgb(r, g, b)
            cr.rectangle(x, y, 1, 1)
            cr.fill()

    return surface


def render_button_grid(buttons, path):
    """Render all buttons into a labeled grid PNG."""
    btn_size = 16  # typical button size
    scale = 3  # scale up for visibility
    cell_w = btn_size * scale + 80  # room for label
    cell_h = btn_size * scale + 10
    cols = 6
    rows = (len(buttons) + cols - 1) // cols

    width = cols * cell_w + 20
    height = rows * cell_h + 40

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)

    # Background
    cr.set_source_rgb(0.15, 0.15, 0.15)
    cr.rectangle(0, 0, width, height)
    cr.fill()

    # Title
    cr.set_source_rgb(1, 1, 1)
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(14)
    cr.move_to(10, 20)
    cr.show_text("Generated XPM Buttons")

    sorted_names = sorted(buttons.keys())
    for idx, name in enumerate(sorted_names):
        xpm_img = buttons[name]
        col = idx % cols
        row = idx // cols
        x = 10 + col * cell_w
        y = 35 + row * cell_h

        # Render the XPM at scale
        btn_surface = xpm_to_surface(xpm_img)
        cr.save()
        cr.translate(x, y)
        cr.scale(scale, scale)
        cr.set_source_surface(btn_surface, 0, 0)
        cr.get_source().set_filter(cairo.FILTER_NEAREST)
        cr.paint()
        cr.restore()

        # Label
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(9)
        cr.move_to(x + btn_size * scale + 4, y + btn_size * scale / 2 + 3)
        cr.show_text(name)

    surface.write_to_png(path)
    print(f"  Written: {path}")


def render_frame_grid(frames, path):
    """Render all frame pieces into a labeled grid PNG."""
    scale = 3
    cell_w = 140
    cell_h = 110
    cols = 4
    rows = (len(frames) + cols - 1) // cols

    width = cols * cell_w + 20
    height = rows * cell_h + 40

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)

    cr.set_source_rgb(0.15, 0.15, 0.15)
    cr.rectangle(0, 0, width, height)
    cr.fill()

    cr.set_source_rgb(1, 1, 1)
    cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(14)
    cr.move_to(10, 20)
    cr.show_text("Generated XPM Frame Pieces")

    sorted_names = sorted(frames.keys())
    for idx, name in enumerate(sorted_names):
        xpm_img = frames[name]
        col = idx % cols
        row = idx // cols
        x = 10 + col * cell_w
        y = 35 + row * cell_h

        # Label first
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(9)
        cr.move_to(x, y + 10)
        cr.show_text(name)

        # Clamp rendered size to fit cell
        render_w = min(xpm_img.width * scale, cell_w - 10)
        render_h = min(xpm_img.height * scale, cell_h - 30)
        sx = render_w / xpm_img.width
        sy = render_h / xpm_img.height

        btn_surface = xpm_to_surface(xpm_img)
        cr.save()
        cr.translate(x, y + 16)
        cr.scale(sx, sy)
        cr.set_source_surface(btn_surface, 0, 0)
        cr.get_source().set_filter(cairo.FILTER_NEAREST)
        cr.paint()
        cr.restore()

    surface.write_to_png(path)
    print(f"  Written: {path}")


if __name__ == "__main__":
    model = ThemeModel()
    btn_size = 16

    print("Generating buttons...")
    buttons = generate_all_buttons(btn_size, model)
    render_button_grid(buttons, "/tmp/pixmap_buttons.png")

    print("Generating frame pieces...")
    frames = generate_all_frames(
        border_x=6, border_y=6,
        corner_x=12, corner_y=12,
        theme_model=model
    )
    render_frame_grid(frames, "/tmp/pixmap_frames.png")

    print("Done!")
