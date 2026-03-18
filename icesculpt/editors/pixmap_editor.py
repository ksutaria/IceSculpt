"""Pixmap browser and generator UI."""

import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..xpm_codec import read_xpm_file, write_xpm_file
from ..pixmap_generator import generate_all_buttons, generate_all_frames
from ..widgets.pixmap_canvas import PixmapCanvas


class PixmapEditor(Gtk.Box):
    """Pixmap browser and editor panel.

    Shows all pixmap files in the theme directory organized by category,
    with thumbnail previews and a pixel editor for selected pixmaps.
    """

    def __init__(self, model):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.model = model
        self._current_image = None
        self._current_path = None

        # Top toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        toolbar.set_margin_start(8)
        toolbar.set_margin_end(8)
        toolbar.set_margin_top(8)

        gen_btn = Gtk.Button(label="Generate Buttons")
        gen_btn.connect("clicked", self._on_generate_buttons)
        toolbar.pack_start(gen_btn, False, False, 0)

        gen_frames_btn = Gtk.Button(label="Generate Frames")
        gen_frames_btn.connect("clicked", self._on_generate_frames)
        toolbar.pack_start(gen_frames_btn, False, False, 0)

        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", self._on_refresh)
        toolbar.pack_start(refresh_btn, False, False, 0)

        recolor_btn = Gtk.Button(label="Recolor All")
        recolor_btn.set_tooltip_text("Apply global hue/sat/lum shift to all XPM assets")
        recolor_btn.connect("clicked", self._on_recolor_all_clicked)
        toolbar.pack_start(recolor_btn, False, False, 0)

        self.pack_start(toolbar, False, False, 0)

        # Main content: file list + pixel editor
        paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        # File list (left)
        scroll_list = Gtk.ScrolledWindow()
        scroll_list.set_size_request(200, -1)
        scroll_list.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self._store = Gtk.ListStore(str, str)  # filename, full path
        self._tree = Gtk.TreeView(model=self._store)
        renderer = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Pixmaps", renderer, text=0)
        self._tree.append_column(col)
        self._tree.get_selection().connect("changed", self._on_selection_changed)
        scroll_list.add(self._tree)
        paned.pack1(scroll_list, resize=False, shrink=False)

        # Pixel editor (right)
        editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        editor_box.set_margin_start(4)

        self._info_label = Gtk.Label(label="Select a pixmap to edit")
        self._info_label.set_xalign(0)
        editor_box.pack_start(self._info_label, False, False, 0)

        # Canvas in a scrolled window
        canvas_scroll = Gtk.ScrolledWindow()
        canvas_scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self._canvas = PixmapCanvas(zoom=16)
        canvas_scroll.add(self._canvas)
        editor_box.pack_start(canvas_scroll, True, True, 0)

        # Zoom controls
        zoom_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        zoom_out = Gtk.Button(label="-")
        zoom_out.connect("clicked", lambda w: self._set_zoom(self._canvas.zoom - 2))
        zoom_box.pack_start(zoom_out, False, False, 0)

        self._zoom_label = Gtk.Label(label="16x")
        zoom_box.pack_start(self._zoom_label, False, False, 0)

        zoom_in = Gtk.Button(label="+")
        zoom_in.connect("clicked", lambda w: self._set_zoom(self._canvas.zoom + 2))
        zoom_box.pack_start(zoom_in, False, False, 0)

        save_btn = Gtk.Button(label="Save Pixmap")
        save_btn.connect("clicked", self._on_save_pixmap)
        zoom_box.pack_end(save_btn, False, False, 0)

        editor_box.pack_start(zoom_box, False, False, 4)

        paned.pack2(editor_box, resize=True, shrink=False)
        paned.set_position(200)

        self.pack_start(paned, True, True, 0)

        # Populate file list
        self._refresh_file_list()

    def _refresh_file_list(self):
        self._store.clear()
        theme_dir = self.model.theme_dir
        if not theme_dir or not os.path.isdir(theme_dir):
            return

        xpm_files = []
        for f in os.listdir(theme_dir):
            if f.lower().endswith((".xpm", ".png")):
                xpm_files.append(f)

        for f in sorted(xpm_files):
            self._store.append([f, os.path.join(theme_dir, f)])

    def _on_selection_changed(self, selection):
        model, tree_iter = selection.get_selected()
        if tree_iter is None:
            return

        filename = model[tree_iter][0]
        filepath = model[tree_iter][1]

        if filepath.lower().endswith(".xpm"):
            try:
                img = read_xpm_file(filepath)
                self._current_image = img
                self._current_path = filepath
                self._canvas.image = img
                self._info_label.set_text(f"{filename} — {img.width}x{img.height}, {len(img.colors)} colors")

                # Set draw color to first non-transparent color
                for char, color in img.colors.items():
                    if color and color.lower() != "none":
                        self._canvas.set_draw_color(char)
                        break
            except Exception as e:
                self._info_label.set_text(f"Error: {e}")
        else:
            self._info_label.set_text(f"{filename} (PNG — view only)")

    def _on_save_pixmap(self, widget):
        if self._current_image and self._current_path:
            try:
                write_xpm_file(self._current_path, self._current_image)
                self._info_label.set_text(f"Saved: {os.path.basename(self._current_path)}")
            except Exception as e:
                self._info_label.set_text(f"Save error: {e}")

    def _set_zoom(self, value):
        self._canvas.zoom = max(2, min(48, value))
        self._zoom_label.set_text(f"{self._canvas.zoom}x")

    def _on_refresh(self, widget):
        self._refresh_file_list()

    def _on_recolor_all_clicked(self, widget):
        theme_dir = self.model.theme_dir
        if not theme_dir:
            self._show_error("Save the theme first.")
            return

        dialog = Gtk.Dialog(title="Recolor All Pixmaps", parent=self.get_toplevel(), flags=0)
        dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_APPLY, Gtk.ResponseType.OK)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_start(10)
        vbox.set_margin_end(10)
        vbox.set_margin_top(10)

        # Hue slider
        vbox.pack_start(Gtk.Label(label="Hue Shift", xalign=0), False, False, 0)
        hue_adj = Gtk.Adjustment(value=0, lower=0, upper=1, step_increment=0.01)
        hue_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=hue_adj)
        vbox.pack_start(hue_scale, False, False, 0)

        # Saturation slider
        vbox.pack_start(Gtk.Label(label="Saturation Factor", xalign=0), False, False, 0)
        sat_adj = Gtk.Adjustment(value=1, lower=0, upper=3, step_increment=0.1)
        sat_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=sat_adj)
        vbox.pack_start(sat_scale, False, False, 0)

        # Luminance slider
        vbox.pack_start(Gtk.Label(label="Luminance Factor", xalign=0), False, False, 0)
        lum_adj = Gtk.Adjustment(value=1, lower=0, upper=3, step_increment=0.1)
        lum_scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=lum_adj)
        vbox.pack_start(lum_scale, False, False, 0)

        dialog.get_content_area().add(vbox)
        dialog.show_all()

        if dialog.run() == Gtk.ResponseType.OK:
            from ..pixmap_generator import recolor_all_pixmaps
            recolored = recolor_all_pixmaps(
                theme_dir,
                hue_adj.get_value(),
                sat_adj.get_value(),
                lum_adj.get_value()
            )
            self._info_label.set_text(f"Recolored {len(recolored)} pixmaps.")
            self._refresh_file_list()

        dialog.destroy()

    def _on_generate_buttons(self, widget):
        theme_dir = self.model.theme_dir
        if not theme_dir:
            self._show_error("Save the theme first to set a directory.")
            return

        try:
            size = max(8, self.model.get_int("TitleBarHeight", 20) - 4)
            buttons = generate_all_buttons(size, self.model)
            for filename, img in buttons.items():
                write_xpm_file(os.path.join(theme_dir, filename), img)

            self._refresh_file_list()
            self._info_label.set_text(f"Generated {len(buttons)} button pixmaps")
        except Exception as e:
            self._show_error(f"Failed to generate buttons:\n{e}")

    def _on_generate_frames(self, widget):
        theme_dir = self.model.theme_dir
        if not theme_dir:
            self._show_error("Save the theme first to set a directory.")
            return

        try:
            bx = max(1, self.model.get_int("BorderSizeX", 6))
            by = max(1, self.model.get_int("BorderSizeY", 6))
            cx = max(1, self.model.get_int("CornerSizeX", 24))
            cy = max(1, self.model.get_int("CornerSizeY", 24))
            frames = generate_all_frames(bx, by, cx, cy, self.model)
            for filename, img in frames.items():
                write_xpm_file(os.path.join(theme_dir, filename), img)

            self._refresh_file_list()
            self._info_label.set_text(f"Generated {len(frames)} frame pixmaps")
        except Exception as e:
            self._show_error(f"Failed to generate frames:\n{e}")

    def _show_error(self, message):
        toplevel = self.get_toplevel()
        parent = toplevel if isinstance(toplevel, Gtk.Window) else None
        dialog = Gtk.MessageDialog(
            transient_for=parent,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.run()
        dialog.destroy()
