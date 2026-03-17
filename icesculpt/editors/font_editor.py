"""Font editor — all font settings with GtkFontChooser integration."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango


# Font keys and their labels
FONT_KEYS = [
    ("TitleFontNameXft", "Title Bar Font"),
    ("MenuFontNameXft", "Menu Font"),
    ("StatusFontNameXft", "Status Font"),
    ("QuickSwitchFontNameXft", "QuickSwitch Font"),
    ("NormalButtonFontNameXft", "Normal Button Font"),
    ("ActiveButtonFontNameXft", "Active Button Font"),
    ("NormalTaskBarFontNameXft", "Normal Taskbar Font"),
    ("ActiveTaskBarFontNameXft", "Active Taskbar Font"),
    ("ToolButtonFontNameXft", "Tool Button Font"),
    ("NormalWorkspaceFontNameXft", "Normal Workspace Font"),
    ("ActiveWorkspaceFontNameXft", "Active Workspace Font"),
    ("MinimizedWindowFontNameXft", "Minimized Window Font"),
    ("ListBoxFontNameXft", "ListBox Font"),
    ("ToolTipFontNameXft", "Tooltip Font"),
    ("ClockFontNameXft", "Clock Font"),
    ("ApmFontNameXft", "APM/Battery Font"),
    ("InputFontNameXft", "Input Font"),
    ("LabelFontNameXft", "Label Font"),
]


def xft_to_pango(xft_str):
    """Convert an Xft font string to a Pango font description string.

    Xft format: "family:size=N:style"
    Pango format: "family style size"

    This is a best-effort conversion for the font dialog.
    """
    if not xft_str:
        return "Sans 10"

    parts = xft_str.split(":")
    family = parts[0] if parts else "Sans"
    size = "10"
    weight = ""
    slant = ""

    for part in parts[1:]:
        part = part.strip()
        if part.startswith("size="):
            size = part[5:]
        elif part == "bold":
            weight = "Bold"
        elif part == "italic":
            slant = "Italic"
        elif part.startswith("style="):
            style = part[6:]
            if "bold" in style.lower():
                weight = "Bold"
            if "italic" in style.lower():
                slant = "Italic"

    desc_parts = [family]
    if weight:
        desc_parts.append(weight)
    if slant:
        desc_parts.append(slant)
    desc_parts.append(size)
    return " ".join(desc_parts)


def pango_to_xft(pango_desc):
    """Convert a Pango font description string back to Xft format.

    Pango format: "Family Style Size"
    Xft format: "family:size=N:style"
    """
    if not pango_desc:
        return "sans-serif:size=10"

    # Parse from Pango description object
    from gi.repository import Pango
    desc = Pango.FontDescription.from_string(pango_desc)

    family = desc.get_family() or "sans-serif"
    size = desc.get_size()
    if desc.get_size_is_absolute():
        size_val = size / Pango.SCALE
    else:
        size_val = size / Pango.SCALE

    parts = [family, f"size={size_val:.0f}"]

    weight = desc.get_weight()
    if weight >= Pango.Weight.BOLD:
        parts.append("bold")

    style = desc.get_style()
    if style == Pango.Style.ITALIC or style == Pango.Style.OBLIQUE:
        parts.append("italic")

    return ":".join(parts)


class FontEditor(Gtk.ScrolledWindow):
    """Scrollable panel with all font settings."""

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._buttons = {}

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)

        for key, label_text in FONT_KEYS:
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

            label = Gtk.Label(label=label_text)
            label.set_xalign(0)
            label.set_size_request(200, -1)
            hbox.pack_start(label, False, False, 0)

            xft_val = model.get(key, "sans-serif:size=10")
            btn = Gtk.FontButton()
            btn.set_font(xft_to_pango(xft_val))
            btn.set_use_font(True)
            btn.set_use_size(True)
            btn.connect("font-set", self._on_font_set, key)
            hbox.pack_start(btn, True, True, 0)

            # Show the Xft string
            xft_label = Gtk.Label(label=xft_val)
            xft_label.set_xalign(0)
            xft_label.set_ellipsize(Pango.EllipsizeMode.END)
            xft_label.set_max_width_chars(30)
            hbox.pack_start(xft_label, False, False, 0)

            self._buttons[key] = (btn, xft_label)
            vbox.pack_start(hbox, False, False, 0)

        self.add(vbox)
        model.connect(self._on_model_changed)

    def _on_font_set(self, btn, key):
        pango_str = btn.get_font()
        try:
            xft_str = pango_to_xft(pango_str)
        except Exception:
            xft_str = pango_str or "sans-serif:size=10"
        self.model.set(key, xft_str)
        if key in self._buttons:
            _, xft_label = self._buttons[key]
            xft_label.set_text(xft_str)

    def _on_model_changed(self, key):
        if key is None:
            for k, (btn, xft_label) in self._buttons.items():
                xft_val = self.model.get(k, "sans-serif:size=10")
                try:
                    btn.set_font(xft_to_pango(xft_val))
                except Exception:
                    btn.set_font("Sans 10")
                xft_label.set_text(xft_val)
        elif key in self._buttons:
            btn, xft_label = self._buttons[key]
            xft_val = self.model.get(key, "sans-serif:size=10")
            try:
                btn.set_font(xft_to_pango(xft_val))
            except Exception:
                btn.set_font("Sans 10")
            xft_label.set_text(xft_val)
