"""Tests for PixmapCanvas business logic (headless)."""

import unittest
from icesculpt.xpm_codec import XpmImage
from icesculpt.widgets.pixmap_canvas import PixmapCanvas
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class TestPixmapCanvasLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def test_canvas_state(self):
        img = XpmImage(width=10, height=10)
        canvas = PixmapCanvas(zoom=10)
        canvas.image = img
        
        self.assertEqual(canvas.zoom, 10)
        
        # Test color selection
        img.colors['A'] = "#FF0000"
        canvas.set_draw_color('A')
        # ... (exercises logic)

    def test_canvas_undo_redo(self):
        img = XpmImage(width=5, height=5)
        canvas = PixmapCanvas(zoom=10)
        canvas.image = img
        canvas.set_draw_color('X')
        
        # 1. Initial change
        canvas.set_pixel_at(0, 0)
        self.assertEqual(img.get_pixel(0, 0), 'X')
        
        # 2. Undo
        self.assertTrue(canvas.undo())
        self.assertEqual(img.get_pixel(0, 0), ' ') # Default
        
        # 3. Redo
        self.assertTrue(canvas.redo())
        self.assertEqual(img.get_pixel(0, 0), 'X')

    def test_canvas_draw_logic(self):
        # Even without drawing, we can exercise the logic that handles clicks
        img = XpmImage(width=10, height=10)
        canvas = PixmapCanvas(zoom=10)
        canvas.image = img
        canvas.set_draw_color('.')
        
        # Simulate a pixel change via public API
        canvas.set_pixel_at(5, 5)
        self.assertEqual(img.get_pixel(5, 5), '.')

if __name__ == "__main__":
    unittest.main()
