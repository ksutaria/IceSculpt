"""Extra tests for pixmap generation logic."""

import unittest
from icesculpt.theme_model import ThemeModel
from icesculpt.pixmap_generator import (
    generate_button, generate_frame_piece, 
    generate_all_buttons, generate_all_frames
)

class TestPixmapExtra(unittest.TestCase):
    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()

    def test_all_button_types(self):
        types = ['close', 'maximize', 'minimize', 'restore', 'rollup', 'rolldown', 'hide', 'depth', 'menu']
        for t in types:
            img = generate_button(t, 20, "#FF0000", "#00FF00")
            self.assertEqual(img.width, 20)
            self.assertIn("X", img.colors) # Should have symbol character

    def test_all_frame_pieces(self):
        positions = ['TL', 'T', 'TR', 'L', 'R', 'BL', 'B', 'BR']
        for p in positions:
            img = generate_frame_piece(p, 10, 10, "#FF0000")
            self.assertEqual(img.width, 10)

    def test_bulk_generators(self):
        # Buttons
        btns = generate_all_buttons(16, self.model)
        self.assertGreater(len(btns), 10)
        self.assertIn("closeA.xpm", btns)
        
        # Frames
        frames = generate_all_frames(6, 6, 24, 24, self.model)
        self.assertGreater(len(frames), 5)
        self.assertIn("frameATL.xpm", frames)

if __name__ == "__main__":
    unittest.main()
