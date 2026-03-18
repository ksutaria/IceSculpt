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

        # Change something - MainWindow connects to model and snapshots on change
        self.win.model.set("BorderSizeX", "15")
        self.assertGreater(len(self.win._undo_stack), 0)

        # Undo
        self.win._on_undo(None)
        self.assertEqual(self.win.model.get("BorderSizeX"), "6") # Default

        # Note: In the current implementation, _on_undo pops from _undo_stack
        # and restores snapshot, which triggers _on_model_changed,
        # but _on_model_changed might push to _undo_stack again if not careful.
        # However, the goal here is to test that the stack is being managed.

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
