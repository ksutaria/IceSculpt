"""Extended tests for MainWindow functionality."""

import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch, PropertyMock

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from icesculpt.app import IceSculptApp
from icesculpt.main_window import MainWindow

class TestMainWindowExtended(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.app = IceSculptApp()
        self.win = MainWindow(self.app)
        self.test_dir = tempfile.mkdtemp()
        
        # Patch MessageDialog globally for this test class to prevent hanging
        self.patcher = patch('icesculpt.main_window.Gtk.MessageDialog')
        self.mock_msg_dlg = self.patcher.start()
        self.mock_msg_dlg.return_value.run.return_value = Gtk.ResponseType.OK

    def tearDown(self):
        self.patcher.stop()
        self.win.destroy()
        shutil.rmtree(self.test_dir)

    @patch('icesculpt.main_window.NewThemeDialog')
    def test_on_new(self, mock_dialog):
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
        mock_dialog.return_value.theme_name = "NewT"
        mock_dialog.return_value.author = "Auth"
        mock_dialog.return_value.look_style = "pixmap"
        
        self.win._on_new(None)
        self.assertEqual(self.win.model.get("ThemeDescription"), "NewT")
        self.assertEqual(self.win.model.get("Look"), "pixmap")

    @patch('icesculpt.main_window.Gtk.FileChooserDialog')
    def test_on_open(self, mock_dialog):
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
        mock_dialog.return_value.get_filename.return_value = os.path.join(self.test_dir, "default.theme")
        with open(mock_dialog.return_value.get_filename(), "w") as f:
            f.write("ThemeDescription=Loaded")
            
        self.win._on_open(None)
        self.assertEqual(self.win.model.get("ThemeDescription"), "Loaded")

    def test_on_save_as(self):
        with patch('icesculpt.main_window.Gtk.FileChooserDialog') as mock_dialog:
            mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
            path = os.path.join(self.test_dir, "saved.theme")
            mock_dialog.return_value.get_filename.return_value = path
            
            self.win._on_save_as(None)
            self.assertTrue(os.path.exists(path))

    @patch('shutil.copytree')
    @patch('subprocess.run')
    def test_on_apply(self, mock_run, mock_copy):
        self.win.model.theme_dir = self.test_dir
        self.win._on_apply(None)
        mock_copy.assert_called()

    def test_accessibility_transforms(self):
        self.win.model.set("TitleFontNameXft", "Sans/10")
        self.win._on_apply_large_fonts(None)
        self.assertIn("15", self.win.model.get("TitleFontNameXft"))
        
        self.win._on_apply_high_contrast(None)
        self.assertEqual(self.win.model.get("ColorActiveTitleBar"), "rgb:00/00/00")

    def test_view_operations(self):
        self.win._on_split_equal(None)
        # Just check it doesn't crash, position is internal
        self.win._on_focus_editor(None)
        self.win._on_focus_preview(None)

    @patch('icesculpt.main_window.Gtk.Dialog')
    def test_on_check_health(self, mock_dialog):
        # With messages
        self.win.model.set("ColorActiveTitleBar", "#000000")
        self.win.model.set("ColorActiveTitleBarText", "#050505")
        
        # Ensure run() returns to avoid hanging
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.CLOSE
        
        self.win._on_check_health(None)
        mock_dialog.assert_called()

    def test_undo_redo_cycle(self):
        self.win.model.set("ThemeDescription", "Step1")
        self.win.model.set("ThemeDescription", "Step2")
        
        self.win._on_undo(None)
        self.assertEqual(self.win.model.get("ThemeDescription"), "Step1")
        
        self.win._on_redo(None)
        self.assertEqual(self.win.model.get("ThemeDescription"), "Step2")

    def test_delete_event(self):
        self.win.model.dirty = False
        res = self.win._on_delete_event(None, None)
        self.assertFalse(res) # Should allow close
        
        self.win.model.dirty = True
        with patch('icesculpt.main_window.Gtk.MessageDialog') as mock_md:
            mock_md.return_value.run.return_value = Gtk.ResponseType.CANCEL
            res = self.win._on_delete_event(None, None)
            self.assertTrue(res) # Should block close

    def test_toggle_preview_hide(self):
        mock_toggle = MagicMock()
        mock_toggle.get_active.return_value = False
        self.win._on_toggle_preview(mock_toggle)
        self.assertFalse(self.win._paned.get_child2().get_visible())

    def test_on_apply_preset_error(self):
        with patch('icesculpt.main_window.json.load', side_effect=Exception("JSON error")):
            self.win._on_apply_preset(None, "dummy.json")
            # Should show error, but we just check it doesn't crash

    def test_on_save_direct(self):
        # Already has filepath, not temp
        path = os.path.join(self.test_dir, "direct.theme")
        self.win.model.filepath = path
        with patch('icesculpt.theme_model.ThemeModel.is_temp', new_callable=PropertyMock) as mock_is_temp:
            mock_is_temp.return_value = False
            with patch.object(self.win.model, 'save') as mock_save:
                self.win._on_save(None)
                mock_save.assert_called()

    def test_on_import_export_dialogs(self):
        with patch('icesculpt.main_window.import_theme_dialog', return_value=True):
            self.win._on_import(None)
        with patch('icesculpt.main_window.export_theme_dialog', return_value=True):
            self.win._on_export(None)

    def test_on_apply_no_dir(self):
        self.win.model.theme_dir = None
        with patch.object(self.win, '_show_error') as mock_err:
            self.win._on_apply(None)
            mock_err.assert_called_with("Save the theme first.")

    def test_try_quit_logic(self):
        # Case 1: Not dirty
        self.win.model.dirty = False
        with patch.object(self.app, 'quit') as mock_quit:
            self.win._try_quit()
            mock_quit.assert_called()
            
        # Case 2: Dirty, Save
        self.win.model.dirty = True
        with patch('icesculpt.main_window.Gtk.MessageDialog') as mock_md:
            mock_md.return_value.run.return_value = Gtk.ResponseType.YES
            with patch.object(self.win, '_on_save') as mock_save:
                res = self.win._check_unsaved()
                self.assertTrue(res)
                mock_save.assert_called()

    def test_main_window_shortcuts(self):
        # Alt+1
        event = MagicMock()
        event.state = Gdk.ModifierType.MOD1_MASK
        event.keyval = Gdk.KEY_1
        res = self.win._on_key_press(None, event)
        self.assertTrue(res)
        self.assertEqual(self.win._notebook.get_current_page(), 0)
        
        # Alt+9
        event.keyval = Gdk.KEY_9
        self.win._on_key_press(None, event)
        self.assertEqual(self.win._notebook.get_current_page(), 8)

if __name__ == "__main__":
    unittest.main()
