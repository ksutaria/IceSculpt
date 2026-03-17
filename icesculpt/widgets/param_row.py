"""Reusable key=value editor row widget."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject


class ParamRow(Gtk.Box):
    """A labeled row with a widget for editing a single theme parameter.

    Layout: [Label] [Widget] in a horizontal box.
    """

    __gsignals__ = {
        "value-changed": (GObject.SignalFlags.RUN_FIRST, None, (str, str)),
    }

    def __init__(self, key, label_text, widget, description=""):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.key = key

        label = Gtk.Label(label=label_text)
        label.set_xalign(0)
        label.set_size_request(200, -1)
        if description:
            label.set_tooltip_text(description)

        self.pack_start(label, False, False, 0)
        self.pack_start(widget, True, True, 0)
        self.editor_widget = widget


def create_int_row(key, label, value, min_val=0, max_val=128, description="", callback=None):
    """Create a ParamRow with a spin button for integer values."""
    adj = Gtk.Adjustment(value=value, lower=min_val, upper=max_val, step_increment=1, page_increment=5)
    spin = Gtk.SpinButton(adjustment=adj, climb_rate=1, digits=0)
    spin.set_value(value)

    row = ParamRow(key, label, spin, description)

    if callback:
        spin.connect("value-changed", lambda w: callback(key, str(int(w.get_value()))))

    return row


def create_bool_row(key, label, value, description="", callback=None):
    """Create a ParamRow with a switch for boolean values."""
    switch = Gtk.Switch()
    switch.set_active(value)
    switch.set_halign(Gtk.Align.START)

    row = ParamRow(key, label, switch, description)

    if callback:
        switch.connect("notify::active", lambda w, p: callback(key, "1" if w.get_active() else "0"))

    return row


def create_string_row(key, label, value, description="", callback=None):
    """Create a ParamRow with a text entry for string values."""
    entry = Gtk.Entry()
    entry.set_text(value)

    row = ParamRow(key, label, entry, description)

    if callback:
        entry.connect("changed", lambda w: callback(key, w.get_text()))

    return row


def create_choice_row(key, label, value, choices, description="", callback=None):
    """Create a ParamRow with a combo box for enum values."""
    combo = Gtk.ComboBoxText()
    active_idx = 0
    for i, choice in enumerate(choices):
        combo.append_text(choice)
        if choice == value:
            active_idx = i
    combo.set_active(active_idx)

    row = ParamRow(key, label, combo, description)

    if callback:
        combo.connect("changed", lambda w: callback(key, w.get_active_text() or ""))

    return row
