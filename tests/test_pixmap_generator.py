"""Tests for pixmap_generator module."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from icesculpt.pixmap_generator import (
    generate_button, generate_frame_piece, generate_title_segment,
)
from icesculpt.xpm_codec import parse_xpm


class TestButtonGeneration(unittest.TestCase):
    def test_close_button(self):
        img = generate_button("close", 16, "#C0C0C0", "#000000")
        self.assertEqual(img.width, 16)
        self.assertEqual(img.height, 16)
        self.assertGreater(len(img.colors), 0)
        # Should be valid XPM
        text = img.to_xpm3("close")
        img2 = parse_xpm(text)
        self.assertEqual(img2.width, 16)

    def test_all_button_types(self):
        types = ["close", "maximize", "minimize", "restore",
                 "rollup", "rolldown", "hide", "depth", "menu"]
        for btn_type in types:
            img = generate_button(btn_type, 16, "#404040", "#FFFFFF")
            self.assertEqual(img.width, 16, f"Failed for {btn_type}")
            self.assertEqual(img.height, 16, f"Failed for {btn_type}")

    def test_button_sizes(self):
        for size in [12, 16, 20, 24, 32]:
            img = generate_button("close", size, "#C0C0C0", "#000000")
            self.assertEqual(img.width, size)
            self.assertEqual(img.height, size)

    def test_button_has_symbol(self):
        # Close button should have foreground pixels (X chars)
        img = generate_button("close", 16, "#C0C0C0", "#000000")
        has_fg = any("X" in row for row in img.pixels)
        self.assertTrue(has_fg, "Close button should have foreground pixels")


class TestFrameGeneration(unittest.TestCase):
    def test_frame_piece(self):
        img = generate_frame_piece("TL", 8, 8, "#5E81AC", active=True)
        self.assertEqual(img.width, 8)
        self.assertEqual(img.height, 8)

    def test_all_positions(self):
        positions = ["TL", "T", "TR", "L", "R", "BL", "B", "BR"]
        for pos in positions:
            img = generate_frame_piece(pos, 6, 6, "#5E81AC")
            self.assertEqual(img.width, 6, f"Failed for {pos}")

    def test_active_vs_inactive(self):
        active = generate_frame_piece("TL", 8, 8, "#5E81AC", active=True)
        inactive = generate_frame_piece("TL", 8, 8, "#4C566A", active=False)
        # Different base colors should give different pixmaps
        self.assertNotEqual(active.colors, inactive.colors)


class TestTitleSegment(unittest.TestCase):
    def test_solid(self):
        img = generate_title_segment("T", 20, 8, "#5E81AC")
        self.assertEqual(img.width, 20)
        self.assertEqual(img.height, 8)

    def test_gradient(self):
        img = generate_title_segment("T", 20, 8, "#5E81AC", "#2E3440")
        self.assertEqual(img.width, 20)
        # Should have multiple colors
        self.assertGreater(len(img.colors), 1)


if __name__ == "__main__":
    unittest.main()
