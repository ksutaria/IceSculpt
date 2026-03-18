"""Tests for App and NewThemeDialog logic (headless)."""

import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

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


class TestAppBoost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def test_app_exception_hook(self):
        from icesculpt.app import _install_global_exception_hook
        import sys
        _install_global_exception_hook()
        sys.excepthook = sys.__excepthook__

    def test_app_startup_open(self):
        from unittest.mock import patch, MagicMock
        import os
        import tempfile
        import shutil
        app = IceSculptApp()
        with patch('gi.repository.Gtk.Application.do_startup'), \
             patch('gi.repository.Gdk.Screen.get_default') as mock_screen:
            mock_screen.return_value = None 
            app.do_startup()
            
        test_dir = tempfile.mkdtemp()
        try:
            mock_file = MagicMock()
            mock_file.get_path.return_value = os.path.join(test_dir, "test.theme")
            with open(mock_file.get_path(), "w") as f: f.write("ThemeDescription = \"OpenTest\"")
            
            app.do_activate()
            app.do_open([mock_file], 1, "")
            self.assertEqual(app._window.model.get("ThemeDescription"), "OpenTest")
        finally:
            shutil.rmtree(test_dir)

    def test_show_error_dialog(self):
        from icesculpt.app import _show_error_dialog
        from unittest.mock import patch
        with patch('gi.repository.Gtk.MessageDialog') as mock_dialog:
            _show_error_dialog("Summary", "Detail")
            mock_dialog.assert_called()
            mock_dialog.return_value.run.assert_called()
            mock_dialog.return_value.destroy.assert_called()

if __name__ == "__main__":
    unittest.main()
