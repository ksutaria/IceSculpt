"""Headless UI logic tests."""

import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from icesculpt.theme_model import ThemeModel
from icesculpt.preview_renderer import PreviewRenderer
from icesculpt.widgets.preview_area import PreviewArea
from icesculpt.editors.color_editor import ColorEditor

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
        # Run main loop briefly to process idle tasks
        while GLib.main_context_default().iteration(False):
            pass
        
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

if __name__ == "__main__":
    unittest.main()
