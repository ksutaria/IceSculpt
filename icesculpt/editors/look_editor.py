"""Look style selector and behavioral toggles."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..widgets.param_row import create_choice_row, create_bool_row, create_string_row


LOOK_STYLES = ["pixmap", "flat", "motif", "win95", "gtk", "nice", "metal2", "warp3", "warp4"]

BOOL_KEYS = [
    ("RolloverButtonsSupported", "Rollover Buttons", "Enable button hover effects"),
    ("TaskBarClockLeds", "Clock LED Digits", "Use LED-style clock display"),
    ("TrayDrawBevel", "Tray Bevel", "Draw bevel on tray icons"),
    ("ShowMenuButtonIcon", "Menu Button Icon", "Show icon on the system menu button"),
    ("TitleBarCentered", "Centered Title", "Center title bar text"),
    ("TitleBarJoinLeft", "Join Title Left", "Join title bar with left frame"),
    ("TitleBarJoinRight", "Join Title Right", "Join title bar with right frame"),
]


class LookEditor(Gtk.ScrolledWindow):
    """Editor for Look style and behavioral toggles."""

    def __init__(self, model):
        super().__init__()
        self.model = model

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)

        # Look style selector
        frame_look = Gtk.Frame(label="Look Style")
        look_val = model.get("Look", "flat")
        look_row = create_choice_row("Look", "Rendering Style", look_val, LOOK_STYLES,
                                     "Controls how windows, buttons, and borders are drawn",
                                     callback=self._on_value_changed)
        look_row.set_margin_start(8)
        look_row.set_margin_end(8)
        look_row.set_margin_top(8)
        look_row.set_margin_bottom(8)
        frame_look.add(look_row)
        vbox.pack_start(frame_look, False, False, 0)
        self._look_combo = look_row.editor_widget

        # Button layout
        frame_btns = Gtk.Frame(label="Button Layout")
        btn_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        btn_box.set_margin_start(8)
        btn_box.set_margin_end(8)
        btn_box.set_margin_top(8)
        btn_box.set_margin_bottom(8)

        left_val = model.get("TitleButtonsLeft", "s")
        left_row = create_string_row("TitleButtonsLeft", "Left Buttons", left_val,
                                     "s=sysmenu, x=close, m=maximize, i=minimize, h=hide, r=rollup, d=depth",
                                     callback=self._on_value_changed)
        btn_box.pack_start(left_row, False, False, 0)

        right_val = model.get("TitleButtonsRight", "xmir")
        right_row = create_string_row("TitleButtonsRight", "Right Buttons", right_val,
                                      "Buttons on right side of title bar",
                                      callback=self._on_value_changed)
        btn_box.pack_start(right_row, False, False, 0)

        sup_val = model.get("TitleButtonsSupported", "xmis")
        sup_row = create_string_row("TitleButtonsSupported", "Supported Buttons", sup_val,
                                    "Which buttons the theme supports",
                                    callback=self._on_value_changed)
        btn_box.pack_start(sup_row, False, False, 0)

        frame_btns.add(btn_box)
        vbox.pack_start(frame_btns, False, False, 0)

        self._string_entries = {
            "TitleButtonsLeft": left_row.editor_widget,
            "TitleButtonsRight": right_row.editor_widget,
            "TitleButtonsSupported": sup_row.editor_widget,
        }

        # Behavioral toggles
        frame_beh = Gtk.Frame(label="Behavior")
        beh_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        beh_box.set_margin_start(8)
        beh_box.set_margin_end(8)
        beh_box.set_margin_top(8)
        beh_box.set_margin_bottom(8)

        self._bool_switches = {}
        for key, label, desc in BOOL_KEYS:
            val = model.get_bool(key, False)
            row = create_bool_row(key, label, val, desc, callback=self._on_value_changed)
            beh_box.pack_start(row, False, False, 0)
            self._bool_switches[key] = row.editor_widget

        frame_beh.add(beh_box)
        vbox.pack_start(frame_beh, False, False, 0)

        self.add(vbox)

        model.connect(self._on_model_changed)

    def _on_value_changed(self, key, value):
        self.model.set(key, value)

    def _on_model_changed(self, key):
        if key is not None:
            return
        # Full reload -- update all widgets from the model
        look_val = self.model.get("Look", "flat")
        try:
            idx = LOOK_STYLES.index(look_val)
        except ValueError:
            idx = 0
        self._look_combo.set_active(idx)

        for skey, default in [("TitleButtonsLeft", "s"),
                              ("TitleButtonsRight", "xmir"),
                              ("TitleButtonsSupported", "xmis")]:
            self._string_entries[skey].set_text(self.model.get(skey, default))

        for bkey, _label, _desc in BOOL_KEYS:
            self._bool_switches[bkey].set_active(self.model.get_bool(bkey, False))
