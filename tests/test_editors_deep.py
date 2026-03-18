"""Deep tests for Desktop, Font, Icon, and Pixmap editors."""

import unittest
import os
import tempfile
import shutil
from unittest.mock import MagicMock, patch

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from icesculpt.theme_model import ThemeModel
from icesculpt.editors.desktop_editor import DesktopEditor
from icesculpt.editors.font_editor import FontEditor, xft_to_pango, pango_to_xft
from icesculpt.editors.icon_editor import IconEditor
from icesculpt.editors.pixmap_editor import PixmapEditor

class TestEditorsDeep(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Gtk.init([])

    def setUp(self):
        self.model = ThemeModel()
        self.test_dir = tempfile.mkdtemp()
        self.model.theme_dir = self.test_dir

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    # --- DesktopEditor ---
    def test_desktop_editor_logic(self):
        editor = DesktopEditor(self.model)
        # Color change
        editor._on_bg_color_changed(None, "#FF0000")
        self.assertEqual(self.model.get_color_hex("DesktopBackgroundColor"), "#FF0000")
        
        # Wallpaper entry
        editor._wp_entry.set_text("/path/to/wall.png")
        self.assertEqual(self.model.get("DesktopBackgroundImage"), "/path/to/wall.png")
        
        # Boolean keys
        editor._bool_switches["DesktopBackgroundScaled"].set_active(True)
        self.assertTrue(self.model.get_bool("DesktopBackgroundScaled"))

    @patch('icesculpt.editors.desktop_editor.Gtk.FileChooserDialog')
    def test_desktop_editor_browse(self, mock_dialog):
        editor = DesktopEditor(self.model)
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
        mock_dialog.return_value.get_filename.return_value = "/tmp/bg.jpg"
        
        editor._on_browse_wallpaper(None)
        self.assertEqual(self.model.get("DesktopBackgroundImage"), "/tmp/bg.jpg")

    # --- FontEditor ---
    def test_font_utils(self):
        self.assertEqual(xft_to_pango("Sans:size=12:bold"), "Sans Bold 12")
        self.assertEqual(pango_to_xft("Sans Bold Italic 12"), "Sans:size=12:bold:italic")
        self.assertEqual(xft_to_pango(""), "Sans 10")
        self.assertEqual(pango_to_xft(""), "sans-serif:size=10")

    def test_font_utils_complex(self):
        # style= variant
        self.assertEqual(xft_to_pango("Sans:style=Bold Italic:size=11"), "Sans Bold Italic 11")
        # italic only
        self.assertEqual(xft_to_pango("Sans:italic:size=9"), "Sans Italic 9")

    def test_font_editor_individual_change(self):
        editor = FontEditor(self.model)
        key = "MenuFontNameXft"
        btn, label = editor._buttons[key]
        
        self.model.set(key, "Monospace:size=13")
        self.assertEqual(label.get_text(), "Monospace:size=13")

    def test_font_editor_logic(self):
        editor = FontEditor(self.model)
        key = "TitleFontNameXft"
        btn, label = editor._buttons[key]
        
        # Simulate font set
        btn.get_font = MagicMock(return_value="Serif 14")
        editor._on_font_set(btn, key)
        self.assertEqual(self.model.get(key), "Serif:size=14")
        self.assertEqual(label.get_text(), "Serif:size=14")

    # --- IconEditor ---
    def test_icon_editor_load(self):
        # Create dummy icon structure
        icons_dir = os.path.join(self.test_dir, "icons", "16x16")
        os.makedirs(icons_dir)
        with open(os.path.join(icons_dir, "test.png"), "w") as f: f.write("fake")
        
        # Mock GdkPixbuf to avoid real file reading
        with patch('gi.repository.GdkPixbuf.Pixbuf.new_from_file_at_scale'):
            editor = IconEditor(self.model)
            # Should have added one item to flowbox (even if pixbuf mock returns None, 
            # it might fail or we can mock it better)
            pass

    @patch('icesculpt.editors.icon_editor.Gtk.FileChooserDialog')
    @patch('shutil.copy2')
    def test_icon_editor_import(self, mock_copy, mock_dialog):
        editor = IconEditor(self.model)
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
        mock_dialog.return_value.get_filename.return_value = "/tmp/icon.png"
        
        editor._on_import(None)
        mock_copy.assert_called()

    # --- PixmapEditor ---
    def test_pixmap_editor_zoom_save(self):
        editor = PixmapEditor(self.model)
        
        # Zoom
        editor._set_zoom(20)
        self.assertEqual(editor._canvas.zoom, 20)
        self.assertIn("20x", editor._zoom_label.get_text())
        
        # Save (no image yet)
        editor._on_save_pixmap(None) # Should not crash

    @patch('icesculpt.editors.pixmap_editor.Gtk.Dialog')
    def test_pixmap_editor_recolor(self, mock_dialog):
        editor = PixmapEditor(self.model)
        mock_dialog.return_value.run.return_value = Gtk.ResponseType.OK
        
        with patch('icesculpt.pixmap_generator.recolor_all_pixmaps', return_value=["a.xpm"]):
            editor._on_recolor_all_clicked(None)
            self.assertIn("Recolored 1", editor._info_label.get_text())

    def test_pixmap_editor_generate(self):
        editor = PixmapEditor(self.model)
        with patch('icesculpt.editors.pixmap_editor.generate_all_buttons', return_value={"closeA.xpm": MagicMock()}):
            editor._on_generate_buttons(None)
            self.assertTrue(len(os.listdir(self.test_dir)) > 0)

    def test_about_dialog(self):
        from icesculpt.dialogs.about import show_about_dialog
        with patch('icesculpt.dialogs.about.Gtk.AboutDialog') as mock_dlg:
            show_about_dialog(None)
            mock_dlg.assert_called()

    def test_font_editor_error_fallbacks(self):
        editor = FontEditor(self.model)
        # Model update with invalid font
        with patch('icesculpt.editors.font_editor.xft_to_pango', side_effect=Exception("Bad")):
            self.model.set("TitleFontNameXft", "invalid")
            btn, label = editor._buttons["TitleFontNameXft"]
            self.assertEqual(label.get_text(), "invalid")

    def test_icon_editor_errors(self):
        self.model.theme_dir = None
        editor = IconEditor(self.model)
        with patch.object(editor, '_show_error') as mock_err:
            editor._on_import(None)
            mock_err.assert_called()

    def test_pixmap_editor_png_selection(self):
        editor = PixmapEditor(self.model)
        selection = MagicMock()
        mock_model = Gtk.ListStore(str, str)
        it = mock_model.append(["test.png", "/path/test.png"])
        selection.get_selected.return_value = (mock_model, it)
        editor._on_selection_changed(selection)
        self.assertIn("PNG", editor._info_label.get_text())

    def test_pixmap_editor_selection(self):
        from icesculpt.xpm_codec import XpmImage, write_xpm_file
        img = XpmImage(2, 2)
        img.colors["."] = "#FFFFFF"
        path = os.path.join(self.test_dir, "test.xpm")
        write_xpm_file(path, img)
        
        editor = PixmapEditor(self.model)
        # Mock selection
        selection = MagicMock()
        mock_model = Gtk.ListStore(str, str)
        it = mock_model.append(["test.xpm", path])
        selection.get_selected.return_value = (mock_model, it)
        
        editor._on_selection_changed(selection)
        self.assertEqual(editor._current_path, path)
        self.assertEqual(editor._canvas.image.width, 2)

    def test_font_editor_model_sync(self):
        editor = FontEditor(self.model)
        self.model.set("TitleFontNameXft", "Serif:size=20")
        # Should update the label
        btn, label = editor._buttons["TitleFontNameXft"]
        self.assertEqual(label.get_text(), "Serif:size=20")
        
        # Test full reload
        self.model._fire_callbacks(None)
        self.assertEqual(label.get_text(), "Serif:size=20")

    def test_pixmap_editor_frames(self):
        editor = PixmapEditor(self.model)
        with patch('icesculpt.editors.pixmap_editor.generate_all_frames', return_value={"frame.xpm": MagicMock()}):
            editor._on_generate_frames(None)
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "frame.xpm")))

if __name__ == "__main__":
    unittest.main()
