#!/usr/bin/env python3
"""Headless Cairo preview rendering — outputs PNGs for visual verification."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cairo
from icesculpt.theme_model import ThemeModel
from icesculpt.preview_renderer import PreviewRenderer


def make_default_model():
    """Create a ThemeModel with Nord-like defaults (the built-in fallbacks)."""
    model = ThemeModel()
    # The renderer uses get_color_rgba with Nord defaults already hardcoded
    return model


def render_full_preview(model, path, width=800, height=600):
    """Render the full desktop preview scene to a PNG."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)
    renderer = PreviewRenderer(model)
    renderer.render(cr, width, height)
    surface.write_to_png(path)
    print(f"  Written: {path}")


def render_menu_preview(model, path, width=200, height=200):
    """Render a menu preview to a PNG."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)
    # Fill background
    cr.set_source_rgb(0.2, 0.2, 0.2)
    cr.rectangle(0, 0, width, height)
    cr.fill()
    renderer = PreviewRenderer(model)
    renderer.render_menu_preview(cr, 20, 20, 160)
    surface.write_to_png(path)
    print(f"  Written: {path}")


def render_tooltip_preview(model, path, width=300, height=100):
    """Render a tooltip preview to a PNG."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)
    cr.set_source_rgb(0.2, 0.2, 0.2)
    cr.rectangle(0, 0, width, height)
    cr.fill()
    renderer = PreviewRenderer(model)
    renderer.render_tooltip_preview(cr, 20, 20)
    surface.write_to_png(path)
    print(f"  Written: {path}")


if __name__ == "__main__":
    print("Rendering previews with default model...")
    model = make_default_model()

    render_full_preview(model, "/tmp/preview_default.png")
    render_menu_preview(model, "/tmp/preview_menu.png")
    render_tooltip_preview(model, "/tmp/preview_tooltip.png")

    print("Done!")
