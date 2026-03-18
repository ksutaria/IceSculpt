"""More detailed tests for editors."""

import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from icesculpt.theme_model import ThemeModel
from icesculpt.editors.font_editor import FontEditor
from icesculpt.editors.desktop_editor import DesktopEditor

class TestMoreEditors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()

    def test_font_editor_logic(self):
        editor = FontEditor(self.model)
        # Test font change
        key = "FontActiveTitleBar"
        # Simulate signal: _on_font_set(button, key)
        # We need a Gtk.FontButton instance
        btn = Gtk.FontButton()
        btn.set_font("Sans Bold 12")
        editor._on_font_set(btn, key)
        # pango_to_xft converts "Sans Bold 12" to "Sans:size=12:bold" (best effort)
        self.assertIn("Sans", self.model.get(key))
        self.assertIn("size=12", self.model.get(key))

    def test_desktop_editor_logic(self):
        editor = DesktopEditor(self.model)
        # Test wallpaper change
        editor._wp_entry.set_text("new_wallpaper.png")
        # connect is called in __init__, so changing text triggers callback
        self.assertEqual(self.model.get("DesktopBackgroundImage"), "new_wallpaper.png")

if __name__ == "__main__":
    unittest.main()
