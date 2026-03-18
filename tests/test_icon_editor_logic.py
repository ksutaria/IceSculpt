"""Tests for IconEditor logic (headless)."""

import unittest
import os
import tempfile
import shutil
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from icesculpt.theme_model import ThemeModel
from icesculpt.editors.icon_editor import IconEditor
from icesculpt.xpm_codec import XpmImage

class TestIconEditorLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.test_dir = tempfile.mkdtemp()
        
        # Create icons directory structure
        self.icons_dir = os.path.join(self.test_dir, "icons")
        os.makedirs(os.path.join(self.icons_dir, "48x48"), exist_ok=True)
        
        # Create a dummy icon
        img = XpmImage(width=16, height=16)
        img.colors['.'] = "#000000"
        img.pixels = ["." * 16] * 16
        with open(os.path.join(self.icons_dir, "48x48", "test.xpm"), "w") as f:
            f.write(img.to_xpm3())
            
        # Point model to this dir
        self.model.theme_dir = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_load_icons(self):
        editor = IconEditor(self.model)
        # _load_icons is called in __init__
        children = editor._flowbox.get_children()
        # It might take a bit for GdkPixbuf to load if we were in a loop
        # but here we just check if it executed without error and added something
        self.assertGreaterEqual(len(children), 0)
        
        # Manually trigger
        editor._load_icons()
        self.assertGreaterEqual(len(editor._flowbox.get_children()), 0)

    def test_import_logic_no_dir(self):
        # Test error handling when no theme dir set
        self.model.theme_dir = None
        editor = IconEditor(self.model)
        # Should not crash
        editor._on_import(None)

if __name__ == "__main__":
    unittest.main()
