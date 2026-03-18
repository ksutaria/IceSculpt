"""Tests for xpm_codec module."""

import os
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from icesculpt.xpm_codec import (
    parse_xpm, create_solid, create_gradient_h, create_gradient_v,
    write_xpm_file, read_xpm_file,
)


SAMPLE_XPM = """\
/* XPM */
static char *test[] = {
"4 3 2 1",
". c #FF0000",
"X c #0000FF",
"..XX",
".XX.",
"XX.."
};
"""


class TestParsing(unittest.TestCase):
    def test_parse_basic(self):
        img = parse_xpm(SAMPLE_XPM)
        self.assertEqual(img.width, 4)
        self.assertEqual(img.height, 3)
        self.assertEqual(img.cpp, 1)
        self.assertEqual(len(img.colors), 2)
        self.assertEqual(len(img.pixels), 3)

    def test_colors(self):
        img = parse_xpm(SAMPLE_XPM)
        self.assertEqual(img.colors["."], "#FF0000")
        self.assertEqual(img.colors["X"], "#0000FF")

    def test_pixels(self):
        img = parse_xpm(SAMPLE_XPM)
        self.assertEqual(img.pixels[0], "..XX")
        self.assertEqual(img.pixels[1], ".XX.")
        self.assertEqual(img.pixels[2], "XX..")

    def test_get_pixel(self):
        img = parse_xpm(SAMPLE_XPM)
        self.assertEqual(img.get_pixel(0, 0), ".")
        self.assertEqual(img.get_pixel(2, 0), "X")

    def test_get_color_at(self):
        img = parse_xpm(SAMPLE_XPM)
        self.assertEqual(img.get_color_at(0, 0), "#FF0000")
        self.assertEqual(img.get_color_at(3, 0), "#0000FF")

    def test_transparency(self):
        xpm_text = '''/* XPM */
static char *t[] = {
"2 1 2 1",
". c None",
"X c #FF0000",
".X"
};'''
        img = parse_xpm(xpm_text)
        self.assertIsNone(img.get_color_at(0, 0))
        self.assertEqual(img.get_color_at(1, 0), "#FF0000")


class TestModification(unittest.TestCase):
    def test_set_pixel(self):
        img = parse_xpm(SAMPLE_XPM)
        img.set_pixel(0, 0, "X")
        self.assertEqual(img.get_pixel(0, 0), "X")

    def test_clone(self):
        img = parse_xpm(SAMPLE_XPM)
        clone = img.clone()
        clone.set_pixel(0, 0, "X")
        # Original should be unchanged
        self.assertEqual(img.get_pixel(0, 0), ".")
        self.assertEqual(clone.get_pixel(0, 0), "X")


class TestGeneration(unittest.TestCase):
    def test_create_solid(self):
        img = create_solid(4, 3, "#FF0000")
        self.assertEqual(img.width, 4)
        self.assertEqual(img.height, 3)
        self.assertEqual(len(img.pixels), 3)
        self.assertEqual(img.get_color_at(0, 0), "#FF0000")

    def test_create_gradient_h(self):
        img = create_gradient_h(5, 2, "#000000", "#FFFFFF")
        self.assertEqual(img.width, 5)
        self.assertEqual(img.height, 2)
        # First pixel should be black-ish, last should be white-ish
        first = img.get_color_at(0, 0)
        last = img.get_color_at(4, 0)
        self.assertEqual(first, "#000000")
        self.assertEqual(last, "#FFFFFF")

    def test_create_gradient_v(self):
        img = create_gradient_v(2, 5, "#000000", "#FFFFFF")
        self.assertEqual(img.height, 5)
        first = img.get_color_at(0, 0)
        last = img.get_color_at(0, 4)
        self.assertEqual(first, "#000000")
        self.assertEqual(last, "#FFFFFF")

    def test_transparent_solid(self):
        img = create_solid(3, 3, None)
        self.assertIsNone(img.get_color_at(0, 0))


class TestSerialization(unittest.TestCase):
    def test_to_xpm3(self):
        img = create_solid(2, 2, "#FF0000")
        text = img.to_xpm3("test")
        self.assertIn("/* XPM */", text)
        self.assertIn("2 2 1 1", text)

    def test_roundtrip_string(self):
        img = parse_xpm(SAMPLE_XPM)
        text = img.to_xpm3("test")
        img2 = parse_xpm(text)
        self.assertEqual(img.width, img2.width)
        self.assertEqual(img.height, img2.height)
        self.assertEqual(img.pixels, img2.pixels)

    def test_roundtrip_file(self):
        img = create_solid(4, 4, "#AABBCC")
        with tempfile.NamedTemporaryFile(suffix=".xpm", delete=False) as f:
            tmppath = f.name

        try:
            write_xpm_file(tmppath, img)
            img2 = read_xpm_file(tmppath)
            self.assertEqual(img.width, img2.width)
            self.assertEqual(img.height, img2.height)
            self.assertEqual(img2.get_color_at(0, 0), "#AABBCC")
        finally:
            os.unlink(tmppath)


class TestXpmCodecBoost(unittest.TestCase):
    def test_xpm_codec_errors(self):
        from icesculpt import xpm_codec
        with self.assertRaises(ValueError):
            xpm_codec.parse_xpm("no strings here")
        with self.assertRaises(ValueError):
            xpm_codec.parse_xpm('"10 10 1 1"') 
        with self.assertRaises(ValueError):
            xpm_codec.parse_xpm('"1 1 2 1", "char c #000000"') 
        with self.assertRaises(ValueError):
            xpm_codec.parse_xpm('"1 1 1 1", "char c #000000"') 

    def test_xpm_gradients_large(self):
        from icesculpt import xpm_codec
        # Wide gradient (cpp=2)
        grad_h = xpm_codec.create_gradient_h(100, 10, "#000000", "#FFFFFF")
        self.assertEqual(grad_h.cpp, 2)
        grad_v = xpm_codec.create_gradient_v(10, 100, "#000000", "#FFFFFF")
        self.assertEqual(grad_v.cpp, 2)

    def test_xpm_image_methods_extra(self):
        from icesculpt import xpm_codec
        img = xpm_codec.XpmImage(2, 2)
        img.set_pixel(0, 0, img.get_pixel(1, 1))
        self.assertEqual(img.get_color_at(0, 0), "#C0C0C0")
        self.assertIsNone(img.get_pixel(5, 5))
        self.assertIsNone(img.get_color_at(5, 5))
        
        img.colors["."] = "#FF0000"
        img.pixels = ["..", ".."]
        img.recolor(hue_shift=0.5)
        self.assertNotEqual(img.get_color_at(0, 0), "#FF0000")

    def test_xpm_write_name_sanitization(self):
        from icesculpt import xpm_codec
        img = xpm_codec.create_solid(1, 1, "#000000")
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bad-name.xpm")
            xpm_codec.write_xpm_file(path, img)
            with open(path, "r") as f:
                content = f.read()
                self.assertIn("static char *bad_name[]", content)


if __name__ == "__main__":
    unittest.main()
