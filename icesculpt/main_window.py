"""Main application window — split layout with editor tabs and live preview."""

import json
import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

from .theme_model import ThemeModel
from .widgets.preview_area import PreviewArea
from .editors.color_editor import ColorEditor
from .editors.font_editor import FontEditor
from .editors.dimension_editor import DimensionEditor
from .editors.look_editor import LookEditor
from .editors.metadata_editor import MetadataEditor
from .editors.pixmap_editor import PixmapEditor
from .editors.taskbar_editor import TaskbarEditor
from .editors.desktop_editor import DesktopEditor
from .editors.icon_editor import IconEditor
from .dialogs.new_theme import NewThemeDialog
from .dialogs.import_export import import_theme_dialog, export_theme_dialog
from .dialogs.about import show_about_dialog

# Presets directory
_PRESETS_DIR = os.path.join(os.path.dirname(__file__), "data", "presets")


class MainWindow(Gtk.ApplicationWindow):
    """Main application window with menu bar, editor tabs, and preview."""

    def __init__(self, app):
        super().__init__(application=app, title="IceSculpt")
        self.set_default_size(1200, 750)

        self.model = ThemeModel()
        self.model.connect(self._on_model_changed)

        # Undo/redo stacks for theme-level changes
        self._undo_stack = []
        self._redo_stack = []
        self._last_snapshot = None

        # Main vertical layout
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        # Menu bar
        vbox.pack_start(self._create_menu_bar(), False, False, 0)

        # Horizontal paned: editors (left) | preview (right)
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        # Left: tabbed editor notebook
        self._notebook = Gtk.Notebook()
        self._notebook.set_scrollable(True)
        self._notebook.set_size_request(300, -1)

        # Create editor tabs with mnemonic labels
        self._add_tab("_Colors", ColorEditor(self.model))
        self._add_tab("_Fonts", FontEditor(self.model))
        self._add_tab("_Dimensions", DimensionEditor(self.model))
        self._add_tab("_Look & Feel", LookEditor(self.model))
        self._add_tab("_Pixmaps", PixmapEditor(self.model))
        self._add_tab("_Taskbar", TaskbarEditor(self.model))
        self._add_tab("D_esktop", DesktopEditor(self.model))
        self._add_tab("_Icons", IconEditor(self.model))
        self._add_tab("_Metadata", MetadataEditor(self.model))

        paned.pack1(self._notebook, resize=True, shrink=True)

        # Right: live preview
        preview_frame = Gtk.Frame(label="Preview")
        preview_frame.set_margin_start(4)
        preview_frame.set_margin_end(4)
        preview_frame.set_margin_top(4)
        preview_frame.set_margin_bottom(4)

        self._preview = PreviewArea(self.model)
        preview_frame.add(self._preview)
        paned.pack2(preview_frame, resize=True, shrink=True)

        self._paned = paned
        paned.set_position(550)
        vbox.pack_start(paned, True, True, 0)

        # Status bar
        self._statusbar = Gtk.Statusbar()
        self._status_ctx = self._statusbar.get_context_id("main")
        vbox.pack_start(self._statusbar, False, False, 0)

        self._update_title()
        self._status("Ready — create or open a theme to begin")

        # Window close handler
        self.connect("delete-event", self._on_delete_event)

        # Keyboard shortcuts
        self.connect("key-press-event", self._on_key_press)

        # Take initial undo snapshot
        self._snapshot_for_undo()

        self.show_all()

    def _add_tab(self, label, widget):
        """Add a tab to the notebook with mnemonic support."""
        tab_label = Gtk.Label(label=label)
        tab_label.set_use_underline(True)
        self._notebook.append_page(widget, tab_label)

    def _create_menu_bar(self):
        """Create the menu bar with accelerators and mnemonics."""
        menubar = Gtk.MenuBar()
        accel = Gtk.AccelGroup()
        self.add_accel_group(accel)

        # File menu
        file_item = Gtk.MenuItem.new_with_mnemonic("_File")
        file_menu = Gtk.Menu()

        new_item = Gtk.MenuItem.new_with_mnemonic("_New Theme...")
        new_item.add_accelerator("activate", accel, Gdk.KEY_n,
                                 Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        new_item.connect("activate", self._on_new)
        file_menu.append(new_item)

        open_item = Gtk.MenuItem.new_with_mnemonic("_Open...")
        open_item.add_accelerator("activate", accel, Gdk.KEY_o,
                                  Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        open_item.connect("activate", self._on_open)
        file_menu.append(open_item)

        file_menu.append(Gtk.SeparatorMenuItem())

        save_item = Gtk.MenuItem.new_with_mnemonic("_Save")
        save_item.add_accelerator("activate", accel, Gdk.KEY_s,
                                  Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        save_item.connect("activate", self._on_save)
        file_menu.append(save_item)

        save_as_item = Gtk.MenuItem.new_with_mnemonic("Save _As...")
        save_as_item.add_accelerator("activate", accel, Gdk.KEY_s,
                                     Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
                                     Gtk.AccelFlags.VISIBLE)
        save_as_item.connect("activate", self._on_save_as)
        file_menu.append(save_as_item)

        file_menu.append(Gtk.SeparatorMenuItem())

        import_item = Gtk.MenuItem.new_with_mnemonic("_Import Archive...")
        import_item.connect("activate", self._on_import)
        file_menu.append(import_item)

        export_item = Gtk.MenuItem.new_with_mnemonic("_Export Archive...")
        export_item.add_accelerator("activate", accel, Gdk.KEY_e,
                                    Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        export_item.connect("activate", self._on_export)
        file_menu.append(export_item)

        file_menu.append(Gtk.SeparatorMenuItem())

        # Presets submenu
        presets_item = Gtk.MenuItem.new_with_mnemonic("Apply _Preset")
        presets_menu = Gtk.Menu()
        self._build_presets_menu(presets_menu)
        presets_item.set_submenu(presets_menu)
        file_menu.append(presets_item)

        file_menu.append(Gtk.SeparatorMenuItem())

        apply_item = Gtk.MenuItem.new_with_mnemonic("A_pply to IceWM")
        apply_item.connect("activate", self._on_apply)
        file_menu.append(apply_item)

        file_menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem.new_with_mnemonic("_Quit")
        quit_item.add_accelerator("activate", accel, Gdk.KEY_q,
                                  Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        quit_item.connect("activate", lambda w: self._try_quit())
        file_menu.append(quit_item)

        file_item.set_submenu(file_menu)
        menubar.append(file_item)

        # Edit menu
        edit_item = Gtk.MenuItem.new_with_mnemonic("_Edit")
        edit_menu = Gtk.Menu()

        undo_item = Gtk.MenuItem.new_with_mnemonic("_Undo")
        undo_item.add_accelerator("activate", accel, Gdk.KEY_z,
                                  Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        undo_item.connect("activate", self._on_undo)
        edit_menu.append(undo_item)

        redo_item = Gtk.MenuItem.new_with_mnemonic("_Redo")
        redo_item.add_accelerator("activate", accel, Gdk.KEY_y,
                                  Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        redo_item.connect("activate", self._on_redo)
        edit_menu.append(redo_item)

        edit_item.set_submenu(edit_menu)
        menubar.append(edit_item)

        # Tools menu
        tools_item = Gtk.MenuItem.new_with_mnemonic("_Tools")
        tools_menu = Gtk.Menu()

        health_item = Gtk.MenuItem.new_with_mnemonic("Check Theme _Health")
        health_item.connect("activate", self._on_check_health)
        tools_menu.append(health_item)

        tools_menu.append(Gtk.SeparatorMenuItem())

        acc_item = Gtk.MenuItem.new_with_mnemonic("_Accessibility")
        acc_menu = Gtk.Menu()

        large_font_item = Gtk.MenuItem.new_with_mnemonic("_Large Fonts")
        large_font_item.connect("activate", self._on_apply_large_fonts)
        acc_menu.append(large_font_item)

        high_contrast_item = Gtk.MenuItem.new_with_mnemonic("_High Contrast")
        high_contrast_item.connect("activate", self._on_apply_high_contrast)
        acc_menu.append(high_contrast_item)

        acc_item.set_submenu(acc_menu)
        tools_menu.append(acc_item)

        tools_item.set_submenu(tools_menu)
        menubar.append(tools_item)

        # View menu
        view_item = Gtk.MenuItem.new_with_mnemonic("_View")
        view_menu = Gtk.Menu()

        toggle_preview = Gtk.CheckMenuItem.new_with_mnemonic("Show _Preview")
        toggle_preview.set_active(True)
        toggle_preview.add_accelerator("activate", accel, Gdk.KEY_p,
                                       Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
                                       Gtk.AccelFlags.VISIBLE)
        toggle_preview.connect("toggled", self._on_toggle_preview)
        view_menu.append(toggle_preview)
        self._toggle_preview_item = toggle_preview

        view_menu.append(Gtk.SeparatorMenuItem())

        split_equal = Gtk.MenuItem.new_with_mnemonic("_Equal Split")
        split_equal.add_accelerator("activate", accel, Gdk.KEY_equal,
                                    Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        split_equal.connect("activate", self._on_split_equal)
        view_menu.append(split_equal)

        focus_editor = Gtk.MenuItem.new_with_mnemonic("Focus _Editor")
        focus_editor.add_accelerator("activate", accel, Gdk.KEY_bracketleft,
                                     Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        focus_editor.connect("activate", self._on_focus_editor)
        view_menu.append(focus_editor)

        focus_preview = Gtk.MenuItem.new_with_mnemonic("Focus Pre_view")
        focus_preview.add_accelerator("activate", accel, Gdk.KEY_bracketright,
                                      Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        focus_preview.connect("activate", self._on_focus_preview)
        view_menu.append(focus_preview)

        view_item.set_submenu(view_menu)
        menubar.append(view_item)

        # Help menu
        help_item = Gtk.MenuItem.new_with_mnemonic("_Help")
        help_menu = Gtk.Menu()

        about_item = Gtk.MenuItem.new_with_mnemonic("_About")
        about_item.connect("activate", lambda w: show_about_dialog(self))
        help_menu.append(about_item)

        help_item.set_submenu(help_menu)
        menubar.append(help_item)

        return menubar

    def _build_presets_menu(self, menu):
        """Populate the presets submenu from data/presets/*.json."""
        presets_dir = os.path.normpath(_PRESETS_DIR)
        if not os.path.isdir(presets_dir):
            item = Gtk.MenuItem(label="(no presets found)")
            item.set_sensitive(False)
            menu.append(item)
            return

        for fname in sorted(os.listdir(presets_dir)):
            if not fname.endswith(".json"):
                continue
            path = os.path.join(presets_dir, fname)
            try:
                with open(path) as f:
                    data = json.load(f)
                name = data.get("name", fname.replace(".json", ""))
            except Exception:
                continue
            item = Gtk.MenuItem(label=name)
            item.connect("activate", self._on_apply_preset, path)
            menu.append(item)

    def _on_apply_preset(self, widget, preset_path):
        """Apply a color preset to the current theme."""
        try:
            with open(preset_path) as f:
                data = json.load(f)
            colors = data.get("colors", {})
            if colors:
                self._snapshot_for_undo()
                self.model.batch_update(colors)
                name = data.get("name", "preset")
                self._status(f"Applied preset: {name}")
        except Exception as e:
            self._show_error(f"Failed to apply preset:\n{e}")

    # -- View operations --

    def _on_toggle_preview(self, widget):
        """Show or hide the preview pane."""
        if widget.get_active():
            self._paned.get_child2().show()
            # Restore split to a reasonable position
            alloc = self.get_allocation()
            self._paned.set_position(alloc.width // 2)
        else:
            self._paned.get_child2().hide()

    def _on_split_equal(self, widget):
        """Set the paned divider to 50/50."""
        alloc = self.get_allocation()
        self._paned.set_position(alloc.width // 2)

    def _on_focus_editor(self, widget):
        """Give more space to the editor (75/25 split)."""
        alloc = self.get_allocation()
        self._paned.set_position(int(alloc.width * 0.75))

    def _on_focus_preview(self, widget):
        """Give more space to the preview (25/75 split)."""
        alloc = self.get_allocation()
        self._paned.set_position(int(alloc.width * 0.25))

    # -- Tools operations --

    def _on_check_health(self, widget):
        from .linter import lint_theme
        messages = lint_theme(self.model)

        dialog = Gtk.Dialog(title="Theme Health Check", parent=self, flags=0)
        dialog.add_buttons(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE)
        dialog.set_default_size(500, 400)

        vbox = dialog.get_content_area()
        vbox.set_spacing(10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)

        if not messages:
            lbl = Gtk.Label(label="No issues found! Your theme looks healthy.")
            vbox.pack_start(lbl, True, True, 0)
        else:
            sw = Gtk.ScrolledWindow()
            sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            vbox.pack_start(sw, True, True, 0)

            listbox = Gtk.ListBox()
            listbox.set_selection_mode(Gtk.SelectionMode.NONE)
            sw.add(listbox)

            for msg in messages:
                row = Gtk.ListBoxRow()
                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                row.add(hbox)

                icon_name = "dialog-warning-symbolic"
                if msg.severity == "error":
                    icon_name = "dialog-error-symbolic"
                elif msg.severity == "info":
                    icon_name = "dialog-information-symbolic"

                img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
                hbox.pack_start(img, False, False, 0)

                lbl = Gtk.Label(label=f"<b>{msg.key}</b>: {msg.message}", xalign=0)
                lbl.set_use_markup(True)
                lbl.set_line_wrap(True)
                hbox.pack_start(lbl, True, True, 0)

                listbox.add(row)

        dialog.show_all()
        dialog.run()
        dialog.destroy()

    def _on_apply_large_fonts(self, widget):
        self._snapshot_for_undo()
        updates = {}
        # Simple heuristic: find all font keys and increase size
        for key in self.model.values:
            if "Font" in key:
                val = self.model.get(key)
                # IceWM font format is usually "name/size"
                if "/" in val:
                    parts = val.split('/')
                    try:
                        size = int(parts[-1])
                        parts[-1] = str(int(size * 1.5))
                        updates[key] = "/".join(parts)
                    except ValueError:
                        pass
        if updates:
            self.model.batch_update(updates)
            self._status("Applied large font transformation")

    def _on_apply_high_contrast(self, widget):
        self._snapshot_for_undo()
        updates = {}
        # Force title bars and text to black/white for maximum contrast
        updates["ColorActiveTitleBar"] = "rgb:00/00/00"
        updates["ColorActiveTitleBarText"] = "rgb:FF/FF/FF"
        updates["ColorNormalTitleBar"] = "rgb:FF/FF/FF"
        updates["ColorNormalTitleBarText"] = "rgb:00/00/00"
        self.model.batch_update(updates)
        self._status("Applied high contrast transformation")

    # -- File operations --

    def _on_new(self, widget):
        if not self._check_unsaved():
            return

        dialog = NewThemeDialog(self)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.model.new_theme(dialog.theme_name, dialog.author)
            self.model.set("Look", dialog.look_style)
            self._status(f"New theme: {dialog.theme_name}")
        dialog.destroy()

    def _on_open(self, widget):
        if not self._check_unsaved():
            return

        dialog = Gtk.FileChooserDialog(
            title="Open Theme File",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )

        filt = Gtk.FileFilter()
        filt.set_name("IceWM Theme (default.theme)")
        filt.add_pattern("default.theme")
        filt.add_pattern("*.theme")
        dialog.add_filter(filt)

        all_filt = Gtk.FileFilter()
        all_filt.set_name("All Files")
        all_filt.add_pattern("*")
        dialog.add_filter(all_filt)

        # Start in common theme directories
        for d in [os.path.expanduser("~/.icewm/themes"),
                  "/usr/share/icewm/themes"]:
            if os.path.isdir(d):
                dialog.set_current_folder(d)
                break

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            try:
                self.model.load_file(filepath)
                self._status(f"Loaded: {filepath}")
            except Exception as e:
                self._show_error(f"Failed to open file:\n{e}")

        dialog.destroy()

    def _on_save(self, widget):
        if self.model.filepath and not self.model.is_temp:
            try:
                self.model.save()
                self._status(f"Saved: {self.model.filepath}")
            except Exception as e:
                self._show_error(f"Save failed:\n{e}")
        else:
            self._on_save_as(widget)

    def _on_save_as(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Save Theme As",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
        )
        dialog.set_do_overwrite_confirmation(True)
        dialog.set_current_name("default.theme")

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filepath = dialog.get_filename()
            try:
                self.model.save(filepath)
                self._status(f"Saved: {filepath}")
            except Exception as e:
                self._show_error(f"Save failed:\n{e}")

        dialog.destroy()

    def _on_import(self, widget):
        if not self._check_unsaved():
            return
        if import_theme_dialog(self, self.model):
            self._status("Theme imported successfully")

    def _on_export(self, widget):
        if export_theme_dialog(self, self.model):
            self._status("Theme exported successfully")

    def _on_apply(self, widget):
        """Copy theme to ~/.icewm/themes/ and signal IceWM to reload."""
        if not self.model.theme_dir:
            self._show_error("Save the theme first.")
            return

        import shutil
        import subprocess

        theme_name = self.model.get("ThemeDescription", "CustomTheme")
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in theme_name)
        if not safe_name:
            safe_name = "unnamed_theme"
        dest_dir = os.path.join(os.path.expanduser("~/.icewm/themes"), safe_name)

        # Save first
        if self.model.dirty:
            self._on_save(widget)

        try:
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            shutil.copytree(self.model.theme_dir, dest_dir)

            # Signal IceWM to reload
            try:
                subprocess.run(["icesh", "restart"], timeout=5, check=False)
            except FileNotFoundError:
                pass  # icesh not available

            self._status(f"Applied theme to {dest_dir}")
        except Exception as e:
            self._show_error(f"Apply failed:\n{e}")

    # -- Undo/Redo --

    def _snapshot_for_undo(self):
        """Save a snapshot of current model values for undo."""
        snapshot = dict(self.model.values)
        if snapshot != self._last_snapshot:
            if self._last_snapshot is not None:
                self._undo_stack.append(self._last_snapshot)
                # Limit stack size
                if len(self._undo_stack) > 50:
                    self._undo_stack.pop(0)
            self._last_snapshot = snapshot
            self._redo_stack.clear()

    def _on_undo(self, widget):
        if not self._undo_stack:
            self._status("Nothing to undo")
            return
        # Save current state to redo
        self._redo_stack.append(dict(self.model.values))
        snapshot = self._undo_stack.pop()
        self._last_snapshot = snapshot
        self.model.restore_snapshot(snapshot)
        self._status("Undo")

    def _on_redo(self, widget):
        if not self._redo_stack:
            self._status("Nothing to redo")
            return
        self._undo_stack.append(dict(self.model.values))
        snapshot = self._redo_stack.pop()
        self._last_snapshot = snapshot
        self.model.restore_snapshot(snapshot)
        self._status("Redo")

    # -- Helpers --

    def _check_unsaved(self):
        """Check for unsaved changes, prompt to save. Returns True to proceed."""
        if not self.model.dirty:
            return True

        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text="Save changes?",
        )
        dialog.format_secondary_text("The current theme has unsaved changes.")
        dialog.add_buttons(
            "Don't Save", Gtk.ResponseType.NO,
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.YES,
        )

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            self._on_save(None)
            return True
        elif response == Gtk.ResponseType.NO:
            return True
        return False  # Cancel

    def _on_delete_event(self, widget, event):
        return not self._check_unsaved()

    def _try_quit(self):
        if self._check_unsaved():
            self.get_application().quit()

    def _on_model_changed(self, key):
        self._update_title()
        # Snapshot for undo on individual changes (not batch/undo/redo)
        if key is not None:
            self._snapshot_for_undo()

    def _update_title(self):
        name = self.model.get("ThemeDescription", "Untitled")
        dirty = " *" if self.model.dirty else ""
        path = f" — {self.model.filepath}" if self.model.filepath else ""
        self.set_title(f"IceSculpt — {name}{dirty}{path}")

    def _status(self, message):
        self._statusbar.pop(self._status_ctx)
        self._statusbar.push(self._status_ctx, message)

    def _show_error(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.run()
        dialog.destroy()

    def _on_key_press(self, widget, event):
        """Handle keyboard shortcuts (Alt+N tab switching only).

        Note: Ctrl+Z/Y undo/redo are handled by menu accelerators,
        not here, to avoid double-firing.
        """
        alt = event.state & Gdk.ModifierType.MOD1_MASK

        # Alt+1..9 switches tabs
        if alt:
            tab_num = event.keyval - Gdk.KEY_1
            if 0 <= tab_num < self._notebook.get_n_pages():
                self._notebook.set_current_page(tab_num)
                return True

        return False
