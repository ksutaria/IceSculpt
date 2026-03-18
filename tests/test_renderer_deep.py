"""Deep tests for the PreviewRenderer logic."""

import unittest
import cairo
from icesculpt.theme_model import ThemeModel
from icesculpt.preview_renderer import PreviewRenderer

class TestRendererDeep(unittest.TestCase):
    def setUp(self):
        self.model = ThemeModel()
        self.model.new_theme()
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 800, 600)
        self.cr = cairo.Context(self.surface)
        self.renderer = PreviewRenderer(self.model)

    def test_render_all_components(self):
        # Full desktop render
        self.renderer.render(self.cr, 800, 600)
        
        # Specific sub-components
        self.renderer.render_menu_preview(self.cr, 0, 0, 200)
        self.renderer.render_tooltip_preview(self.cr, 0, 0)

    def test_rendering_variants(self):
        # Test justify variants
        for justify in [0, 50, 100]:
            self.model.set("TitleBarJustify", str(justify))
            self.renderer.render(self.cr, 800, 600)

        # Test button configuration variants
        self.model.set("TitleButtonsLeft", "s")
        self.model.set("TitleButtonsRight", "xmi")
        self.renderer.render(self.cr, 800, 600)

    def test_color_fallbacks(self):
        # Clear all values to force fallbacks
        self.model.values = {}
        self.renderer.render(self.cr, 800, 600)
        self.renderer.render_menu_preview(self.cr, 0, 0, 200)

    def test_dimensions_clamping(self):
        self.model.set("BorderSizeX", "100") # Too large
        self.model.set("TitleBarHeight", "5") # Too small
        self.renderer.render(self.cr, 800, 600)

    def test_taskbar_rendering(self):
        # Force taskbar colors
        self.model.set("ColorDefaultTaskBar", "rgb:11/11/11")
        self.model.set("ColorActiveTaskBarApp", "rgb:22/22/22")
        self.renderer.render(self.cr, 800, 600)

if __name__ == "__main__":
    unittest.main()
