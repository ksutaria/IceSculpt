"""Tests for the ThemeModel."""

import unittest
import os
import tempfile
import shutil
from icesculpt.theme_model import ThemeModel

class TestThemeModel(unittest.TestCase):
    def setUp(self):
        self.model = ThemeModel()
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_new_theme(self):
        self.model.new_theme("My Theme", "Author Name")
        self.assertEqual(self.model.get("ThemeDescription"), "My Theme")
        self.assertEqual(self.model.get("ThemeAuthor"), "Author Name")
        self.assertTrue(self.model.dirty)

    def test_set_get(self):
        self.model.new_theme()
        self.model.set("BorderSizeX", "10")
        self.assertEqual(self.model.get("BorderSizeX"), "10")
        self.assertEqual(self.model.get_int("BorderSizeX"), 10)
        self.assertTrue(self.model.dirty)

    def test_save_load(self):
        theme_path = os.path.join(self.test_dir, "default.theme")
        self.model.new_theme("SaveTest", "Tester")
        self.model.set("ColorActiveTitleBar", "rgb:11/22/33")
        self.model.save(theme_path)
        
        new_model = ThemeModel()
        new_model.load_file(theme_path)
        self.assertEqual(new_model.get("ThemeDescription"), "SaveTest")
        self.assertEqual(new_model.get("ColorActiveTitleBar"), "rgb:11/22/33")
        self.assertFalse(new_model.dirty)

    def test_batch_update(self):
        self.model.new_theme()
        updates = {
            "ColorActiveTitleBar": "rgb:00/00/00",
            "ColorNormalTitleBar": "rgb:FF/FF/FF"
        }
        self.model.batch_update(updates)
        self.assertEqual(self.model.get("ColorActiveTitleBar"), "rgb:00/00/00")
        self.assertEqual(self.model.get("ColorNormalTitleBar"), "rgb:FF/FF/FF")

    def test_undo_redo_integration(self):
        # This tests the logic in MainWindow via the model's connect mechanism
        # but here we just test model basic connect
        changes = []
        def on_change(key):
            changes.append(key)
        
        self.model.connect(on_change)
        self.model.set("TestKey", "Val")
        self.assertIn("TestKey", changes)

    def test_get_color_rgba(self):
        self.model.set("MyColor", "rgb:FF/00/00")
        r, g, b, a = self.model.get_color_rgba("MyColor")
        self.assertAlmostEqual(r, 1.0)
        self.assertAlmostEqual(g, 0.0)
        self.assertAlmostEqual(b, 0.0)

if __name__ == "__main__":
    unittest.main()
