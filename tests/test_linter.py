"""Tests for the theme linter and health check."""

import unittest
from icesculpt.theme_model import ThemeModel
from icesculpt.linter import lint_theme

class TestLinter(unittest.TestCase):
    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme("Test Theme", "Author")

    def test_missing_metadata(self):
        self.model.set("ThemeDescription", "")
        messages = lint_theme(self.model)
        # Should have an info message about missing metadata
        infos = [m for m in messages if m.severity == "info"]
        self.assertTrue(any("ThemeDescription" in m.key for m in infos))

    def test_invalid_colors(self):
        self.model.set("ColorActiveTitleBar", "not-a-color")
        messages = lint_theme(self.model)
        errors = [m for m in messages if m.severity == "error"]
        self.assertTrue(any("ColorActiveTitleBar" in m.key for m in errors))

    def test_gradient_colors(self):
        # Valid gradient
        self.model.set("ColorActiveTitleBar", "rgb:00/00/00,rgb:FF/FF/FF")
        messages = lint_theme(self.model)
        errors = [m for m in messages if m.key == "ColorActiveTitleBar" and m.severity == "error"]
        self.assertEqual(len(errors), 0)
        
        # Invalid part in gradient
        self.model.set("ColorActiveTitleBar", "rgb:00/00/00,invalid")
        messages = lint_theme(self.model)
        errors = [m for m in messages if m.key == "ColorActiveTitleBar" and m.severity == "error"]
        self.assertGreater(len(errors), 0)

    def test_deprecated_keys(self):
        self.model.set("ShowHelp", "1")
        messages = lint_theme(self.model)
        warnings = [m for m in messages if m.severity == "warning" and m.key == "ShowHelp"]
        self.assertGreater(len(warnings), 0)

    def test_accessibility_contrast(self):
        # Low contrast: gray on gray
        self.model.set("ColorActiveTitleBar", "rgb:80/80/80")
        self.model.set("ColorActiveTitleBarText", "rgb:81/81/81")
        messages = lint_theme(self.model)
        warnings = [m for m in messages if "contrast" in m.message.lower()]
        self.assertGreater(len(warnings), 0)
        
        # High contrast: white on black
        self.model.set("ColorActiveTitleBar", "rgb:00/00/00")
        self.model.set("ColorActiveTitleBarText", "rgb:FF/FF/FF")
        messages = lint_theme(self.model)
        warnings = [m for m in messages if "contrast" in m.message.lower()]
        self.assertEqual(len(warnings), 0)

if __name__ == "__main__":
    unittest.main()
