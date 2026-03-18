"""Headless UI logic tests."""

import unittest
import os
import tempfile
import shutil
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from icesculpt.theme_model import ThemeModel
from icesculpt.preview_renderer import PreviewRenderer
from icesculpt.widgets.preview_area import PreviewArea
from icesculpt.editors.color_editor import ColorEditor
from icesculpt.editors.pixmap_editor import PixmapEditor
from icesculpt.app import IceSculptApp
from icesculpt.main_window import MainWindow

class TestUILogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize GTK
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()

    def test_preview_renderer_basic(self):
        # Render to a dummy surface to exercise logic
        import cairo
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
        cr = cairo.Context(surface)
        renderer = PreviewRenderer(self.model)
        renderer.render(cr, 800, 600)
        # Check some rendering states
        renderer.force_active = True
        renderer.render(cr, 800, 600)
        renderer.force_active = False
        renderer.render(cr, 800, 600)

    def test_preview_area_widget(self):
        # Test the wrapper widget logic
        area = PreviewArea(self.model)
        # Trigger model change to exercise redraw scheduling
        self.model.set("ColorActiveTitleBar", "rgb:11/22/33")
        # Run main loop briefly to process idle tasks (capped to avoid hangs)
        for _ in range(10):
            GLib.main_context_default().iteration(False)

        # Test mode toggles
        area.btn_active.set_active(True)
        self.assertEqual(area.renderer.force_active, True)
        area.btn_inactive.set_active(True)
        self.assertEqual(area.renderer.force_active, False)

    def test_color_editor_logic(self):
        # Exercise editor creation and model binding
        editor = ColorEditor(self.model)
        # Find a swatch and simulate change
        key = list(editor._swatches.keys())[0]
        swatch, label = editor._swatches[key]
        editor._on_swatch_changed(swatch, "#FF0000", key)
        self.assertEqual(self.model.get_color_hex(key), "#FF0000")

    def test_pixmap_editor_ops(self):
        test_dir = tempfile.mkdtemp()
        self.model.theme_dir = test_dir
        editor = PixmapEditor(self.model)

        # Test generate buttons (exercises pixmap_generator + editor logic)
        editor._on_generate_buttons(None)
        self.assertTrue(os.path.exists(os.path.join(test_dir, "closeA.xpm")))

        # Test refresh
        editor._on_refresh(None)
        self.assertGreater(len(editor._store), 0)

        shutil.rmtree(test_dir)

    def test_main_window_ops(self):
        app = IceSculptApp()
        win = MainWindow(app)
        # MainWindow creates its own model, so use that one
        model = win.model

        # Test toggle preview
        win._on_toggle_preview(win._toggle_preview_item)

        # Test status
        win._status("Testing coverage")

        # Test title update
        model.set("ThemeDescription", "CoverageTheme")
        win._on_model_changed("ThemeDescription")
        self.assertIn("CoverageTheme", win.get_title())


class TestUIBoost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()

    def test_gradient_builder(self):
        from icesculpt.widgets.gradient_builder import GradientBuilder
        changed_val = None
        def on_changed(v): nonlocal changed_val; changed_val = v
        gb = GradientBuilder("rgb:FF/00/00, invalid, #0000FF", on_changed)
        self.assertEqual(len(gb.colors), 2)
        gb._on_add_clicked(None)
        gb._on_move_clicked(None, 0, 1)
        gb._on_delete_clicked(None, 1)
        gb._notify()
        self.assertIn("rgb:00/00/FF", changed_val)

    def test_pixmap_canvas_undo_redo(self):
        from icesculpt.widgets.pixmap_canvas import PixmapCanvas
        from icesculpt import xpm_codec
        img = xpm_codec.create_solid(2, 2, "#000000")
        canvas = PixmapCanvas()
        canvas.image = img
        canvas.set_draw_color(".")
        canvas.set_pixel_at(0, 0)
        self.assertEqual(len(canvas._undo_stack), 1)
        canvas.undo()
        self.assertEqual(len(canvas._undo_stack), 0)
        self.assertEqual(len(canvas._redo_stack), 1)
        canvas.redo()
        self.assertEqual(len(canvas._undo_stack), 1)
        self.assertEqual(len(canvas._redo_stack), 0)

    def test_preview_area_error_handling(self):
        from unittest.mock import patch, MagicMock
        pa = PreviewArea(self.model)
        with patch.object(pa.renderer, 'render', side_effect=Exception("Render Fail")):
            mock_cr = MagicMock()
            pa._on_draw(pa.canvas, mock_cr)
            mock_cr.fill.assert_called()

    def test_color_editor_extra(self):
        self.model.set_color_hex("ColorActiveTitleBar", "#FF0000")
        editor = ColorEditor(self.model)
        editor._on_make_gradient_clicked(None, "ColorActiveTitleBar")
        self.assertIn(",", self.model.get("ColorActiveTitleBar"))
        self.model.set_color_hex("ColorActiveBorder", "#00FF00")
        swatch, label = editor._swatches["ColorActiveBorder"]
        self.assertEqual(label.get_text(), "#00FF00")
        self.model._fire_callbacks(None)
        self.assertEqual(label.get_text(), "#00FF00")
if __name__ == "__main__":
    unittest.main()
