"""Tests for pixmap recoloring and generation logic."""

import unittest
from icesculpt.xpm_codec import XpmImage
from icesculpt.pixmap_generator import recolor_all_pixmaps
import tempfile
import os
import shutil

class TestPixmapAugmented(unittest.TestCase):
    def test_xpm_recolor_logic(self):
        # Create a simple XPM
        img = XpmImage(width=2, height=2)
        img.colors['.'] = "#FF0000" # Red
        img.pixels = ["..", ".."]
        
        # Shift hue by 0.5 (should turn red to cyan-ish)
        img.recolor(hue_shift=0.5)
        
        new_color = img.colors['.']
        self.assertNotEqual(new_color, "#FF0000")
        
    def test_recolor_all_pixmaps(self):
        test_dir = tempfile.mkdtemp()
        try:
            # Create a dummy XPM file
            xpm_path = os.path.join(test_dir, "test.xpm")
            img = XpmImage(width=1, height=1)
            img.colors['.'] = "#FF0000"
            img.pixels = ["."]
            with open(xpm_path, "w") as f:
                f.write(img.to_xpm3())
            
            # Recolor
            recolored = recolor_all_pixmaps(test_dir, hue_shift=0.1)
            self.assertIn("test.xpm", recolored)
            
            # Verify file was written
            with open(xpm_path, "r") as f:
                content = f.read()
                self.assertIn("static char", content)
        finally:
            shutil.rmtree(test_dir)

if __name__ == "__main__":
    unittest.main()
