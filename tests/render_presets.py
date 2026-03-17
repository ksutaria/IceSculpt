#!/usr/bin/env python3
"""Render each preset's preview and tile them into a 2x2 comparison PNG."""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import cairo
from icesculpt.theme_model import ThemeModel
from icesculpt.preview_renderer import PreviewRenderer

PRESETS_DIR = os.path.join(os.path.dirname(__file__), "..", "icesculpt", "data", "presets")


def load_preset_model(preset_path):
    """Load a preset JSON and return a ThemeModel with those values."""
    with open(preset_path) as f:
        data = json.load(f)
    model = ThemeModel()
    for key, value in data.get("colors", {}).items():
        model.values[key] = value
    return model, data.get("name", os.path.basename(preset_path))


def render_preset_tile(model, width, height):
    """Render a single preset preview to a Cairo surface."""
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)
    renderer = PreviewRenderer(model)
    renderer.render(cr, width, height)
    return surface


if __name__ == "__main__":
    tile_w, tile_h = 400, 300
    preset_files = sorted(
        f for f in os.listdir(PRESETS_DIR) if f.endswith(".json")
    )

    cols = 2
    rows = (len(preset_files) + 1) // 2
    label_h = 24
    total_w = cols * tile_w
    total_h = rows * (tile_h + label_h)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, total_w, total_h)
    cr = cairo.Context(surface)

    # Black background
    cr.set_source_rgb(0, 0, 0)
    cr.rectangle(0, 0, total_w, total_h)
    cr.fill()

    for idx, fname in enumerate(preset_files):
        col = idx % cols
        row = idx // cols
        x = col * tile_w
        y = row * (tile_h + label_h)

        preset_path = os.path.join(PRESETS_DIR, fname)
        model, name = load_preset_model(preset_path)

        # Label
        cr.set_source_rgb(1, 1, 1)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(14)
        cr.move_to(x + 8, y + 17)
        cr.show_text(name)

        # Render tile
        tile_surface = render_preset_tile(model, tile_w, tile_h)
        cr.set_source_surface(tile_surface, x, y + label_h)
        cr.paint()

    out_path = "/tmp/preset_comparison.png"
    surface.write_to_png(out_path)
    print(f"Written: {out_path}")
