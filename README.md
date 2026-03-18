# IceSculpt

[![Build and Package](https://github.com/ksutaria/IceSculpt/actions/workflows/build.yml/badge.svg)](https://github.com/ksutaria/IceSculpt/actions)
[![codecov](https://codecov.io/gh/ksutaria/IceSculpt/branch/main/graph/badge.svg)](https://app.codecov.io/gh/ksutaria/IceSculpt)

IceSculpt is a visual theme editor for the [IceWM](https://ice-wm.org/) window manager. It provides an intuitive, GTK3-based interface for creating, editing, and previewing IceWM themes without needing to manually edit configuration files or manually re-render XPM images.

![IceSculpt](https://via.placeholder.com/800x500.png?text=IceWM+Theme+Studio+Screenshot) *(Placeholder for screenshot)*

## Features

* **Real-time Preview:** See changes instantly as you edit colors, fonts, and dimensions. The preview uses Cairo to accurately simulate the IceWM desktop, taskbar, and menus.
* **Lossless Parsing:** The `.theme` file parser preserves all comments, blank lines, and unrecognized keys. Re-saving a theme won't destroy your manual formatting.
* **Comprehensive Property Support:** Editors for Colors, Fonts, Dimensions, Pixmaps, Taskbar settings, Desktop settings, Icons, and Metadata.
* **XPM Codec Built-in:** Native support for reading, generating, and writing XPM (X PixMap) files, which are extensively used by IceWM.
* **Presets:** Apply pre-defined color schemes (like Nord, Dracula, Gruvbox) from built-in JSON presets.
* **Import/Export:** Easily share themes by importing and exporting `.tar.gz` archives.

## Installation

### Prerequisites
Ensure you have the required system libraries installed. On Debian/Ubuntu-based systems:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### Install from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/ksutaria/IceSculpt.git
   cd IceSculpt
   ```
2. Install the package:
   ```bash
   pip install .
   ```
   *(For development, use `pip install -e .` to install in editable mode).*

## Usage

Launch the application from your terminal:
```bash
icesculpt
```

* **Create a New Theme:** Go to `File -> New Theme...` to start from scratch.
* **Open an Existing Theme:** Go to `File -> Open...` and select a `default.theme` file (e.g., from `~/.icewm/themes/`).
* **Live Preview:** Toggle the live preview pane from the `View` menu.
* **Apply to IceWM:** Once you are happy with your changes, click `File -> Apply to IceWM`. This will copy your theme to `~/.icewm/themes/` and signal IceWM to restart.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Clone the repository and install in editable mode.
2. Run tests using `pytest`:
   ```bash
   pytest
   ```
3. Generate preview images for visual inspection:
   ```bash
   python3 tests/render_preview.py
   ```

### Architecture Overview
* **`icesculpt/theme_model.py`:** The central data store. UI components update the model, which fires events to the renderer.
* **`icesculpt/preview_renderer.py`:** A Cairo-based engine that draws a simulated IceWM environment based on the current model state.
* **`icesculpt/theme_parser.py`:** Reads and writes IceWM configuration files while preserving non-data text (comments, spacing).

## License

This project is licensed under the **LGPL-2.1-or-later** License. See the [LICENSE](LICENSE) file for details.
