"""Icon management and creation editor."""

import os

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Pango


class IconEditor(Gtk.Box):
    """Icon browser for theme icons directory."""

    def __init__(self, model):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.model = model

        self.set_margin_start(8)
        self.set_margin_end(8)
        self.set_margin_top(8)
        self.set_margin_bottom(8)

        # Info
        label = Gtk.Label()
        label.set_markup("Icons are stored in the theme's <b>icons/</b> subdirectory at 16x16, 32x32, and 48x48 sizes.")
        label.set_xalign(0)
        label.set_line_wrap(True)
        self.pack_start(label, False, False, 0)

        # Icon grid
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self._flowbox = Gtk.FlowBox()
        self._flowbox.set_valign(Gtk.Align.START)
        self._flowbox.set_max_children_per_line(10)
        self._flowbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        scroll.add(self._flowbox)
        self.pack_start(scroll, True, True, 0)

        # Toolbar
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        refresh_btn = Gtk.Button(label="Refresh")
        refresh_btn.connect("clicked", lambda w: self._load_icons())
        toolbar.pack_start(refresh_btn, False, False, 0)

        import_btn = Gtk.Button(label="Import Icon...")
        import_btn.connect("clicked", self._on_import)
        toolbar.pack_start(import_btn, False, False, 0)

        self.pack_start(toolbar, False, False, 0)

        self._load_icons()

    def _load_icons(self):
        # Clear existing (destroy to free pixbufs)
        for child in self._flowbox.get_children():
            child.destroy()

        theme_dir = self.model.theme_dir
        if not theme_dir:
            return

        icons_dir = os.path.join(theme_dir, "icons")
        if not os.path.isdir(icons_dir):
            return

        for size_dir in sorted(os.listdir(icons_dir)):
            size_path = os.path.join(icons_dir, size_dir)
            if not os.path.isdir(size_path):
                continue
            for f in sorted(os.listdir(size_path)):
                filepath = os.path.join(size_path, f)
                if not f.lower().endswith((".xpm", ".png")):
                    continue
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(filepath, 48, 48, True)
                    img = Gtk.Image.new_from_pixbuf(pixbuf)
                    box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
                    box.pack_start(img, False, False, 0)
                    lbl = Gtk.Label(label=f"{size_dir}/{f}")
                    lbl.set_ellipsize(Pango.EllipsizeMode.END)
                    lbl.set_max_width_chars(12)
                    box.pack_start(lbl, False, False, 0)
                    self._flowbox.add(box)
                except Exception:
                    pass

        self._flowbox.show_all()

    def _on_import(self, widget):
        theme_dir = self.model.theme_dir
        if not theme_dir:
            self._show_error("Save the theme first to set a directory.")
            return

        dialog = Gtk.FileChooserDialog(
            title="Import Icon",
            action=Gtk.FileChooserAction.OPEN,
            transient_for=self.get_toplevel(),
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )

        filt = Gtk.FileFilter()
        filt.set_name("Images")
        filt.add_pattern("*.png")
        filt.add_pattern("*.xpm")
        dialog.add_filter(filt)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            src = dialog.get_filename()
            try:
                import shutil
                dest_dir = os.path.join(theme_dir, "icons", "48x48")
                os.makedirs(dest_dir, exist_ok=True)
                shutil.copy2(src, dest_dir)
                self._load_icons()
            except Exception as e:
                self._show_error(f"Failed to import icon:\n{e}")

        dialog.destroy()

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
