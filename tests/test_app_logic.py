"""Tests for App and NewThemeDialog logic (headless)."""

import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

from icesculpt.app import IceSculptApp
from icesculpt.dialogs.new_theme import NewThemeDialog

class TestAppDialogsLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def test_app_init(self):
        app = IceSculptApp()
        self.assertEqual(app.get_application_id(), "org.icesculpt.IceSculpt")
        # Test do_activate (basic sanity)
        app.do_activate()
        self.assertIsNotNone(app._window)

    def test_new_theme_dialog_logic(self):
        parent = Gtk.Window()
        dialog = NewThemeDialog(parent)
        
        # Simulate user input
        dialog._name_entry.set_text("DialogTest")
        dialog._author_entry.set_text("Tester")
        
        self.assertEqual(dialog.theme_name, "DialogTest")
        self.assertEqual(dialog.author, "Tester")
        dialog.destroy()

if __name__ == "__main__":
    unittest.main()
