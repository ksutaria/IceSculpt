"""Deep tests for ColorSwatch and PixmapCanvas widgets."""

import unittest
from unittest.mock import MagicMock, patch

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from icesculpt.widgets.color_swatch import ColorSwatch
from icesculpt.widgets.pixmap_canvas import PixmapCanvas
from icesculpt.xpm_codec import XpmImage

class TestWidgetsDeep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def test_color_swatch_basics(self):
        swatch = ColorSwatch("#FF0000", size=32)
        self.assertEqual(swatch.hex_color, "#FF0000")
        
        swatch.hex_color = "#00FF00"
        self.assertEqual(swatch.hex_color, "#00FF00")
        
        # Test draw (exercises _on_draw)
        surface = MagicMock()
        cr = MagicMock()
        swatch._on_draw(swatch, cr)
        cr.set_source_rgb.assert_called()

    def test_color_swatch_gradient_draw(self):
        swatch = ColorSwatch("#FF0000,#0000FF")
        cr = MagicMock()
        swatch._on_draw(swatch, cr)
        # Should have created a LinearGradient
        cr.set_source.assert_called()

    @patch('icesculpt.widgets.color_swatch.Gtk.ColorChooserDialog')
    def test_color_swatch_click(self, mock_dialog):
        swatch = ColorSwatch("#808080")
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
        mock_dialog.return_value.get_rgba.return_value = Gdk.RGBA(red=1.0, green=0, blue=0, alpha=1.0)
        
        # Simulate click
        event = MagicMock()
        event.button = 1
        swatch._on_click(swatch, event)
        
        self.assertEqual(swatch.hex_color, "#FF0000")

    @patch('icesculpt.widgets.color_swatch.Gtk.Dialog')
    def test_color_swatch_gradient_click(self, mock_dialog):
        swatch = ColorSwatch("#FF0000,#0000FF")
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.CLOSE
        
        event = MagicMock()
        event.button = 1
        swatch._on_click(swatch, event)
        mock_dialog.assert_called()

    def test_color_swatch_key_press(self):
        swatch = ColorSwatch("#808080")
        with patch.object(swatch, '_open_color_dialog') as mock_open:
            event = MagicMock()
            event.keyval = Gdk.KEY_Return
            swatch._on_key_press(swatch, event)
            mock_open.assert_called()

    def test_pixmap_canvas_properties(self):
        img = XpmImage(8, 8)
        canvas = PixmapCanvas(img, zoom=10)
        self.assertEqual(canvas.image, img)
        self.assertEqual(canvas.zoom, 10)
        
        new_img = XpmImage(4, 4)
        canvas.image = new_img
        self.assertEqual(canvas.image, new_img)
        
        canvas.zoom = 20
        self.assertEqual(canvas.zoom, 20)

    def test_pixmap_canvas_drawing_logic(self):
        img = XpmImage(2, 2)
        img.colors["."] = None # Transparent
        img.colors["X"] = "#000000"
        img.pixels = [".X", "X."]
        
        canvas = PixmapCanvas(img, zoom=10)
        cr = MagicMock()
        canvas._do_draw(cr)
        # Should have called set_source_rgb for checkerboard and black pixel
        self.assertGreater(cr.set_source_rgb.call_count, 0)

    def test_pixmap_canvas_interaction(self):
        img = XpmImage(4, 4)
        canvas = PixmapCanvas(img, zoom=10)
        canvas.set_draw_color("X")
        
        # Press
        event = MagicMock()
        event.button = 1
        event.x = 5
        event.y = 5
        canvas._on_button_press(canvas, event)
        self.assertTrue(canvas._drawing)
        self.assertEqual(img.get_pixel(0, 0), "X")
        
        # Motion
        event.x = 15
        event.y = 5
        canvas._on_motion(canvas, event)
        self.assertEqual(img.get_pixel(1, 0), "X")
        
        # Release
        canvas._on_button_release(canvas, event)
        self.assertFalse(canvas._drawing)

    def test_pixmap_canvas_set_pixel(self):
        canvas = PixmapCanvas()
        canvas.set_draw_color("X")
        canvas.set_pixel_at(0, 0)
        self.assertEqual(canvas.image.get_pixel(0, 0), "X")
        self.assertGreater(len(canvas._undo_stack), 0)
        
        # Test undo/redo limit
        canvas._max_undo = 2
        canvas.set_pixel_at(1, 1)
        canvas.set_pixel_at(2, 2)
        canvas.set_pixel_at(3, 3)
        self.assertEqual(len(canvas._undo_stack), 2)

    def test_pixmap_canvas_undo_redo_methods(self):
        canvas = PixmapCanvas()
        canvas.set_draw_color("X")
        canvas.set_pixel_at(0, 0) # pixels[0] was ' ', now 'X'
        
        # Undo
        res = canvas.undo()
        self.assertTrue(res)
        self.assertEqual(canvas.image.get_pixel(0, 0), " ")
        
        # Redo
        res = canvas.redo()
        self.assertTrue(res)
        self.assertEqual(canvas.image.get_pixel(0, 0), "X")
        
        # Redo when empty
        canvas._redo_stack.clear()
        self.assertFalse(canvas.redo())
        
        # Undo when empty
        canvas._undo_stack.clear()
        self.assertFalse(canvas.undo())

if __name__ == "__main__":
    unittest.main()
