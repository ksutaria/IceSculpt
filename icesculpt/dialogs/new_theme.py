"""New theme wizard dialog."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..editors.look_editor import LOOK_STYLES


class NewThemeDialog(Gtk.Dialog):
    """Dialog for creating a new theme."""

    def __init__(self, parent=None):
        super().__init__(
            title="New Theme",
            transient_for=parent,
            modal=True,
        )
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK,
        )
        self.set_default_size(400, 250)

        content = self.get_content_area()
        content.set_spacing(8)
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)

        # Theme name
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hbox.pack_start(Gtk.Label(label="Theme Name:"), False, False, 0)
        self._name_entry = Gtk.Entry()
        self._name_entry.set_text("My Theme")
        hbox.pack_start(self._name_entry, True, True, 0)
        content.pack_start(hbox, False, False, 0)

        # Author
        hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hbox2.pack_start(Gtk.Label(label="Author:"), False, False, 0)
        self._author_entry = Gtk.Entry()
        hbox2.pack_start(self._author_entry, True, True, 0)
        content.pack_start(hbox2, False, False, 0)

        # Look style
        hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        hbox3.pack_start(Gtk.Label(label="Look Style:"), False, False, 0)
        self._look_combo = Gtk.ComboBoxText()
        for style in LOOK_STYLES:
            self._look_combo.append_text(style)
        self._look_combo.set_active(1)  # flat
        hbox3.pack_start(self._look_combo, True, True, 0)
        content.pack_start(hbox3, False, False, 0)

        self.show_all()

    @property
    def theme_name(self):
        return self._name_entry.get_text()

    @property
    def author(self):
        return self._author_entry.get_text()

    @property
    def look_style(self):
        return self._look_combo.get_active_text() or "flat"
