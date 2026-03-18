"""Tests for color_utils module."""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from icesculpt.color_utils import (
    icewm_to_hex, hex_to_icewm, hex_to_rgba, rgba_to_hex,
    darken, lighten, blend,
)


class TestIcewmToHex(unittest.TestCase):
    def test_rgb_format(self):
        self.assertEqual(icewm_to_hex("rgb:FF/00/80"), "#FF0080")

    def test_rgb_lowercase(self):
        self.assertEqual(icewm_to_hex("rgb:ff/00/80"), "#FF0080")

    def test_hex_passthrough(self):
        self.assertEqual(icewm_to_hex("#AABBCC"), "#AABBCC")

    def test_hex3_expansion(self):
        self.assertEqual(icewm_to_hex("#F08"), "#FF0088")

    def test_named_color(self):
        self.assertEqual(icewm_to_hex("black"), "#000000")
        self.assertEqual(icewm_to_hex("white"), "#FFFFFF")
        self.assertEqual(icewm_to_hex("red"), "#FF0000")

    def test_named_color_case_insensitive(self):
        self.assertEqual(icewm_to_hex("Navy"), "#000080")

    def test_whitespace_stripped(self):
        self.assertEqual(icewm_to_hex("  rgb:FF/FF/FF  "), "#FFFFFF")

    def test_invalid_raises(self):
        with self.assertRaises(ValueError):
            icewm_to_hex("notacolor")

    def test_single_char_hex(self):
        # rgb:F/0/0 should expand to rgb:FF/00/00
        self.assertEqual(icewm_to_hex("rgb:F/0/0"), "#FF0000")


class TestHexToIcewm(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(hex_to_icewm("#FF0080"), "rgb:FF/00/80")

    def test_lowercase_input(self):
        self.assertEqual(hex_to_icewm("#aabbcc"), "rgb:AA/BB/CC")


class TestHexToRgba(unittest.TestCase):
    def test_white(self):
        r, g, b, a = hex_to_rgba("#FFFFFF")
        self.assertAlmostEqual(r, 1.0)
        self.assertAlmostEqual(g, 1.0)
        self.assertAlmostEqual(b, 1.0)
        self.assertAlmostEqual(a, 1.0)

    def test_black(self):
        r, g, b, a = hex_to_rgba("#000000")
        self.assertAlmostEqual(r, 0.0)
        self.assertAlmostEqual(g, 0.0)
        self.assertAlmostEqual(b, 0.0)

    def test_midpoint(self):
        r, g, b, a = hex_to_rgba("#808080")
        self.assertAlmostEqual(r, 128 / 255.0, places=3)


class TestRgbaToHex(unittest.TestCase):
    def test_white(self):
        self.assertEqual(rgba_to_hex(1.0, 1.0, 1.0), "#FFFFFF")

    def test_black(self):
        self.assertEqual(rgba_to_hex(0.0, 0.0, 0.0), "#000000")

    def test_clamps(self):
        self.assertEqual(rgba_to_hex(1.5, -0.5, 0.5), "#FF0080")


class TestRoundTrip(unittest.TestCase):
    def test_icewm_roundtrip(self):
        original = "rgb:AA/BB/CC"
        hex_val = icewm_to_hex(original)
        back = hex_to_icewm(hex_val)
        self.assertEqual(back, original)

    def test_rgba_roundtrip(self):
        hex_val = "#3F7FAF"
        r, g, b, a = hex_to_rgba(hex_val)
        result = rgba_to_hex(r, g, b)
        self.assertEqual(result, hex_val)


class TestColorOps(unittest.TestCase):
    def test_darken(self):
        result = darken("#FFFFFF", 0.5)
        r, g, b, a = hex_to_rgba(result)
        self.assertAlmostEqual(r, 0.5, places=1)

    def test_lighten(self):
        result = lighten("#000000", 0.5)
        r, g, b, a = hex_to_rgba(result)
        self.assertAlmostEqual(r, 0.5, places=1)

    def test_blend_midpoint(self):
        result = blend("#000000", "#FFFFFF", 0.5)
        r, g, b, a = hex_to_rgba(result)
        self.assertAlmostEqual(r, 0.5, places=1)

    def test_blend_endpoints(self):
        self.assertEqual(blend("#FF0000", "#0000FF", 0.0), "#FF0000")
        self.assertEqual(blend("#FF0000", "#0000FF", 1.0), "#0000FF")


if __name__ == "__main__":
    unittest.main()
