"""Deep logic tests for pixmap editing and generation (headless)."""

import unittest
import os
import tempfile
import shutil
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from icesculpt.theme_model import ThemeModel
from icesculpt.editors.pixmap_editor import PixmapEditor
from icesculpt.widgets.pixmap_canvas import PixmapCanvas
from icesculpt.xpm_codec import XpmImage

class TestPixmapLogicDeep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()
        self.test_dir = tempfile.mkdtemp()
        self.model.theme_dir = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_recolor_all_dialog_logic(self):
        # We can't easily test the actual dialog run() in headless,
        # but we can test the recolor_all_pixmaps function it calls.
        from icesculpt.pixmap_generator import recolor_all_pixmaps
        
        # Create a dummy XPM
        xpm_path = os.path.join(self.test_dir, "btn.xpm")
        img = XpmImage(10, 10)
        img.colors['.'] = "#FF0000"
        img.pixels = ["." * 10] * 10
        from icesculpt.xpm_codec import write_xpm_file
        write_xpm_file(xpm_path, img)
        
        # Call the logic
        recolored = recolor_all_pixmaps(self.test_dir, hue_shift=0.5)
        self.assertIn("btn.xpm", recolored)

    def test_pixmap_editor_generation_logic(self):
        editor = PixmapEditor(self.model)
        
        # Test generate buttons
        editor._on_generate_buttons(None)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "closeA.xpm")))
        
        # Test generate frames
        editor._on_generate_frames(None)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "frameATL.xpm")))

    def test_canvas_interaction_logic(self):
        img = XpmImage(10, 10)
        img.colors['X'] = "#000000"
        canvas = PixmapCanvas(image=img, zoom=10)
        canvas.set_draw_color('X')
        
        # Test coordinate mapping
        pos = canvas._pixel_at(55, 55) # zoom is 10, so should be (5, 5)
        self.assertEqual(pos, (5, 5))
        
        # Test out of bounds
        self.assertIsNone(canvas._pixel_at(150, 150))

if __name__ == "__main__":
    unittest.main()
