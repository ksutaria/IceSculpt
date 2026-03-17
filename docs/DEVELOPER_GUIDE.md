# IceSculpt Developer Guide

Welcome, developers! This guide provides a technical overview of IceSculpt's architecture and development process.

## Architecture Overview

IceSculpt follows a reactive architecture where `ThemeModel` serves as the central state store.

*   **Model (`theme_model.py`):** Holds the current theme properties and fires events on changes.
*   **View (`main_window.py` + `editors/`):** GTK+ 3 interface that displays data and allows users to modify it.
*   **Renderer (`preview_renderer.py`):** Uses Cairo to draw a visual representation of the theme based on the current model state.
*   **Parser (`theme_parser.py`):** Handles reading and writing the `.theme` format while maintaining formatting and comments.
*   **Codec (`xpm_codec.py`):** Custom implementation for reading and writing XPM images used by IceWM.

## Development Setup

### Python Environment
Create a virtual environment and install the package in editable mode:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e ".[test]"
```

### Running Tests
We use `pytest` for unit testing.
```bash
pytest
```
For visual verification of renderer changes:
```bash
python3 tests/render_preview.py
```

## Adding New Theme Properties
1.  **Registry:** Add the new property to `icesculpt/data/theme_keys.json`.
2.  **Editor:** If it belongs to a new category, create a new editor in `icesculpt/editors/` and register it in `MainWindow`.
3.  **Renderer:** Update `PreviewRenderer` in `preview_renderer.py` to visually reflect the new property.

## Binary Build and Distribution Strategy

To ensure users have a full inclusive binary ready to execute with all dependencies, we use **AppImage** and **Flatpak** for Linux distribution.

### Build Philosophy
*   **Self-Contained:** Binaries should bundle Python, GTK, and all necessary libraries.
*   **Architecture Support:** We provide builds for `x86_64` (amd64) and `aarch64` (arm64).
*   **CI/CD:** Builds are automated using **GitHub Actions**.

### Simulated Environments (Multi-arch)
We use `qemu-user-static` combined with Docker containers in our CI pipelines to simulate different architectures (`arm64`, `x86`) on `amd64` runners. This ensures consistent binary generation across all target platforms.

### Distribution Formats
*   **AppImage:** A single-file executable that runs on most Linux distributions.
*   **Flatpak:** A sandboxed application format distributed via Flathub.
*   **Python Wheel:** Standard Python distribution for users who prefer `pip install`.
