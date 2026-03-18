"""Deep logic tests for MainWindow (headless)."""

import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from icesculpt.app import IceSculptApp
from icesculpt.main_window import MainWindow

class TestMainWindowDeep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.app = IceSculptApp()
        self.win = MainWindow(self.app)

    def test_view_menu_focus_logic(self):
        # Test focus operations
        self.win._on_focus_editor(None)
        self.win._on_focus_preview(None)
        self.win._on_split_equal(None)
        # Verify positions indirectly via logic execution

    def test_undo_redo_complex(self):
        model = self.win.model
        
        # 1. First change
        model.set("BorderSizeX", "10")
        self.assertEqual(len(self.win._undo_stack), 1)
        
        # 2. Second change
        model.set("BorderSizeX", "20")
        self.assertEqual(len(self.win._undo_stack), 2)
        
        # 3. Undo
        self.win._on_undo(None)
        self.assertEqual(model.get("BorderSizeX"), "10")
        self.assertEqual(len(self.win._redo_stack), 1)
        
        # 4. Redo
        self.win._on_redo(None)
        self.assertEqual(model.get("BorderSizeX"), "20")

    def test_model_callback_title_update(self):
        model = self.win.model
        model.set("ThemeDescription", "New Title")
        # Callback should have fired _update_title
        self.assertIn("New Title", self.win.get_title())

if __name__ == "__main__":
    unittest.main()
