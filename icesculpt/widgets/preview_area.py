"""GtkDrawingArea wrapper for the live theme preview."""

import logging

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from ..preview_renderer import PreviewRenderer

logger = logging.getLogger(__name__)


class PreviewArea(Gtk.DrawingArea):
    """Drawing area that renders the live theme preview.

    Connects to the ThemeModel and redraws when values change.
    """

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.renderer = PreviewRenderer(model)

        self.set_size_request(200, 150)
        self.connect("draw", self._on_draw)

        # Redraw when model changes
        model.connect(self._on_model_changed)

        self._redraw_pending = False

    def _on_draw(self, widget, cr):
        w = self.get_allocated_width()
        h = self.get_allocated_height()

        # Clip to allocation
        cr.rectangle(0, 0, w, h)
        cr.clip()

        try:
            self.renderer.render(cr, w, h)
        except Exception as e:
            logger.error("Preview render error: %s", e, exc_info=True)
            # Draw a fallback instead of showing nothing
            cr.set_source_rgb(0.3, 0.3, 0.3)
            cr.rectangle(0, 0, w, h)
            cr.fill()
            cr.set_source_rgb(0.8, 0.8, 0.8)
            cr.select_font_face("Sans", 0, 0)
            cr.set_font_size(12)
            cr.move_to(10, h / 2)
            cr.show_text(f"Preview error: {e}")
        return False

    def _on_model_changed(self, key):
        """Schedule a redraw (coalesce rapid changes)."""
        if not self._redraw_pending:
            self._redraw_pending = True
            GLib.idle_add(self._do_redraw)

    def _do_redraw(self):
        self._redraw_pending = False
        self.queue_draw()
        return False  # Don't repeat
