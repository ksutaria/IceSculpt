"""Tests for editor panel logic (headless)."""

import unittest
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from icesculpt.theme_model import ThemeModel
from icesculpt.editors.desktop_editor import DesktopEditor
from icesculpt.editors.dimension_editor import DimensionEditor
from icesculpt.editors.font_editor import FontEditor
from icesculpt.editors.icon_editor import IconEditor
from icesculpt.editors.look_editor import LookEditor
from icesculpt.editors.metadata_editor import MetadataEditor
from icesculpt.editors.taskbar_editor import TaskbarEditor

class TestEditors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()

    def test_instantiate_all_editors(self):
        editors = [
            DesktopEditor,
            DimensionEditor,
            FontEditor,
            IconEditor,
            LookEditor,
            MetadataEditor,
            TaskbarEditor
        ]
        for editor_cls in editors:
            editor = editor_cls(self.model)
            self.assertIsNotNone(editor)
            # Basic sanity check: should have some children
            if isinstance(editor, Gtk.Container):
                self.assertGreater(len(editor.get_children()), 0)

    def test_metadata_editor_logic(self):
        editor = MetadataEditor(self.model)
        # Find description entry
        # ... (implementation dependent, but just exercising instantiation helps)
        self.model.set("ThemeDescription", "New Desc")
        # Ensure it doesn't crash on model update
        from gi.repository import GLib
        for _ in range(10):
            GLib.main_context_default().iteration(False)


class TestEditorsBoost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()

    def test_new_theme_dialog_properties(self):
        from icesculpt.dialogs.new_theme import NewThemeDialog
        dialog = NewThemeDialog()
        dialog._name_entry.set_text("CustomName")
        dialog._author_entry.set_text("CustomAuthor")
        self.assertEqual(dialog.theme_name, "CustomName")
        self.assertEqual(dialog.author, "CustomAuthor")
        self.assertEqual(dialog.look_style, "flat")
        dialog.destroy()

    def test_metadata_editor_extra(self):
        self.model.set("ThemeDescription", "Old")
        editor = MetadataEditor(self.model)
        editor._entries["ThemeAuthor"].set_text("NewAuthor")
        self.assertEqual(self.model.get("ThemeAuthor"), "NewAuthor")
        self.model.set("ThemeDescription", "NewDescription")
        self.assertEqual(editor._entries["ThemeDescription"].get_text(), "NewDescription")
        self.model.batch_update({"License": "GPL"})
        self.assertEqual(editor._entries["License"].get_text(), "GPL")

if __name__ == "__main__":
    unittest.main()
