"""Dimension editor — border sizes, title height, corners, scrollbars."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..widgets.param_row import create_int_row


# Dimension settings: (key, label, default, min, max, description)
DIMENSION_KEYS = [
    ("BorderSizeX", "Horizontal Border", 6, 0, 128, "Width of left/right window borders"),
    ("BorderSizeY", "Vertical Border", 6, 0, 128, "Height of top/bottom window borders"),
    ("DlgBorderSizeX", "Dialog Horiz. Border", 2, 0, 128, "Width of dialog borders"),
    ("DlgBorderSizeY", "Dialog Vert. Border", 2, 0, 128, "Height of dialog borders"),
    ("CornerSizeX", "Corner Width", 24, 0, 64, "Width of corner resize handles"),
    ("CornerSizeY", "Corner Height", 24, 0, 64, "Height of corner resize handles"),
    ("TitleBarHeight", "Title Bar Height", 20, 0, 128, "Height of the window title bar"),
    ("TitleBarJustify", "Title Justification", 0, 0, 100, "Title text position: 0=left, 50=center, 100=right"),
    ("TitleBarHorzOffset", "Title Horiz. Offset", 0, -128, 128, "Horizontal offset of title text"),
    ("TitleBarVertOffset", "Title Vert. Offset", 0, -128, 128, "Vertical offset of title text"),
    ("ScrollBarX", "ScrollBar Width", 16, 0, 64, "Width of scrollbars"),
    ("ScrollBarY", "ScrollBar Height", 16, 0, 64, "Height of scrollbar buttons"),
    ("MenuIconSize", "Menu Icon Size", 16, 0, 128, "Size of icons in menus"),
    ("SmallIconSize", "Small Icon Size", 16, 0, 128, "Size of small icons"),
    ("LargeIconSize", "Large Icon Size", 32, 0, 128, "Size of large icons"),
    ("HugeIconSize", "Huge Icon Size", 48, 0, 128, "Size of huge icons"),
]


class DimensionEditor(Gtk.ScrolledWindow):
    """Scrollable panel with all dimension settings."""

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._spin_buttons = {}  # key -> SpinButton

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)

        for key, label, default, min_v, max_v, desc in DIMENSION_KEYS:
            value = model.get_int(key, default)
            row = create_int_row(key, label, value, min_v, max_v, desc,
                                 callback=self._on_value_changed)
            self._spin_buttons[key] = row.editor_widget
            vbox.pack_start(row, False, False, 0)

        self.add(vbox)
        model.connect(self._on_model_changed)

    def _on_model_changed(self, key):
        if key is None:
            for k, default_info in [(d[0], d[2]) for d in DIMENSION_KEYS]:
                if k in self._spin_buttons:
                    self._spin_buttons[k].set_value(self.model.get_int(k, default_info))
        elif key in self._spin_buttons:
            default = next((d[2] for d in DIMENSION_KEYS if d[0] == key), 0)
            self._spin_buttons[key].set_value(self.model.get_int(key, default))

    def _on_value_changed(self, key, value):
        self.model.set(key, value)
