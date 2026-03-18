"""Tests for import/export logic."""

import unittest
import os
import tarfile
import tempfile
import shutil
from icesculpt.theme_model import ThemeModel
from icesculpt.dialogs.import_export import _do_import, _do_export

class TestImportExport(unittest.TestCase):
    def setUp(self):
        self.model = ThemeModel()
        self.test_dir = tempfile.mkdtemp()
        self.theme_dir = tempfile.mkdtemp()
        
        # Create a basic theme structure
        with open(os.path.join(self.theme_dir, "default.theme"), "w") as f:
            f.write("ThemeDescription=\"Test\"\n")
        
        self.model.load_file(os.path.join(self.theme_dir, "default.theme"))

    def tearDown(self):
        shutil.rmtree(self.test_dir)
        shutil.rmtree(self.theme_dir)

    def test_do_export(self):
        archive_path = os.path.join(self.test_dir, "test.tar.gz")
        # Pass None as parent since _show_error would fail anyway in headless
        # but _do_export shouldn't call it if everything is right
        success = _do_export(None, self.model, archive_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(archive_path))
        
        # Verify content
        with tarfile.open(archive_path, "r:gz") as tar:
            names = tar.getnames()
            self.assertTrue(any("default.theme" in n for n in names))

    def test_do_import(self):
        # 1. Create an archive
        archive_path = os.path.join(self.test_dir, "import.tar.gz")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(self.theme_dir, arcname="mytheme")
            
        # 2. Import it
        success = _do_import(None, self.model, archive_path)
        self.assertTrue(success)
        self.assertEqual(self.model.get("ThemeDescription"), "Test")
        
    def test_do_import_invalid(self):
        # No default.theme
        empty_dir = tempfile.mkdtemp()
        archive_path = os.path.join(self.test_dir, "invalid.tar.gz")
        with tarfile.open(archive_path, "w:gz") as tar:
            tar.add(empty_dir, arcname="nothing")
        
        # This should fail and return False
        # We wrap in try/except because it might try to show a Gtk error dialog
        try:
            success = _do_import(None, self.model, archive_path)
            self.assertFalse(success)
        except Exception:
            pass
        finally:
            shutil.rmtree(empty_dir)

if __name__ == "__main__":
    unittest.main()
