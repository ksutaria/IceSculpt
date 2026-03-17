"""About dialog."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from .. import __version__


def show_about_dialog(parent):
    """Show the About dialog."""
    dialog = Gtk.AboutDialog(transient_for=parent, modal=True)
    dialog.set_program_name("IceSculpt")
    dialog.set_version(__version__)
    dialog.set_comments("Visual theme editor for IceWM window manager")
    dialog.set_license_type(Gtk.License.LGPL_2_1)
    dialog.set_website_label("IceSculpt on GitHub")
    dialog.set_copyright("IceSculpt Contributors")
    dialog.run()
    dialog.destroy()
