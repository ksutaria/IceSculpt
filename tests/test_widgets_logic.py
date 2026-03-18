"""Tests for widget business logic (headless)."""

import unittest
from icesculpt.theme_model import ThemeModel
from icesculpt.widgets.param_row import ParamRow
from icesculpt.widgets.gradient_builder import GradientBuilder
from icesculpt.widgets.color_swatch import ColorSwatch
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class TestWidgetsLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()

    def test_gradient_builder_logic(self):
        def on_changed(val):
            self.last_val = val
        
        self.last_val = None
        builder = GradientBuilder("rgb:00/00/00,rgb:FF/FF/FF", on_changed)
        self.assertEqual(len(builder.colors), 2)
        
        # Add color
        builder._on_add_clicked(None)
        self.assertEqual(len(builder.colors), 3)
        self.assertIn("rgb:80/80/80", self.last_val)
        
        # Move color
        first_color = builder.colors[0]
        builder._on_move_clicked(None, 0, 1)
        self.assertEqual(builder.colors[1], first_color)
        
        # Delete color
        builder._on_delete_clicked(None, 0)
        self.assertEqual(len(builder.colors), 2)

    def test_color_swatch_logic(self):
        swatch = ColorSwatch("#FF0000")
        self.assertEqual(swatch.hex_color, "#FF0000")
        
        swatch.hex_color = "#00FF00"
        self.assertEqual(swatch.hex_color, "#00FF00")

    def test_color_swatch_gradient_draw(self):
        # This exercises the cairo drawing logic for gradients
        swatch = ColorSwatch("rgb:FF/00/00,rgb:00/00/FF")
        import cairo
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 24, 24)
        cr = cairo.Context(surface)
        # Manually trigger the draw handler
        swatch._on_draw(swatch, cr)
        # If no AttributeError was raised, the fix is verified

if __name__ == "__main__":
    unittest.main()
