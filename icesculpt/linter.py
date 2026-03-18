"""Theme linter and health check rules for IceWM themes."""

import os
from . import color_utils

class LintMessage:
    """A single lint finding."""
    def __init__(self, key, message, severity="warning"):
        self.key = key
        self.message = message
        self.severity = severity  # error, warning, info

    def __str__(self):
        return f"[{self.severity.upper()}] {self.key}: {self.message}"

def lint_theme(model):
    """Run all lint rules on the given ThemeModel.
    
    Returns:
        List of LintMessage objects.
    """
    messages = []

    # 1. Check required metadata
    required_metadata = ["ThemeDescription", "ThemeAuthor"]
    for key in required_metadata:
        if not model.get(key):
            messages.append(LintMessage(key, "Missing recommended metadata field", "info"))

    # 2. Check color formats
    for key, value in model.values.items():
        if key.startswith("Color") and value:
            # Multi-color gradients are allowed: "color1,color2,color3"
            parts = value.split(',')
            for part in parts:
                try:
                    color_utils.icewm_to_hex(part.strip())
                except ValueError:
                    messages.append(LintMessage(key, f"Invalid color format: {part!r}", "error"))

    # 3. Check for deprecated keys
    deprecated = {
        "MenuMouseTracking": "Use MenuMouseTracking=1 instead",
        "ShowHelp": "Deprecated in recent IceWM versions",
    }
    for key in model.values:
        if key in deprecated:
            messages.append(LintMessage(key, deprecated[key], "warning"))

    # 4. Check pixmap references
    if model.theme_dir:
        for key, value in model.values.items():
            if key.endswith("Pixmap") and value:
                # Value is a filename or relative path
                px_path = os.path.join(model.theme_dir, value)
                if not os.path.exists(px_path) and not value.startswith("/"):
                    # Check common extensions if not provided
                    found = False
                    for ext in [".xpm", ".png", ".svg"]:
                        if os.path.exists(px_path + ext):
                            found = True
                            break
                    if not found:
                        messages.append(LintMessage(key, f"Referenced pixmap not found: {value}", "warning"))

    # 5. Accessibility: Contrast check
    # Check Active Title Bar text contrast
    bg = model.get_color_hex("ColorActiveTitleBar", "#5E81AC")
    fg = model.get_color_hex("ColorActiveTitleBarText", "#ECEFF4")
    ratio = color_utils.get_contrast_ratio(bg, fg)
    if ratio < 4.5:
        messages.append(LintMessage("ColorActiveTitleBarText",
                                    f"Low contrast ratio ({ratio:.2f}:1) against title bar background. WCAG recommends 4.5:1.",
                                    "warning"))

    return messages
