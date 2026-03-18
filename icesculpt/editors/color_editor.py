"""Color editor panel — all 70+ color settings organized by category."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from ..widgets.color_swatch import ColorSwatch
from ..color_utils import hex_to_icewm


# Color keys organized by category
COLOR_CATEGORIES = [
    ("Title Bar", [
        ("ColorActiveTitleBar", "Active Title Bar"),
        ("ColorActiveTitleBarText", "Active Title Text"),
        ("ColorActiveTitleBarShadow", "Active Title Shadow"),
        ("ColorNormalTitleBar", "Normal Title Bar"),
        ("ColorNormalTitleBarText", "Normal Title Text"),
        ("ColorNormalTitleBarShadow", "Normal Title Shadow"),
    ]),
    ("Borders", [
        ("ColorActiveBorder", "Active Border"),
        ("ColorNormalBorder", "Normal Border"),
    ]),
    ("Buttons", [
        ("ColorNormalButton", "Normal Button"),
        ("ColorNormalButtonText", "Normal Button Text"),
        ("ColorActiveButton", "Active Button"),
        ("ColorActiveButtonText", "Active Button Text"),
    ]),
    ("Menu", [
        ("ColorNormalMenu", "Normal Menu"),
        ("ColorNormalMenuItemText", "Normal Menu Text"),
        ("ColorActiveMenuItem", "Active Menu Item"),
        ("ColorActiveMenuItemText", "Active Menu Item Text"),
        ("ColorDisabledMenuItemText", "Disabled Menu Text"),
        ("ColorNormalMenuSeparator", "Menu Separator"),
        ("ColorNormalMenuItemShadow", "Menu Item Shadow"),
    ]),
    ("Taskbar", [
        ("ColorDefaultTaskBar", "Taskbar Background"),
        ("ColorNormalTaskBarApp", "Normal Task App"),
        ("ColorNormalTaskBarAppText", "Normal Task App Text"),
        ("ColorActiveTaskBarApp", "Active Task App"),
        ("ColorActiveTaskBarAppText", "Active Task App Text"),
        ("ColorMinimizedTaskBarApp", "Minimized Task App"),
        ("ColorMinimizedTaskBarAppText", "Minimized Task App Text"),
        ("ColorInvisibleTaskBarApp", "Invisible Task App"),
        ("ColorInvisibleTaskBarAppText", "Invisible Task App Text"),
    ]),
    ("Dialog", [
        ("ColorDialog", "Dialog Background"),
        ("ColorDialogText", "Dialog Text"),
    ]),
    ("Tooltip", [
        ("ColorToolTip", "Tooltip Background"),
        ("ColorToolTipText", "Tooltip Text"),
    ]),
    ("QuickSwitch", [
        ("ColorQuickSwitch", "QuickSwitch Background"),
        ("ColorQuickSwitchText", "QuickSwitch Text"),
        ("ColorQuickSwitchActive", "QuickSwitch Active"),
    ]),
    ("ListBox", [
        ("ColorListBox", "ListBox Background"),
        ("ColorListBoxText", "ListBox Text"),
        ("ColorListBoxSelection", "ListBox Selection"),
        ("ColorListBoxSelectionText", "ListBox Selection Text"),
    ]),
    ("ScrollBar", [
        ("ColorScrollBar", "ScrollBar Track"),
        ("ColorScrollBarSlider", "ScrollBar Slider"),
        ("ColorScrollBarButton", "ScrollBar Button"),
        ("ColorScrollBarArrow", "ScrollBar Arrow"),
        ("ColorScrollBarButtonArrow", "ScrollBar Button Arrow"),
        ("ColorScrollBarInactiveArrow", "ScrollBar Inactive Arrow"),
    ]),
    ("Input", [
        ("ColorInput", "Input Background"),
        ("ColorInputText", "Input Text"),
        ("ColorInputSelection", "Input Selection"),
        ("ColorInputSelectionText", "Input Selection Text"),
    ]),
    ("Labels", [
        ("ColorLabel", "Label Background"),
        ("ColorLabelText", "Label Text"),
    ]),
    ("Clock", [
        ("ColorClock", "Clock Background"),
        ("ColorClockText", "Clock Text"),
    ]),
    ("APM / Battery", [
        ("ColorApm", "APM Background"),
        ("ColorApmText", "APM Text"),
        ("ColorApmBattFull", "Battery Full"),
        ("ColorApmBattLow", "Battery Low"),
        ("ColorApmBattCritical", "Battery Critical"),
        ("ColorApmGraphBg", "APM Graph Background"),
    ]),
    ("CPU Monitor", [
        ("ColorCPUStatusUser", "CPU User"),
        ("ColorCPUStatusSystem", "CPU System"),
        ("ColorCPUStatusInterrupts", "CPU Interrupts"),
        ("ColorCPUStatusIoWait", "CPU IO Wait"),
        ("ColorCPUStatusSoftIrq", "CPU Soft IRQ"),
        ("ColorCPUStatusNice", "CPU Nice"),
        ("ColorCPUStatusIdle", "CPU Idle"),
        ("ColorCPUStatusSteal", "CPU Steal"),
    ]),
    ("Network Monitor", [
        ("ColorNetSend", "Net Send"),
        ("ColorNetReceive", "Net Receive"),
        ("ColorNetIdle", "Net Idle"),
    ]),
    ("Memory Monitor", [
        ("ColorMEMStatusUser", "MEM User"),
        ("ColorMEMStatusBuffers", "MEM Buffers"),
        ("ColorMEMStatusCached", "MEM Cached"),
        ("ColorMEMStatusFree", "MEM Free"),
    ]),
    ("Desktop", [
        ("DesktopBackgroundColor", "Desktop Background"),
        ("DesktopTransparencyColor", "Transparency Color"),
    ]),
]


class ColorEditor(Gtk.ScrolledWindow):
    """Scrollable panel with all color settings organized by category."""

    def __init__(self, model):
        super().__init__()
        self.model = model
        self._swatches = {}  # key -> ColorSwatch

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_margin_start(8)
        vbox.set_margin_end(8)
        vbox.set_margin_top(8)
        vbox.set_margin_bottom(8)

        for cat_name, keys in COLOR_CATEGORIES:
            # Category header
            frame = Gtk.Frame(label=cat_name)
            frame.set_margin_top(4)
            frame.set_margin_bottom(4)

            grid = Gtk.Grid()
            grid.set_column_spacing(8)
            grid.set_row_spacing(4)
            grid.set_margin_start(8)
            grid.set_margin_end(8)
            grid.set_margin_top(4)
            grid.set_margin_bottom(8)

            for row_idx, (key, label_text) in enumerate(keys):
                # Label
                label = Gtk.Label(label=label_text)
                label.set_xalign(0)
                label.set_hexpand(True)
                grid.attach(label, 0, row_idx, 1, 1)

                # Color swatch
                val = model.get(key)
                hex_color = model.get_color_hex(key, "#808080")
                display_val = val if ',' in val else hex_color
                
                swatch = ColorSwatch(display_val, size=28)
                swatch.connect("color-changed", self._on_swatch_changed, key)
                grid.attach(swatch, 1, row_idx, 1, 1)

                # Hex label
                label_str = "Gradient" if ',' in val else hex_color
                hex_label = Gtk.Label(label=label_str)
                hex_label.set_xalign(0)
                hex_label.set_width_chars(8)
                hex_label.get_style_context().add_class("monospace")
                grid.attach(hex_label, 2, row_idx, 1, 1)
                
                # Make Gradient button
                grad_btn = Gtk.Button.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
                grad_btn.set_tooltip_text("Convert to Gradient")
                grad_btn.connect("clicked", self._on_make_gradient_clicked, key)
                grid.attach(grad_btn, 3, row_idx, 1, 1)

                self._swatches[key] = (swatch, hex_label)

            frame.add(grid)
            vbox.pack_start(frame, False, False, 0)

        self.add(vbox)

        # Listen for model changes to update swatches
        model.connect(self._on_model_changed)

    def _on_swatch_changed(self, swatch, hex_color, key):
        """Handle color swatch change — update model."""
        if ',' in hex_color:
            self.model.set(key, hex_color)
        else:
            self.model.set_color_hex(key, hex_color)
        
        # Update hex label
        if key in self._swatches:
            _, hex_label = self._swatches[key]
            hex_label.set_text("Gradient" if ',' in hex_color else hex_color)

    def _on_make_gradient_clicked(self, btn, key):
        val = self.model.get(key)
        if ',' not in val:
            h = self.model.get_color_hex(key)
            self.model.set(key, f"{h},{h}")

    def _on_model_changed(self, key):
        """Handle model change — update swatch if needed."""
        if key is None:
            # Full reload
            for k, (swatch, hex_label) in self._swatches.items():
                val = self.model.get(k)
                h = self.model.get_color_hex(k, "#808080")
                display_val = val if ',' in val else h
                swatch.hex_color = display_val
                hex_label.set_text("Gradient" if ',' in display_val else h)
        elif key in self._swatches:
            swatch, hex_label = self._swatches[key]
            val = self.model.get(key)
            h = self.model.get_color_hex(key, "#808080")
            display_val = val if ',' in val else h
            swatch.hex_color = display_val
            hex_label.set_text("Gradient" if ',' in display_val else h)
