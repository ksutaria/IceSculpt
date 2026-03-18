"""A visual widget for building IceWM multi-color gradients."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
from .. import color_utils

class GradientBuilder(Gtk.Box):
    """UI for editing comma-separated color lists (gradients)."""
    
    def __init__(self, value_str, on_changed):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.on_changed = on_changed
        self.colors = []
        
        if value_str:
            for part in value_str.split(','):
                try:
                    self.colors.append(color_utils.icewm_to_hex(part.strip()))
                except ValueError:
                    continue
        
        if not self.colors:
            self.colors = ["#808080"]
            
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.add(self.list_box)
        
        self._refresh()
        
        add_btn = Gtk.Button.new_with_label("Add Color")
        add_btn.connect("clicked", self._on_add_clicked)
        self.pack_start(add_btn, False, False, 0)

    def _refresh(self):
        for child in self.list_box.get_children():
            self.list_box.remove(child)
            
        for i, color in enumerate(self.colors):
            row = Gtk.ListBoxRow()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            row.add(hbox)
            
            cp = Gtk.ColorButton()
            rgba = Gdk.RGBA()
            rgba.parse(color)
            cp.set_rgba(rgba)
            cp.connect("color-set", self._on_color_set, i)
            hbox.pack_start(cp, False, False, 0)
            
            up_btn = Gtk.Button.new_from_icon_name("go-up-symbolic", Gtk.IconSize.BUTTON)
            up_btn.set_sensitive(i > 0)
            up_btn.connect("clicked", self._on_move_clicked, i, -1)
            hbox.pack_start(up_btn, False, False, 0)
            
            down_btn = Gtk.Button.new_from_icon_name("go-down-symbolic", Gtk.IconSize.BUTTON)
            down_btn.set_sensitive(i < len(self.colors) - 1)
            down_btn.connect("clicked", self._on_move_clicked, i, 1)
            hbox.pack_start(down_btn, False, False, 0)
            
            del_btn = Gtk.Button.new_from_icon_name("edit-delete-symbolic", Gtk.IconSize.BUTTON)
            del_btn.set_sensitive(len(self.colors) > 1)
            del_btn.connect("clicked", self._on_delete_clicked, i)
            hbox.pack_start(del_btn, False, False, 0)
            
            self.list_box.add(row)
        
        self.show_all()

    def _on_color_set(self, cp, index):
        rgba = cp.get_rgba()
        self.colors[index] = color_utils.rgba_to_hex(rgba.red, rgba.green, rgba.blue)
        self._notify()

    def _on_move_clicked(self, btn, index, delta):
        new_index = index + delta
        self.colors[index], self.colors[new_index] = self.colors[new_index], self.colors[index]
        self._refresh()
        self._notify()

    def _on_delete_clicked(self, btn, index):
        self.colors.pop(index)
        self._refresh()
        self._notify()

    def _on_add_clicked(self, btn):
        self.colors.append("#808080")
        self._refresh()
        self._notify()

    def _notify(self):
        icewm_colors = [color_utils.hex_to_icewm(c) for color in self.colors]
        # hex_to_icewm returns rgb:RR/GG/BB
        value = ",".join([color_utils.hex_to_icewm(c) for c in self.colors])
        self.on_changed(value)
