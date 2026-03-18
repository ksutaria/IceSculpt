"""Deep tests for import/export logic and safe tar members."""

import unittest
import tempfile
import shutil
from unittest.mock import MagicMock, patch

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from icesculpt.theme_model import ThemeModel
from icesculpt.dialogs.import_export import (
    _safe_tar_members, _do_import, _do_export,
    import_theme_dialog, export_theme_dialog
)

class TestImportExportDeep(unittest.TestCase):
    def setUp(self):
        self.model = ThemeModel()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_safe_tar_members(self):
        # Create a mock tar with some dangerous and safe members
        tar = MagicMock()
        
        m_safe = MagicMock()
        m_safe.name = "safe.txt"
        m_safe.issym.return_value = False
        m_safe.islnk.return_value = False
        
        m_sym = MagicMock()
        m_sym.name = "danger_sym"
        m_sym.issym.return_value = True
        m_sym.islnk.return_value = False
        
        m_traversal = MagicMock()
        m_traversal.name = "../outside.txt"
        m_traversal.issym.return_value = False
        m_traversal.islnk.return_value = False
        
        tar.getmembers.return_value = [m_safe, m_sym, m_traversal]
        
        safe_members = list(_safe_tar_members(tar, self.test_dir))
        self.assertEqual(len(safe_members), 1)
        self.assertEqual(safe_members[0].name, "safe.txt")

    @patch('icesculpt.dialogs.import_export.Gtk.FileChooserDialog')
    def test_import_theme_dialog_cancel(self, mock_dialog):
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.CANCEL
        result = import_theme_dialog(None, self.model)
        self.assertFalse(result)

    @patch('icesculpt.dialogs.import_export.Gtk.FileChooserDialog')
    @patch('icesculpt.dialogs.import_export._do_import')
    def test_import_theme_dialog_ok(self, mock_do_import, mock_dialog):
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
        mock_dialog.return_value.get_filename.return_value = "dummy.tar.gz"
        mock_do_import.return_value = True
        
        result = import_theme_dialog(None, self.model)
        self.assertTrue(result)
        mock_do_import.assert_called_with(None, self.model, "dummy.tar.gz")

    @patch('icesculpt.dialogs.import_export.Gtk.FileChooserDialog')
    def test_export_theme_dialog_cancel(self, mock_dialog):
        self.model.theme_dir = self.test_dir
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.CANCEL
        result = export_theme_dialog(None, self.model)
        self.assertFalse(result)

    @patch('icesculpt.dialogs.import_export.Gtk.FileChooserDialog')
    @patch('icesculpt.dialogs.import_export._do_export')
    def test_export_theme_dialog_ok(self, mock_do_export, mock_dialog):
        self.model.theme_dir = self.test_dir
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
        mock_dialog.return_value.get_filename.return_value = "out.tar.gz"
        mock_do_export.return_value = True
        
        result = export_theme_dialog(None, self.model)
        self.assertTrue(result)
        mock_do_export.assert_called_with(None, self.model, "out.tar.gz")

    def test_do_import_exception(self):
        # Trigger an exception during import
        with patch('tarfile.open', side_effect=Exception("Tar error")):
            result = _do_import(None, self.model, "nonexistent.tar.gz")
            self.assertFalse(result)

    def test_do_export_exception(self):
        self.model.theme_dir = self.test_dir
        with patch('tarfile.open', side_effect=Exception("Write error")):
            result = _do_export(None, self.model, "out.tar.gz")
            self.assertFalse(result)

if __name__ == "__main__":
    unittest.main()
