"""GtkDrawingArea wrapper for the live theme preview."""

import logging

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib

from ..preview_renderer import PreviewRenderer

logger = logging.getLogger(__name__)


class PreviewArea(Gtk.Box):
    """Container that includes the preview DrawingArea and state controls."""

    def __init__(self, model):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.model = model
        self.renderer = PreviewRenderer(model)

        # Toolbar for state toggles
        toolbar = Gtk.Toolbar()
        toolbar.get_style_context().add_class("inline-toolbar")
        self.pack_start(toolbar, False, False, 0)

        self.btn_both = Gtk.RadioToolButton()
        self.btn_both.set_icon_name("view-fullscreen-symbolic")
        self.btn_both.set_tooltip_text("Show Desktop (Both Windows)")
        self.btn_both.connect("toggled", self._on_mode_toggled, None)
        toolbar.insert(self.btn_both, -1)

        self.btn_active = Gtk.RadioToolButton.new_from_widget(self.btn_both)
        self.btn_active.set_icon_name("window-new-symbolic")
        self.btn_active.set_tooltip_text("Show Active Window Only")
        self.btn_active.connect("toggled", self._on_mode_toggled, True)
        toolbar.insert(self.btn_active, -1)

        self.btn_inactive = Gtk.RadioToolButton.new_from_widget(self.btn_both)
        self.btn_inactive.set_icon_name("window-close-symbolic") # Using a dim icon
        self.btn_inactive.set_tooltip_text("Show Inactive Window Only")
        self.btn_inactive.connect("toggled", self._on_mode_toggled, False)
        toolbar.insert(self.btn_inactive, -1)

        # Drawing Area
        self.canvas = Gtk.DrawingArea()
        self.canvas.set_size_request(200, 150)
        self.canvas.connect("draw", self._on_draw)
        self.pack_start(self.canvas, True, True, 0)

        # Redraw when model changes
        model.connect(self._on_model_changed)

        self._redraw_pending = False

    def _on_mode_toggled(self, btn, state):
        self.renderer.force_active = state
        self.canvas.queue_draw()

    def _on_draw(self, widget, cr):
        w = self.canvas.get_allocated_width()
        h = self.canvas.get_allocated_height()

        # Clip to allocation
        cr.rectangle(0, 0, w, h)
        cr.clip()

        try:
            self.renderer.render(cr, w, h)
        except Exception as e:
            logger.error("Preview render error: %s", e, exc_info=True)
            # Draw a fallback
            cr.set_source_rgb(0.3, 0.3, 0.3)
            cr.rectangle(0, 0, w, h)
            cr.fill()
        return False

    def _on_model_changed(self, key):
        """Schedule a redraw (coalesce rapid changes)."""
        if not self._redraw_pending:
            self._redraw_pending = True
            GLib.idle_add(self._do_redraw)

    def _do_redraw(self):
        self._redraw_pending = False
        self.canvas.queue_draw()
        return False
