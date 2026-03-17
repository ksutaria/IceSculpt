"""Desktop/wallpaper configuration editor."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..widgets.color_swatch import ColorSwatch
from ..widgets.param_row import create_bool_row
from ..color_utils import hex_to_icewm


class DesktopEditor(Gtk.ScrolledWindow):
    """Editor for wallpaper and desktop background settings."""

    def __init__(self, model):
        super().__init__()
        self.model = model

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)

        # Background color
        color_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        color_box.pack_start(Gtk.Label(label="Background Color"), False, False, 0)
        hex_color = model.get_color_hex("DesktopBackgroundColor", "#2E3440")
        self._bg_swatch = ColorSwatch(hex_color, size=28)
        self._bg_swatch.connect("color-changed", self._on_bg_color_changed)
        color_box.pack_start(self._bg_swatch, False, False, 0)
        vbox.pack_start(color_box, False, False, 0)

        # Wallpaper file
        wp_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        wp_box.pack_start(Gtk.Label(label="Wallpaper Image"), False, False, 0)
        self._wp_entry = Gtk.Entry()
        self._wp_entry.set_text(model.get("DesktopBackgroundImage", ""))
        self._wp_entry.set_hexpand(True)
        self._wp_entry.connect("changed", lambda w: model.set("DesktopBackgroundImage", w.get_text()))
        wp_box.pack_start(self._wp_entry, True, True, 0)

        browse_btn = Gtk.Button(label="Browse...")
        browse_btn.connect("clicked", self._on_browse_wallpaper)
        wp_box.pack_start(browse_btn, False, False, 0)
        vbox.pack_start(wp_box, False, False, 0)

        # Boolean options
        self._bool_keys = [
            ("DesktopBackgroundScaled", "Scale to Fit", "Scale wallpaper to fill screen"),
            ("DesktopBackgroundCenter", "Center", "Center wallpaper on screen"),
            ("DesktopBackgroundMultihead", "Multihead", "Use separate wallpaper per monitor"),
        ]

        self._bool_switches = {}
        for key, label, desc in self._bool_keys:
            val = model.get_bool(key, key == "DesktopBackgroundScaled")
            row = create_bool_row(key, label, val, desc, callback=self._on_value_changed)
            vbox.pack_start(row, False, False, 0)
            self._bool_switches[key] = row.editor_widget

        self.add(vbox)

        model.connect(self._on_model_changed)

    def _on_bg_color_changed(self, swatch, hex_color):
        self.model.set_color_hex("DesktopBackgroundColor", hex_color)

    def _on_browse_wallpaper(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Select Wallpaper",
            action=Gtk.FileChooserAction.OPEN,
            transient_for=self.get_toplevel(),
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
        )

        # Image filter
        filt = Gtk.FileFilter()
        filt.set_name("Images")
        filt.add_mime_type("image/png")
        filt.add_mime_type("image/jpeg")
        filt.add_mime_type("image/xpm")
        filt.add_pattern("*.png")
        filt.add_pattern("*.jpg")
        filt.add_pattern("*.jpeg")
        filt.add_pattern("*.xpm")
        dialog.add_filter(filt)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            path = dialog.get_filename()
            self._wp_entry.set_text(path)
            self.model.set("DesktopBackgroundImage", path)

        dialog.destroy()

    def _on_value_changed(self, key, value):
        self.model.set(key, value)

    def _on_model_changed(self, key):
        if key is not None:
            return
        # Full reload -- update all widgets from the model
        hex_color = self.model.get_color_hex("DesktopBackgroundColor", "#2E3440")
        self._bg_swatch.hex_color = hex_color

        self._wp_entry.set_text(self.model.get("DesktopBackgroundImage", ""))

        for bkey, _label, _desc in self._bool_keys:
            self._bool_switches[bkey].set_active(
                self.model.get_bool(bkey, bkey == "DesktopBackgroundScaled")
            )
