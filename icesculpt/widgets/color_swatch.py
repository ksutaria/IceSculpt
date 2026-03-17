"""Clickable color swatch widget that opens a GtkColorChooserDialog."""

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GObject

from ..color_utils import hex_to_rgba


class ColorSwatch(Gtk.DrawingArea):
    """A small colored rectangle that opens a color picker on click.

    Signals:
        color-changed: Emitted when the user picks a new color.
                       Handler receives (widget, hex_color_string).
    """

    __gsignals__ = {
        "color-changed": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self, hex_color="#808080", size=24):
        super().__init__()
        self._hex = hex_color
        self._size = size
        self.set_size_request(size, size)
        self.set_can_focus(True)
        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.KEY_PRESS_MASK
        )
        self.connect("draw", self._on_draw)
        self.connect("button-press-event", self._on_click)
        self.connect("key-press-event", self._on_key_press)
        self.set_tooltip_text(hex_color)

    @property
    def hex_color(self):
        return self._hex

    @hex_color.setter
    def hex_color(self, value):
        if value != self._hex:
            self._hex = value
            self.set_tooltip_text(value)
            self.queue_draw()

    def _on_draw(self, widget, cr):
        w = self.get_allocated_width()
        h = self.get_allocated_height()

        # Draw checkerboard for transparency indication
        cr.set_source_rgb(0.8, 0.8, 0.8)
        cr.rectangle(0, 0, w, h)
        cr.fill()
        cr.set_source_rgb(0.6, 0.6, 0.6)
        sq = 4
        for row in range(0, h, sq):
            for col in range(0, w, sq):
                if (row // sq + col // sq) % 2:
                    cr.rectangle(col, row, sq, sq)
                    cr.fill()

        # Draw the color
        r, g, b, _ = hex_to_rgba(self._hex)
        cr.set_source_rgb(r, g, b)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        # Draw border
        if self.has_focus():
            cr.set_source_rgb(0.2, 0.5, 1.0)
            cr.set_line_width(2)
        else:
            cr.set_source_rgb(0.3, 0.3, 0.3)
            cr.set_line_width(1)
        cr.rectangle(0.5, 0.5, w - 1, h - 1)
        cr.stroke()

        return False

    def _on_click(self, widget, event):
        if event.button == 1:
            self._open_color_dialog()

    def _on_key_press(self, widget, event):
        if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
            self._open_color_dialog()
            return True
        return False

    def _open_color_dialog(self):
        toplevel = self.get_toplevel()
        parent = toplevel if isinstance(toplevel, Gtk.Window) else None
        dialog = Gtk.ColorChooserDialog(
            title="Choose Color",
            transient_for=parent,
        )
        dialog.set_use_alpha(False)

        # Set current color
        rgba = Gdk.RGBA()
        if not rgba.parse(self._hex):
            rgba.parse("#808080")
        dialog.set_rgba(rgba)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            rgba = dialog.get_rgba()
            ri = max(0, min(255, int(round(rgba.red * 255))))
            gi_ = max(0, min(255, int(round(rgba.green * 255))))
            bi = max(0, min(255, int(round(rgba.blue * 255))))
            new_hex = f"#{ri:02X}{gi_:02X}{bi:02X}"
            self._hex = new_hex
            self.set_tooltip_text(new_hex)
            self.queue_draw()
            self.emit("color-changed", new_hex)

        dialog.destroy()

