"""GtkApplication entry point for IceSculpt."""

import sys
import traceback
import logging

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, Gio, GLib

from .main_window import MainWindow

logger = logging.getLogger(__name__)


def _show_error_dialog(summary, detail=""):
    """Show a modal error dialog.  Works even before the main window exists."""
    dialog = Gtk.MessageDialog(
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=summary,
    )
    if detail:
        dialog.format_secondary_text(detail)
    dialog.run()
    dialog.destroy()


def _install_global_exception_hook():
    """Replace sys.excepthook so unhandled exceptions show a GTK dialog.

    PyGObject catches exceptions inside signal/callback handlers and
    prints them to stderr.  By replacing sys.excepthook we intercept
    those as well, surfacing them in the UI instead of the launch shell.
    """
    original_hook = sys.excepthook

    def _hook(exc_type, exc_value, exc_tb):
        # Ignore KeyboardInterrupt so Ctrl-C still works
        if issubclass(exc_type, KeyboardInterrupt):
            original_hook(exc_type, exc_value, exc_tb)
            return

        # Format the traceback for the dialog
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_tb)
        tb_text = "".join(tb_lines)
        logger.error("Unhandled exception:\n%s", tb_text)

        try:
            _show_error_dialog(
                f"Unexpected error: {exc_value}",
                tb_text[-1500:],  # Trim to avoid a huge dialog
            )
        except Exception:
            # Last resort — if GTK itself is broken, fall back to stderr
            original_hook(exc_type, exc_value, exc_tb)

    sys.excepthook = _hook


class ThemeStudioApp(Gtk.Application):
    """Main GTK application."""

    def __init__(self):
        super().__init__(
            application_id="org.icesculpt.IceSculpt",
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        self._window = None

    def do_activate(self):
        if not self._window:
            self._window = MainWindow(self)
        self._window.present()

    def do_open(self, files, n_files, hint):
        self.do_activate()
        if files:
            filepath = files[0].get_path()
            if filepath:
                try:
                    self._window.model.load_file(filepath)
                except Exception as e:
                    self._window._show_error(f"Failed to load {filepath}:\n{e}")

    def do_startup(self):
        Gtk.Application.do_startup(self)

        # Load custom CSS
        css = b"""
        .monospace {
            font-family: monospace;
            font-size: 9pt;
        }
        """
        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )


def main():
    """Entry point."""
    _install_global_exception_hook()
    app = ThemeStudioApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
