"""Taskbar-specific settings editor."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..widgets.param_row import create_int_row


TASKBAR_KEYS = [
    ("TaskBarCPUSamples", "CPU Samples", 20, 2, 1000, "Number of CPU samples in graph"),
    ("TaskBarMEMSamples", "Memory Samples", 20, 2, 1000, "Number of memory samples in graph"),
    ("TaskBarNetSamples", "Network Samples", 20, 2, 1000, "Number of network samples in graph"),
    ("TaskBarGraphHeight", "Graph Height", 20, 8, 256, "Height of monitor graphs in pixels"),
]


class TaskbarEditor(Gtk.ScrolledWindow):
    """Editor for taskbar-specific settings."""

    def __init__(self, model):
        super().__init__()
        self.model = model

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)

        frame = Gtk.Frame(label="Monitor Applets")
        fbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        fbox.set_margin_start(8)
        fbox.set_margin_end(8)
        fbox.set_margin_top(8)
        fbox.set_margin_bottom(8)

        self._spin_buttons = {}
        for key, label, default, min_v, max_v, desc in TASKBAR_KEYS:
            value = model.get_int(key, default)
            row = create_int_row(key, label, value, min_v, max_v, desc,
                                 callback=self._on_value_changed)
            fbox.pack_start(row, False, False, 0)
            self._spin_buttons[key] = row.editor_widget

        frame.add(fbox)
        vbox.pack_start(frame, False, False, 0)

        self.add(vbox)

        model.connect(self._on_model_changed)

    def _on_value_changed(self, key, value):
        self.model.set(key, value)

    def _on_model_changed(self, key):
        if key is not None:
            return
        # Full reload -- update all widgets from the model
        for tkey, _label, default, _min_v, _max_v, _desc in TASKBAR_KEYS:
            self._spin_buttons[tkey].set_value(self.model.get_int(tkey, default))
