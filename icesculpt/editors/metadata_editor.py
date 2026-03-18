"""Metadata editor — ThemeDescription, ThemeAuthor, License fields."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib


class MetadataEditor(Gtk.Box):
    """Editor panel for theme metadata fields."""

    def __init__(self, model):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.model = model

        self.set_margin_start(12)
        self.set_margin_end(12)
        self.set_margin_top(12)
        self.set_margin_bottom(12)

        self._entries = {}

        fields = [
            ("ThemeDescription", "Theme Name / Description"),
            ("ThemeAuthor", "Author"),
            ("License", "License"),
        ]

        for key, label_text in fields:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

            label = Gtk.Label(label=label_text)
            label.set_xalign(0)
            label.set_size_request(180, -1)
            hbox.pack_start(label, False, False, 0)

            entry = Gtk.Entry()
            entry.set_text(model.get(key, ""))
            entry.connect("changed", self._on_entry_changed, key)
            hbox.pack_start(entry, True, True, 0)

            self._entries[key] = entry
            self.pack_start(hbox, False, False, 0)

        # Info label
        info = Gtk.Label()
        info.set_markup("<small>These fields are stored in the theme file header.</small>")
        info.set_xalign(0)
        info.set_margin_top(8)
        self.pack_start(info, False, False, 0)

        # File info
        self._file_label = Gtk.Label()
        self._file_label.set_xalign(0)
        self._file_label.set_margin_top(16)
        self._update_file_label()
        self.pack_start(self._file_label, False, False, 0)

        model.connect(self._on_model_changed)

    def _on_entry_changed(self, entry, key):
        self.model.set(key, entry.get_text())

    def _on_model_changed(self, key):
        if key is None or key in self._entries:
            # Full reload or specific key change
            for k, entry in self._entries.items():
                if key is not None and k != key:
                    continue
                val = self.model.get(k, "")
                if entry.get_text() != val:
                    entry.set_text(val)
            self._update_file_label()

    def _update_file_label(self):
        path = self.model.filepath or "(unsaved)"
        escaped = GLib.markup_escape_text(path)
        self._file_label.set_markup(f"<small><b>File:</b> {escaped}</small>")
