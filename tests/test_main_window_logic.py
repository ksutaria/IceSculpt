"""Tests for MainWindow business logic (headless)."""

import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from icesculpt.app import IceSculptApp
from icesculpt.main_window import MainWindow

class TestMainWindowLogic(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.app = IceSculptApp()
        self.win = MainWindow(self.app)

    def test_undo_redo_stack(self):
        # Initial state
        self.assertEqual(len(self.win._undo_stack), 0)
        
        # Change something
        self.win.model.set("BorderSizeX", "15")
        self.assertGreater(len(self.win._undo_stack), 0)
        
        # Undo
        self.win._on_undo(None)
        self.assertEqual(self.win.model.get("BorderSizeX"), "6") # Default
        self.assertGreater(len(self.win._redo_stack), 0)
        
        # Redo
        self.win._on_redo(None)
        self.assertEqual(self.win.model.get("BorderSizeX"), "15")

    def test_accessibility_actions(self):
        # These methods are now in MainWindow
        self.win.model.set("FontActiveTitleBar", "Sans/10")
        self.win._on_apply_large_fonts(None)
        self.assertIn("/15", self.win.model.get("FontActiveTitleBar"))
        
        self.win._on_apply_high_contrast(None)
        self.assertEqual(self.win.model.get("ColorActiveTitleBar"), "rgb:00/00/00")

    def test_status_updates(self):
        self.win._status("Test Message")
        # Just ensure it doesn't crash

if __name__ == "__main__":
    unittest.main()
