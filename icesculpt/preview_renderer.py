"""Cairo-based live preview of IceWM window decorations and taskbar.

Renders a simulated desktop with:
  - An active window with title bar, borders, and buttons
  - An inactive window behind it
  - A taskbar strip at the bottom
"""

class PreviewRenderer:
    """Renders a preview of IceWM window decorations using Cairo.

    All drawing uses theme model values for colors, dimensions, and fonts.
    """

    def __init__(self, model):
        """Initialize with a ThemeModel instance."""
        self.model = model
        self.force_active = None  # None = draw both, True = only active, False = only inactive

    def render(self, cr, width, height):
        """Render the full preview scene.

        Args:
            cr: Cairo context.
            width: Available width in pixels.
            height: Available height in pixels.
        """
        # Background
        self._draw_desktop_bg(cr, width, height)

        # Reserve space for taskbar
        taskbar_h = 32
        desktop_h = height - taskbar_h

        # Draw inactive window first (behind)
        if self.force_active is None or self.force_active is False:
            self._draw_window(cr, active=False,
                              x=width * 0.35, y=desktop_h * 0.1,
                              w=width * 0.55, h=desktop_h * 0.55,
                              title="Inactive Window")

        # Draw active window on top
        if self.force_active is None or self.force_active is True:
            # Shift position if only active is shown
            x = width * 0.05 if self.force_active is None else width * 0.2
            y = desktop_h * 0.15 if self.force_active is None else desktop_h * 0.15
            w = width * 0.6 if self.force_active is None else width * 0.6
            h = desktop_h * 0.65 if self.force_active is None else desktop_h * 0.65
            
            self._draw_window(cr, active=True,
                              x=x, y=y, w=w, h=h,
                              title="Active Window")

        # Draw taskbar
        self._draw_taskbar(cr, 0, desktop_h, width, taskbar_h)

    def _draw_desktop_bg(self, cr, width, height):
        """Draw the desktop background."""
        r, g, b, a = self.model.get_color_rgba("DesktopBackgroundColor", "#2E3440")
        cr.set_source_rgb(r, g, b)
        cr.rectangle(0, 0, width, height)
        cr.fill()

    def _draw_window(self, cr, active, x, y, w, h, title="Window"):
        """Draw a complete window with title bar, borders, and client area."""
        m = self.model
        prefix = "Active" if active else "Normal"

        border_x = m.get_int("BorderSizeX", 6)
        border_y = m.get_int("BorderSizeY", 6)
        title_h = m.get_int("TitleBarHeight", 20)

        # Clamp to reasonable sizes
        border_x = max(1, min(border_x, 20))
        border_y = max(1, min(border_y, 20))
        title_h = max(12, min(title_h, 48))

        x, y, w, h = int(x), int(y), int(w), int(h)

        # -- Border --
        br, bg, bb, _ = m.get_color_rgba(f"Color{prefix}Border", "#4C566A" if not active else "#5E81AC")
        cr.set_source_rgb(br, bg, bb)
        cr.rectangle(x, y, w, h)
        cr.fill()

        # -- Title bar background --
        tr, tg, tb, _ = m.get_color_rgba(f"Color{prefix}TitleBar", "#3B4252" if not active else "#5E81AC")
        cr.set_source_rgb(tr, tg, tb)
        cr.rectangle(x + border_x, y + border_y, w - 2 * border_x, title_h)
        cr.fill()

        # -- Title text --
        txr, txg, txb, _ = m.get_color_rgba(f"Color{prefix}TitleBarText", "#D8DEE9" if not active else "#ECEFF4")
        cr.set_source_rgb(txr, txg, txb)
        cr.select_font_face("Sans", 0, 1 if active else 0)  # Bold for active
        font_size = max(10, min(title_h - 4, 18))
        cr.set_font_size(font_size)

        # Title text position
        text_extents = cr.text_extents(title)
        justify = m.get_int("TitleBarJustify", 0)
        title_area_w = w - 2 * border_x - title_h * 2  # Leave room for buttons
        if justify == 0:  # Left
            tx = x + border_x + title_h + 4
        elif justify == 100:  # Right
            tx = x + border_x + title_area_w - text_extents.width
        else:  # Center or proportional
            tx = x + border_x + title_h + (title_area_w - text_extents.width) * justify / 100.0
        ty = y + border_y + (title_h + font_size) / 2 - 2

        cr.move_to(tx, ty)
        cr.show_text(title)

        # -- Title bar buttons --
        self._draw_title_buttons(cr, active, x + border_x, y + border_y,
                                 w - 2 * border_x, title_h)

        # -- Client area --
        client_x = x + border_x
        client_y = y + border_y + title_h
        client_w = w - 2 * border_x
        client_h = h - 2 * border_y - title_h

        if client_w > 0 and client_h > 0:
            cr.set_source_rgb(0.95, 0.95, 0.95)
            cr.rectangle(client_x, client_y, client_w, client_h)
            cr.fill()

            # Draw some fake content lines
            cr.set_source_rgba(0.7, 0.7, 0.7, 0.5)
            line_y = client_y + 15
            while line_y < client_y + client_h - 10:
                line_w = client_w * (0.4 + 0.4 * ((line_y * 7) % 13) / 13.0)
                cr.rectangle(client_x + 10, line_y, min(line_w, client_w - 20), 8)
                cr.fill()
                line_y += 18

    def _draw_title_buttons(self, cr, active, bar_x, bar_y, bar_w, bar_h):
        """Draw close/maximize/minimize buttons on the title bar."""
        m = self.model
        btn_size = max(8, bar_h - 6)
        btn_y = bar_y + (bar_h - btn_size) // 2
        margin = 3

        # Button background color
        prefix = "Active" if active else "Normal"
        btn_bg_r, btn_bg_g, btn_bg_b, _ = m.get_color_rgba(f"Color{prefix}Button", "#4C566A")
        btn_fg_r, btn_fg_g, btn_fg_b, _ = m.get_color_rgba(f"Color{prefix}ButtonText", "#D8DEE9")

        # Right side buttons: close, maximize, minimize
        buttons_right = m.get("TitleButtonsRight", "xmir")
        bx = bar_x + bar_w - margin - btn_size
        for btn_char in buttons_right:
            if bx < bar_x + bar_w // 3:
                break
            # Button background
            cr.set_source_rgb(btn_bg_r, btn_bg_g, btn_bg_b)
            cr.rectangle(bx, btn_y, btn_size, btn_size)
            cr.fill()

            # Button border (subtle 3D effect)
            cr.set_source_rgba(1, 1, 1, 0.3)
            cr.move_to(bx, btn_y + btn_size)
            cr.line_to(bx, btn_y)
            cr.line_to(bx + btn_size, btn_y)
            cr.set_line_width(1)
            cr.stroke()
            cr.set_source_rgba(0, 0, 0, 0.3)
            cr.move_to(bx + btn_size, btn_y)
            cr.line_to(bx + btn_size, btn_y + btn_size)
            cr.line_to(bx, btn_y + btn_size)
            cr.set_line_width(1)
            cr.stroke()

            # Button symbol
            cr.set_source_rgb(btn_fg_r, btn_fg_g, btn_fg_b)
            cr.set_line_width(1.5)
            cx, cy = bx + btn_size / 2, btn_y + btn_size / 2
            s = btn_size * 0.3  # Symbol half-size

            if btn_char == 'x':  # Close
                cr.move_to(cx - s, cy - s)
                cr.line_to(cx + s, cy + s)
                cr.stroke()
                cr.move_to(cx + s, cy - s)
                cr.line_to(cx - s, cy + s)
                cr.stroke()
            elif btn_char == 'm':  # Maximize
                cr.rectangle(cx - s, cy - s, s * 2, s * 2)
                cr.stroke()
            elif btn_char == 'i':  # Minimize
                cr.move_to(cx - s, cy + s)
                cr.line_to(cx + s, cy + s)
                cr.set_line_width(2)
                cr.stroke()
                cr.set_line_width(1.5)
            elif btn_char == 'r':  # Rollup
                cr.move_to(cx - s, cy + s * 0.5)
                cr.line_to(cx, cy - s * 0.5)
                cr.line_to(cx + s, cy + s * 0.5)
                cr.stroke()
            elif btn_char == 'h':  # Hide
                cr.move_to(cx - s, cy)
                cr.line_to(cx + s, cy)
                cr.stroke()

            bx -= btn_size + margin

        # Left side: system menu button
        buttons_left = m.get("TitleButtonsLeft", "s")
        lx = bar_x + margin
        for btn_char in buttons_left:
            if btn_char == 's':  # System menu
                cr.set_source_rgb(btn_bg_r, btn_bg_g, btn_bg_b)
                cr.rectangle(lx, btn_y, btn_size, btn_size)
                cr.fill()

                # Draw a small menu icon (three lines)
                cr.set_source_rgb(btn_fg_r, btn_fg_g, btn_fg_b)
                cr.set_line_width(1.5)
                for i in range(3):
                    ly = btn_y + btn_size * (0.3 + i * 0.2)
                    cr.move_to(lx + btn_size * 0.25, ly)
                    cr.line_to(lx + btn_size * 0.75, ly)
                    cr.stroke()

            lx += btn_size + margin

    def _draw_taskbar(self, cr, x, y, w, h):
        """Draw the taskbar strip."""
        m = self.model

        # Taskbar background
        r, g, b, _ = m.get_color_rgba("ColorDefaultTaskBar", "#3B4252")
        cr.set_source_rgb(r, g, b)
        cr.rectangle(x, y, w, h)
        cr.fill()

        # Top edge highlight
        cr.set_source_rgba(1, 1, 1, 0.15)
        cr.move_to(x, y + 0.5)
        cr.line_to(x + w, y + 0.5)
        cr.set_line_width(1)
        cr.stroke()

        # Start button area
        btn_w = 60
        btn_h = h - 6
        btn_x = x + 3
        btn_y = y + 3

        ar, ag, ab, _ = m.get_color_rgba("ColorActiveTaskBarApp", "#4C566A")
        cr.set_source_rgb(ar, ag, ab)
        cr.rectangle(btn_x, btn_y, btn_w, btn_h)
        cr.fill()

        # Active task button text
        atr, atg, atb, _ = m.get_color_rgba("ColorActiveTaskBarAppText", "#ECEFF4")
        cr.set_source_rgb(atr, atg, atb)
        cr.select_font_face("Sans", 0, 1)
        cr.set_font_size(11)
        cr.move_to(btn_x + 6, btn_y + btn_h - 5)
        cr.show_text("Active")

        # Normal task button
        nbtn_x = btn_x + btn_w + 4
        nbtn_w = 70
        nr, ng, nb, _ = m.get_color_rgba("ColorNormalTaskBarApp", "#2E3440")
        cr.set_source_rgb(nr, ng, nb)
        cr.rectangle(nbtn_x, btn_y, nbtn_w, btn_h)
        cr.fill()

        ntr, ntg, ntb, _ = m.get_color_rgba("ColorNormalTaskBarAppText", "#D8DEE9")
        cr.set_source_rgb(ntr, ntg, ntb)
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(11)
        cr.move_to(nbtn_x + 6, btn_y + btn_h - 5)
        cr.show_text("Inactive")

        # Clock on the right
        clock_w = 55
        clock_x = x + w - clock_w - 4
        clock_y = btn_y

        clk_r, clk_g, clk_b, _ = m.get_color_rgba("ColorClock", "#2E3440")
        cr.set_source_rgb(clk_r, clk_g, clk_b)
        cr.rectangle(clock_x, clock_y, clock_w, btn_h)
        cr.fill()

        ct_r, ct_g, ct_b, _ = m.get_color_rgba("ColorClockText", "#88C0D0")
        cr.set_source_rgb(ct_r, ct_g, ct_b)
        cr.select_font_face("Monospace", 0, 0)
        cr.set_font_size(11)
        cr.move_to(clock_x + 6, clock_y + btn_h - 5)
        cr.show_text("12:34")

    def render_menu_preview(self, cr, x, y, width):
        """Render a menu preview snippet.

        Args:
            cr: Cairo context.
            x, y: Top-left position.
            width: Menu width.
        """
        m = self.model
        item_h = 24
        items = [
            ("File", False),
            ("Edit", True),  # active/highlighted
            ("View", False),
            ("---", False),  # separator
            ("Help", False),
        ]

        cur_y = y
        for label, active in items:
            if label == "---":
                # Separator
                sep_r, sep_g, sep_b, _ = m.get_color_rgba("ColorNormalMenuSeparator", "#4C566A")
                cr.set_source_rgb(sep_r, sep_g, sep_b)
                cr.set_line_width(1)
                cr.move_to(x + 4, cur_y + item_h // 2 + 0.5)
                cr.line_to(x + width - 4, cur_y + item_h // 2 + 0.5)
                cr.stroke()
            elif active:
                # Active menu item
                ar, ag, ab, _ = m.get_color_rgba("ColorActiveMenuItem", "#5E81AC")
                cr.set_source_rgb(ar, ag, ab)
                cr.rectangle(x, cur_y, width, item_h)
                cr.fill()
                atr, atg, atb, _ = m.get_color_rgba("ColorActiveMenuItemText", "#ECEFF4")
                cr.set_source_rgb(atr, atg, atb)
                cr.select_font_face("Sans", 0, 0)
                cr.set_font_size(12)
                cr.move_to(x + 8, cur_y + 17)
                cr.show_text(label)
            else:
                # Normal menu item
                nr, ng, nb, _ = m.get_color_rgba("ColorNormalMenu", "#3B4252")
                cr.set_source_rgb(nr, ng, nb)
                cr.rectangle(x, cur_y, width, item_h)
                cr.fill()
                ntr, ntg, ntb, _ = m.get_color_rgba("ColorNormalMenuItemText", "#D8DEE9")
                cr.set_source_rgb(ntr, ntg, ntb)
                cr.select_font_face("Sans", 0, 0)
                cr.set_font_size(12)
                cr.move_to(x + 8, cur_y + 17)
                cr.show_text(label)

            cur_y += item_h

    def render_tooltip_preview(self, cr, x, y):
        """Render a tooltip preview."""
        m = self.model
        text = "Tooltip preview"
        cr.select_font_face("Sans", 0, 0)
        cr.set_font_size(11)
        extents = cr.text_extents(text)
        pad = 6

        bg_r, bg_g, bg_b, _ = m.get_color_rgba("ColorToolTip", "#ECEFF4")
        cr.set_source_rgb(bg_r, bg_g, bg_b)
        cr.rectangle(x, y, extents.width + pad * 2, extents.height + pad * 2)
        cr.fill()

        # Border
        cr.set_source_rgba(0, 0, 0, 0.4)
        cr.rectangle(x + 0.5, y + 0.5, extents.width + pad * 2 - 1, extents.height + pad * 2 - 1)
        cr.set_line_width(1)
        cr.stroke()

        # Text
        fg_r, fg_g, fg_b, _ = m.get_color_rgba("ColorToolTipText", "#2E3440")
        cr.set_source_rgb(fg_r, fg_g, fg_b)
        cr.move_to(x + pad, y + pad + extents.height)
        cr.show_text(text)
