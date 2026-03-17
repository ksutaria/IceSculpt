# IceSculpt User Guide

Welcome to IceSculpt! This guide will help you navigate the application and create stunning themes for your IceWM desktop.

## Getting Started

### Launching the Application
Run `icesculpt` from your application menu or terminal. You'll be greeted with the main window, featuring an editor panel on the left and a live preview on the right.

### The Main Interface
*   **Editor Tabs:** Categorized panels (Colors, Fonts, etc.) where you modify theme properties.
*   **Live Preview:** Shows a simulated IceWM desktop environment that updates in real-time.
*   **Menu Bar:** Access file operations, undo/redo, and view toggles.

## Core Workflows

### Creating a New Theme
1.  Go to `File -> New Theme...`.
2.  Enter the theme name and your name as the author.
3.  Choose an initial "Look" style (e.g., `flat`, `pixmap`).
4.  Click OK. You now have a blank canvas with reasonable defaults.

### Opening and Editing Themes
1.  Go to `File -> Open...`.
2.  Navigate to your `~/.icewm/themes` folder and select a `default.theme` file.
3.  Modify properties in the editor tabs:
    *   **Colors:** Change window borders, taskbar, and menu colors.
    *   **Fonts:** Set font families and sizes for various UI elements.
    *   **Dimensions:** Adjust title bar height, border thickness, and corner sizes.
    *   **Pixmaps:** (For `pixmap` look) Manage the background images for buttons and bars.
4.  Use `Edit -> Undo` (Ctrl+Z) if you make a mistake.

### Applying Your Theme
When you're happy with the results:
1.  Go to `File -> Apply to IceWM`.
2.  The application will copy your theme to `~/.icewm/themes/` and signal IceWM to restart and use the new theme immediately.

## Tips for Better Themes
*   **Use Presets:** Go to `File -> Apply Preset` to quickly try popular color schemes like Nord or Dracula.
*   **Focus Your View:** Use the `View` menu to toggle the preview or split the screen equally between the editor and preview.
*   **Keep Backups:** Use `File -> Export Archive` to save your theme as a `.tar.gz` file for backup or sharing.
