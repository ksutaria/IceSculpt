"""Zoomable pixel editor grid for editing small XPM pixmaps."""

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GObject

from ..xpm_codec import XpmImage
from ..color_utils import hex_to_rgba


class PixmapCanvas(Gtk.DrawingArea):
    """A zoomed grid for hand-editing small pixmaps.

    Supports:
      - Pencil tool (click/drag to set pixels)
      - Per-canvas undo/redo
      - Zoom in/out
    """

    __gsignals__ = {
        "pixel-changed": (GObject.SignalFlags.RUN_FIRST, None, (int, int)),
        "image-modified": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, image=None, zoom=12):
        super().__init__()
        self._image = image or XpmImage(16, 16, 1)
        self._zoom = zoom
        self._current_char = None  # Current drawing character
        self._drawing = False
        self._undo_stack = []
        self._redo_stack = []
        self._max_undo = 50

        self._update_size()

        self.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.connect("draw", self._on_draw)
        self.connect("button-press-event", self._on_button_press)
        self.connect("button-release-event", self._on_button_release)
        self.connect("motion-notify-event", self._on_motion)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, img):
        self._image = img
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._update_size()
        self.queue_draw()

    @property
    def zoom(self):
        return self._zoom

    @zoom.setter
    def zoom(self, value):
        self._zoom = max(1, min(64, value))
        self._update_size()
        self.queue_draw()

    def set_draw_color(self, char):
        """Set the character used when drawing pixels."""
        self._current_char = char

    def undo(self):
        if self._undo_stack:
            state = self._undo_stack.pop()
            self._redo_stack.append(list(self._image.pixels))
            self._image.pixels = state
            self.queue_draw()
            self.emit("image-modified")
            return True
        return False

    def redo(self):
        if self._redo_stack:
            state = self._redo_stack.pop()
            self._undo_stack.append(list(self._image.pixels))
            self._image.pixels = state
            self.queue_draw()
            self.emit("image-modified")
            return True
        return False

    def _update_size(self):
        w = self._image.width * self._zoom + 1
        h = self._image.height * self._zoom + 1
        self.set_size_request(w, h)

    def _on_draw(self, widget, cr):
        try:
            self._do_draw(cr)
        except Exception:
            # Draw a visible error indicator instead of crashing silently
            cr.set_source_rgb(0.8, 0.2, 0.2)
            cr.rectangle(0, 0, self.get_allocated_width(), self.get_allocated_height())
            cr.fill()
            cr.set_source_rgb(1, 1, 1)
            cr.select_font_face("Sans", 0, 0)
            cr.set_font_size(11)
            cr.move_to(4, 16)
            cr.show_text("Draw error — image may be invalid")
        return False

    def _do_draw(self, cr):
        """Actual draw logic, separated so _on_draw can catch errors."""
        img = self._image
        z = self._zoom

        # Draw pixels
        for y in range(img.height):
            for x in range(img.width):
                color = img.get_color_at(x, y)
                if color is None:
                    # Transparency checkerboard (two half-cell rectangles)
                    sq = z // 2 or 1
                    cx, cy = x * z, y * z
                    cr.set_source_rgb(0.9, 0.9, 0.9)
                    cr.rectangle(cx, cy, z, z)
                    cr.fill()
                    cr.set_source_rgb(0.7, 0.7, 0.7)
                    for sy in range(0, z, sq * 2):
                        for sx in range(0, z, sq * 2):
                            cr.rectangle(cx + sx + sq, cy + sy, sq, sq)
                            cr.rectangle(cx + sx, cy + sy + sq, sq, sq)
                    cr.fill()
                else:
                    r, g, b, _ = hex_to_rgba(color)
                    cr.set_source_rgb(r, g, b)
                    cr.rectangle(x * z, y * z, z, z)
                    cr.fill()

        # Draw grid lines
        cr.set_source_rgba(0, 0, 0, 0.2)
        cr.set_line_width(0.5)
        for x in range(img.width + 1):
            cr.move_to(x * z + 0.5, 0)
            cr.line_to(x * z + 0.5, img.height * z)
        for y in range(img.height + 1):
            cr.move_to(0, y * z + 0.5)
            cr.line_to(img.width * z, y * z + 0.5)
        cr.stroke()

    def _pixel_at(self, event_x, event_y):
        """Convert event coordinates to pixel coordinates."""
        x = int(event_x) // self._zoom
        y = int(event_y) // self._zoom
        if 0 <= x < self._image.width and 0 <= y < self._image.height:
            return x, y
        return None

    def _on_button_press(self, widget, event):
        if event.button == 1 and self._current_char:
            # Save undo state (bounded)
            self._undo_stack.append(list(self._image.pixels))
            if len(self._undo_stack) > self._max_undo:
                self._undo_stack.pop(0)
            self._redo_stack.clear()
            self._drawing = True
            pos = self._pixel_at(event.x, event.y)
            if pos:
                self._image.set_pixel(pos[0], pos[1], self._current_char)
                self.queue_draw()
                self.emit("pixel-changed", pos[0], pos[1])

    def _on_button_release(self, widget, event):
        if event.button == 1 and self._drawing:
            self._drawing = False
            self.emit("image-modified")

    def _on_motion(self, widget, event):
        if self._drawing and self._current_char:
            pos = self._pixel_at(event.x, event.y)
            if pos:
                self._image.set_pixel(pos[0], pos[1], self._current_char)
                self.queue_draw()
                self.emit("pixel-changed", pos[0], pos[1])

