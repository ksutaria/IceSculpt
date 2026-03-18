"""Tests for theme_parser module."""

import os
import tempfile
import unittest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from icesculpt.theme_parser import (
    parse_theme_file, parse_theme_file_from_string, extract_values,
    update_value, remove_key, write_theme_file, create_empty_theme,
)


SAMPLE_THEME = """\
# Test theme
# by Author

ThemeDescription="Test Theme"
ThemeAuthor="Test Author"
Look=flat

# Colors
ColorActiveTitleBar="rgb:40/80/C0"
ColorNormalTitleBar=rgb:C0/C0/C0
ColorActiveTitleBarText="#FFFFFF"

BorderSizeX=6
BorderSizeY=6
TitleBarHeight=20
"""


class TestParsing(unittest.TestCase):
    def test_parse_string(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        self.assertGreater(len(lines), 0)

    def test_extract_values(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        vals = extract_values(lines)
        self.assertEqual(vals["ThemeDescription"], "Test Theme")
        self.assertEqual(vals["ThemeAuthor"], "Test Author")
        self.assertEqual(vals["Look"], "flat")
        self.assertEqual(vals["ColorActiveTitleBar"], "rgb:40/80/C0")
        self.assertEqual(vals["ColorNormalTitleBar"], "rgb:C0/C0/C0")
        self.assertEqual(vals["BorderSizeX"], "6")

    def test_comments_preserved(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        comment_lines = [l for l in lines if l.comment_only]
        self.assertGreaterEqual(len(comment_lines), 2)

    def test_blank_lines_preserved(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        blank_lines = [l for l in lines if l.blank]
        self.assertGreater(len(blank_lines), 0)

    def test_quoted_value_unquoted(self):
        lines = parse_theme_file_from_string('Key="value with spaces"')
        vals = extract_values(lines)
        self.assertEqual(vals["Key"], "value with spaces")

    def test_unquoted_value(self):
        lines = parse_theme_file_from_string("Look=flat")
        vals = extract_values(lines)
        self.assertEqual(vals["Look"], "flat")


class TestModification(unittest.TestCase):
    def test_update_existing(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        result = update_value(lines, "Look", "pixmap")
        self.assertTrue(result)
        vals = extract_values(lines)
        self.assertEqual(vals["Look"], "pixmap")

    def test_update_new_key(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        result = update_value(lines, "NewKey", "newvalue")
        self.assertFalse(result)
        vals = extract_values(lines)
        self.assertEqual(vals["NewKey"], "newvalue")

    def test_remove_key(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        result = remove_key(lines, "Look")
        self.assertTrue(result)
        vals = extract_values(lines)
        self.assertNotIn("Look", vals)

    def test_remove_nonexistent(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        result = remove_key(lines, "Nonexistent")
        self.assertFalse(result)


class TestRoundTrip(unittest.TestCase):
    def test_write_and_reread(self):
        lines = parse_theme_file_from_string(SAMPLE_THEME)
        vals_before = extract_values(lines)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".theme", delete=False) as f:
            tmppath = f.name

        try:
            write_theme_file(tmppath, lines)
            lines2 = parse_theme_file(tmppath)
            vals_after = extract_values(lines2)
            self.assertEqual(vals_before, vals_after)
        finally:
            os.unlink(tmppath)

    def test_create_empty_theme(self):
        lines = create_empty_theme("My Theme", "Author")
        vals = extract_values(lines)
        self.assertEqual(vals["ThemeDescription"], "My Theme")
        self.assertEqual(vals["ThemeAuthor"], "Author")
        self.assertIn("Look", vals)


class TestFileIO(unittest.TestCase):
    def test_parse_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".theme", delete=False) as f:
            f.write(SAMPLE_THEME)
            tmppath = f.name

        try:
            lines = parse_theme_file(tmppath)
            vals = extract_values(lines)
            self.assertEqual(vals["ThemeDescription"], "Test Theme")
        finally:
            os.unlink(tmppath)


if __name__ == "__main__":
    unittest.main()


class TestLinterBoost(unittest.TestCase):
    def test_linter_boost(self):
        from icesculpt.theme_model import ThemeModel
        from icesculpt.linter import lint_theme, LintMessage
        model = ThemeModel()
        with tempfile.TemporaryDirectory() as d:
            model.theme_dir = d
            model.set("TitleBarPixmap", "missing.xpm")
            model.set("ColorActiveTitleBar", "#000000")
            model.set("ColorActiveTitleBarText", "#111111")
            
            messages = lint_theme(model)
            msg_str = [str(m) for m in messages]
            
            self.assertTrue(any("Referenced pixmap not found" in s for s in msg_str))
            self.assertTrue(any("Low contrast ratio" in s for s in msg_str))
            
            lm = LintMessage("K", "M", "error")
            self.assertEqual(str(lm), "[ERROR] K: M")


class TestParserBoost(unittest.TestCase):
    def test_parser_unparseable(self):
        content = "This is not a key value pair"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".theme", delete=False) as f:
            f.write(content)
            path = f.name
        try:
            lines = parse_theme_file(path)
            self.assertEqual(len(lines), 1)
            self.assertEqual(lines[0].raw, content)
        finally:
            os.unlink(path)
            
    def test_theme_line_to_string(self):
        from icesculpt.theme_parser import ThemeLine
        tl_blank = ThemeLine("", blank=True)
        self.assertEqual(tl_blank.to_string(), "")
        tl_comment = ThemeLine("# Comment", comment_only=True)
        self.assertEqual(tl_comment.to_string(), "# Comment")
        tl_quoted = ThemeLine("", key="Key", value="Value with space")
        self.assertEqual(tl_quoted.to_string(), 'Key="Value with space"')

    def test_theme_line_quoting(self):
        from icesculpt.theme_parser import ThemeLine
        # Test _needs_quoting logic
        self.assertFalse(ThemeLine._needs_quoting(""))
        self.assertTrue(ThemeLine._needs_quoting("With Space"))
        self.assertFalse(ThemeLine._needs_quoting("rgb:1/2/3 with space"))
        self.assertFalse(ThemeLine._needs_quoting("/path/to file"))
        self.assertFalse(ThemeLine._needs_quoting('Already "quoted"'))
