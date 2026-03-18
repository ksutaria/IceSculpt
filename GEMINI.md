# IceSculpt

Visual theme editor for the IceWM window manager.

## Project Overview

`icesculpt` is a Python-based GTK+ 3 application designed to simplify the creation and modification of IceWM themes. It provides a real-time preview of theme changes using a Cairo-based renderer and supports both traditional color-based themes and modern pixmap-based themes.

### Key Technologies
- **Python 3.8+**: Core application logic.
- **GTK+ 3 (via PyGObject)**: User interface.
- **Cairo (via pycairo)**: High-fidelity preview rendering.
- **IceWM Theme Format**: Parser and writer for `.theme` files.
- **XPM**: Support for X PixMap format used by IceWM.

## Directory Structure

- `icesculpt/`: Core package.
    - `app.py`: Entry point and GTK application lifecycle.
    - `main_window.py`: Main window layout and high-level UI coordination.
    - `theme_model.py`: Reactive model representing the theme being edited.
    - `theme_parser.py`: Robust parser/writer for IceWM `.theme` files that preserves comments and formatting.
    - `preview_renderer.py`: Cairo-based rendering engine for theme previews (taskbar, windows, menus).
    - `color_utils.py`: Utilities for converting between IceWM color formats (hex, rgb:R/G/B, etc.) and RGBA.
    - `editors/`: Specialized UI panels for editing different theme aspects (Colors, Dimensions, Fonts, Pixmaps, Metadata).
    - `widgets/`: Custom GTK widgets (Color swatch, Pixmap canvas, etc.).
    - `data/`: Static data and resources.
        - `theme_keys.json`: Comprehensive metadata for all IceWM theme properties.
        - `presets/`: Built-in theme presets (Nord, Gruvbox, Dracula, etc.).
        - `pixmap_templates/`: Base templates for generating new pixmap themes.
- `tests/`: Comprehensive test suite.
    - `test_*.py`: Unit tests for parser, color utils, and logic.
    - `render_*.py`: Headless rendering scripts for visual verification.

## Building and Running

### Prerequisites
Ensure you have the required system libraries installed (Debian/Ubuntu example):
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 xvfb
```

### Development Setup
```bash
# Install in editable mode with test dependencies
pip install -e .
```

### Running the Application
```bash
# Using the launcher script
./icesculpt

# Or via python
python3 -m icesculpt.app
```

### Testing
```bash
# Run all tests using pytest
pytest

# Or run specific test files
python3 -m unittest tests/test_parser.py

# Generate preview images for visual inspection
python3 tests/render_preview.py
```

## Development Conventions

- **Modular Editors:** Each property category (Colors, Fonts, etc.) has its own editor class in `icesculpt/editors/`.
- **Theme Model:** All UI changes should go through `ThemeModel` to ensure consistency and trigger preview updates.
- **Parser Integrity:** `theme_parser.py` is designed to be "lossless" regarding comments and unknown keys; avoid bypassing it when saving files.
- **Type Hinting:** New code should include Python type hints for better maintainability.
- **Linting:** Use `flake8` or `ruff` (preferred) for code style enforcement.
