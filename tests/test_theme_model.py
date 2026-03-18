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

    def test_model_bool_int(self):
        self.model.set("TestBool", "1")
        self.assertTrue(self.model.get_bool("TestBool"))
        self.model.set("TestBool", "true")
        self.assertTrue(self.model.get_bool("TestBool"))
        self.model.set("TestBool", "yes")
        self.assertTrue(self.model.get_bool("TestBool"))
        self.model.set("TestBool", "0")
        self.assertFalse(self.model.get_bool("TestBool"))
        self.assertFalse(self.model.get_bool("NonExistent", default=False))
        
        self.model.set("TestInt", "abc")
        self.assertEqual(self.model.get_int("TestInt", 42), 42)
        self.assertEqual(self.model.get_int("Empty", 7), 7)

    def test_model_colors_extra(self):
        self.model.set_color("Color1", 1.0, 0.0, 0.0)
        self.assertEqual(self.model.get("Color1"), "rgb:FF/00/00")
        
        self.model.set_color_hex("Color2", "#00FF00")
        self.assertEqual(self.model.get("Color2"), "rgb:00/FF/00")
        
        self.assertEqual(self.model.get_color_hex("Color2"), "#00FF00")
        self.assertEqual(self.model.get_color_hex("NonExistent", "#123456"), "#123456")
        
        # Test malformed color fallback
        self.model.set("BadColor", "not-a-color")
        self.assertEqual(self.model.get_color_hex("BadColor", "#000000"), "#000000")
        r, g, b, a = self.model.get_color_rgba("BadColor", "#FFFFFF")
        self.assertEqual((r, g, b), (1.0, 1.0, 1.0))

    def test_model_categories_and_registry(self):
        cats = self.model.get_categories()
        self.assertIn("Menu Colors", cats)
        
        keys = self.model.get_keys_by_category("Menu Colors")
        self.assertTrue(len(keys) > 0)
        
        reg = self.model.key_registry
        self.assertIn("ColorActiveTitleBar", reg)
        self.assertEqual(self.model.get("ColorActiveTitleBar"), reg["ColorActiveTitleBar"].default)

    def test_model_temp_dirs(self):
        self.assertFalse(self.model.is_temp)
        d = tempfile.mkdtemp(dir=self.test_dir)
        self.model.register_temp_dir(d)
        self.model.theme_dir = None
        self.assertFalse(self.model.is_temp)
        self.model.theme_dir = "/tmp/some/other/path"
        self.assertFalse(self.model.is_temp)
        self.model.theme_dir = os.path.join(d, "subdir")
        self.assertTrue(self.model.is_temp)
        self.model.new_theme()
        self.assertFalse(os.path.exists(d))

    def test_model_snapshot_and_disconnect(self):
        self.model.set("K1", "V1")
        self.model.set("K2", "V2")
        snapshot = {"K1": "V1_new", "K3": "V3"}
        self.model.restore_snapshot(snapshot)
        self.assertEqual(self.model.get("K1"), "V1_new")
        self.assertEqual(self.model.get("K3"), "V3")
        self.assertEqual(self.model.get("K2"), "")

        called = False
        def cb(k):
            nonlocal called
            called = True
        cid = self.model.connect(cb)
        self.model.disconnect(cid)
        self.model.set("X", "Y")
        self.assertFalse(called)
        
        called_count = 0
        def cb2(k):
            nonlocal called_count
            called_count += 1
        self.model.connect(cb2, key_filter=["F1", "F2"])
        self.model.set("F1", "V")
        self.model.set("F2", "V2")
        self.model.set("F3", "V3")
        self.assertEqual(called_count, 2)

    def test_model_save_and_copy(self):
        with self.assertRaises(ValueError):
            self.model.save()
        src_dir = os.path.join(self.test_dir, "src")
        os.makedirs(src_dir)
        with open(os.path.join(src_dir, "asset.xpm"), "w") as f:
            f.write("/* XPM */")
        theme_file = os.path.join(src_dir, "default.theme")
        with open(theme_file, "w") as f:
            f.write("ThemeDescription = \"Test\"")
        self.model.load_file(theme_file)
        dst_dir = os.path.join(self.test_dir, "dst")
        dst_theme = os.path.join(dst_dir, "default.theme")
        self.model.save(dst_theme)
        self.assertTrue(os.path.exists(os.path.join(dst_dir, "asset.xpm")))

    def test_model_load_from_lines(self):
        from icesculpt.theme_parser import ThemeLine
        line = ThemeLine("Key=Val", key="Key", value="Val")
        self.model.load_from_lines([line], "/some/path")
        self.assertEqual(self.model.get("Key"), "Val")
        self.assertEqual(self.model.filepath, "/some/path")

    def test_model_save_dir_exists(self):
        src_dir = os.path.join(self.test_dir, "src2")
        os.makedirs(src_dir)
        with open(os.path.join(src_dir, "asset.xpm"), "w") as f:
            f.write("/* XPM */")
        theme_file = os.path.join(src_dir, "default.theme")
        with open(theme_file, "w") as f:
            f.write("ThemeDescription = \"Test\"")
        self.model.load_file(theme_file)
        # Target dir already exists
        dst_dir = os.path.join(self.test_dir, "dst2")
        os.makedirs(dst_dir)
        # Put another asset there to trigger item copy logic
        with open(os.path.join(dst_dir, "other.xpm"), "w") as f:
            f.write("/* XPM */")
        self.model.save(os.path.join(dst_dir, "default.theme"))
        self.assertTrue(os.path.exists(os.path.join(dst_dir, "asset.xpm")))

    def test_model_callback_filter_match(self):
        called = False
        def cb(k):
            nonlocal called
            called = True
        self.model.connect(cb, key_filter="MatchKey")
        self.model.set("MatchKey", "Val")
        self.assertTrue(called)

    def test_load_theme_keys_default(self):
        from icesculpt.theme_model import load_theme_keys
        keys = load_theme_keys() # Test default path
        self.assertIn("ThemeDescription", keys)

    def test_model_callback_filter_tuple(self):
        called_count = 0
        def cb(k):
            nonlocal called_count
            called_count += 1
        self.model.connect(cb, key_filter=("T1", "T2"))
        self.model.set("T1", "V")
        self.model.set("T2", "V2")
        self.model.set("T3", "V3")
        self.assertEqual(called_count, 2)

if __name__ == "__main__":
    unittest.main()
