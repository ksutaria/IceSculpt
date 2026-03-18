#!/usr/bin/env python3
"""Capture screenshots of specific UI components for documentation."""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import cairo

from icesculpt.theme_model import ThemeModel
from icesculpt.editors.color_editor import ColorEditor
from icesculpt.editors.taskbar_editor import TaskbarEditor

def load_dracula(model):
    path = os.path.join(os.path.dirname(__file__), "..", "icesculpt", "data", "presets", "dracula.json")
    with open(path) as f:
        data = json.load(f)
    for key, value in data.get("colors", {}).items():
        model.values[key] = value

def capture_widget(widget, path, width=600, height=400):
    offscreen = Gtk.OffscreenWindow()
    offscreen.add(widget)
    offscreen.show_all()
    
    # Let it layout
    while Gtk.events_pending():
        Gtk.main_iteration()
    
    # Create surface and render
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    cr = cairo.Context(surface)
    
    # White background for components
    cr.set_source_rgb(1, 1, 1)
    cr.rectangle(0, 0, width, height)
    cr.fill()
    
    widget.draw(cr)
    surface.write_to_png(path)
    print(f"  Written: {path}")

if __name__ == "__main__":
    Gtk.init([])
    model = ThemeModel()
    load_dracula(model)
    
    print("Capturing UI components...")
    
    # 1. Color Editor
    ce = ColorEditor(model)
    ce.set_size_request(600, 800)
    capture_widget(ce, "/tmp/ui_color_editor.png", 600, 800)
    
    # 2. Taskbar Editor
    te = TaskbarEditor(model)
    te.set_size_request(600, 300)
    capture_widget(te, "/tmp/ui_taskbar_editor.png", 600, 300)
    
    print("Done!")
