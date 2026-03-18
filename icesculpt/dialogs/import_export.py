"""Theme import/export dialogs — tarball handling."""

import os
import tarfile
import tempfile
import shutil

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


def import_theme_dialog(parent, model):
    """Show a dialog to import a theme from a .tar.gz archive.

    Args:
        parent: Parent window.
        model: ThemeModel instance.

    Returns:
        True if a theme was successfully imported.
    """
    dialog = Gtk.FileChooserDialog(
        title="Import Theme Archive",
        transient_for=parent,
        action=Gtk.FileChooserAction.OPEN,
    )
    dialog.add_buttons(
        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_OPEN, Gtk.ResponseType.OK,
    )

    filt = Gtk.FileFilter()
    filt.set_name("Theme Archives (*.tar.gz, *.tgz)")
    filt.add_pattern("*.tar.gz")
    filt.add_pattern("*.tgz")
    dialog.add_filter(filt)

    response = dialog.run()
    result = False

    if response == Gtk.ResponseType.OK:
        archive_path = dialog.get_filename()
        result = _do_import(parent, model, archive_path)

    dialog.destroy()
    return result


def _safe_tar_members(tar, dest_dir):
    """Yield tar members that are safe to extract (no path traversal, no links)."""
    dest_real = os.path.realpath(dest_dir)
    for member in tar.getmembers():
        # Skip symlinks and hardlinks
        if member.issym() or member.islnk():
            continue
        # Resolve the would-be extracted path and ensure it stays under dest_dir
        member_path = os.path.realpath(os.path.join(dest_dir, member.name))
        if not member_path.startswith(dest_real + os.sep) and member_path != dest_real:
            continue
        yield member


def _do_import(parent, model, archive_path):
    """Extract and load a theme archive."""
    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            # Extract to temp dir with safe filtering
            tmpdir = tempfile.mkdtemp(prefix="icewm_theme_import_")

            # Use Python 3.12+ data filter if available, else manual filtering
            if hasattr(tarfile, 'data_filter'):
                tar.extractall(tmpdir, filter="data")
            else:
                tar.extractall(tmpdir, members=list(_safe_tar_members(tar, tmpdir)))

            # Find default.theme
            theme_file = None
            for root, dirs, files in os.walk(tmpdir):
                if "default.theme" in files:
                    theme_file = os.path.join(root, "default.theme")
                    break

            if theme_file is None:
                _show_error(parent, "No default.theme found in archive.")
                shutil.rmtree(tmpdir, ignore_errors=True)
                return False

            model.load_file(theme_file)
            # Register tmpdir for cleanup when the model loads another theme.
            # Must be after load_file() since load cleans up previous temp dirs.
            model.register_temp_dir(tmpdir)
            return True

    except Exception as e:
        _show_error(parent, f"Import failed: {e}")
        return False


def export_theme_dialog(parent, model):
    """Show a dialog to export the current theme as a .tar.gz archive.

    Args:
        parent: Parent window.
        model: ThemeModel instance.

    Returns:
        True if export succeeded.
    """
    if not model.theme_dir:
        _show_error(parent, "Save the theme first before exporting.")
        return False

    dialog = Gtk.FileChooserDialog(
        title="Export Theme Archive",
        transient_for=parent,
        action=Gtk.FileChooserAction.SAVE,
    )
    dialog.add_buttons(
        Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
        Gtk.STOCK_SAVE, Gtk.ResponseType.OK,
    )
    dialog.set_do_overwrite_confirmation(True)

    theme_name = model.get("ThemeDescription", "theme")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in theme_name)
    dialog.set_current_name(f"{safe_name}.tar.gz")

    response = dialog.run()
    result = False

    if response == Gtk.ResponseType.OK:
        output_path = dialog.get_filename()
        result = _do_export(parent, model, output_path)

    dialog.destroy()
    return result


def _do_export(parent, model, output_path):
    """Create a .tar.gz archive of the theme directory."""
    theme_dir = model.theme_dir
    if not theme_dir or not os.path.isdir(theme_dir):
        _show_error(parent, "Theme directory not found.")
        return False

    try:
        dir_name = os.path.basename(theme_dir)
        with tarfile.open(output_path, "w:gz") as tar:
            for root, dirs, files in os.walk(theme_dir):
                for f in files:
                    full = os.path.join(root, f)
                    arcname = os.path.join(dir_name, os.path.relpath(full, theme_dir))
                    tar.add(full, arcname=arcname)
        return True
    except Exception as e:
        _show_error(parent, f"Export failed: {e}")
        return False


def _show_error(parent, message):
    if parent is None:
        print(f"Error: {message}")
        return
    dialog = Gtk.MessageDialog(
        transient_for=parent,
        message_type=Gtk.MessageType.ERROR,
        buttons=Gtk.ButtonsType.OK,
        text=message,
    )
    dialog.run()
    dialog.destroy()
