"""In-memory data model for IceWM theme settings.

The ThemeModel is the single source of truth. Editors write to it,
the preview reads from it. Changes fire callbacks so the preview
updates instantly.
"""

import json
import logging
import os
import shutil

from . import theme_parser
from . import color_utils

logger = logging.getLogger(__name__)


class ThemeKey:
    """Metadata about a single theme setting key."""

    __slots__ = ("name", "type", "default", "category", "description",
                 "min_val", "max_val", "choices")

    def __init__(self, name, key_type="string", default="", category="General",
                 description="", min_val=None, max_val=None, choices=None):
        self.name = name
        self.type = key_type  # color, font, int, bool, string, filepath, look
        self.default = default
        self.category = category
        self.description = description
        self.min_val = min_val
        self.max_val = max_val
        self.choices = choices  # For enum-like types


def load_theme_keys(json_path=None):
    """Load the theme key registry from theme_keys.json.

    Returns:
        Dict mapping key name to ThemeKey object.
    """
    if json_path is None:
        json_path = os.path.join(os.path.dirname(__file__), "data", "theme_keys.json")
    json_path = os.path.normpath(json_path)

    if not os.path.exists(json_path):
        return {}

    with open(json_path, "r") as f:
        data = json.load(f)

    keys = {}
    for entry in data.get("keys", []):
        tk = ThemeKey(
            name=entry["name"],
            key_type=entry.get("type", "string"),
            default=entry.get("default", ""),
            category=entry.get("category", "General"),
            description=entry.get("description", ""),
            min_val=entry.get("min"),
            max_val=entry.get("max"),
            choices=entry.get("choices"),
        )
        keys[tk.name] = tk
    return keys


class ThemeModel:
    """In-memory model for all theme settings.

    Attributes:
        filepath: Path to the loaded theme file (None for new themes).
        dirty: True if unsaved changes exist.
        values: Dict of current key→value (all strings).
        lines: Parsed ThemeLine list for round-trip writing.
    """

    def __init__(self):
        self.filepath = None
        self.dirty = False
        self.values = {}
        self.lines = []
        self._callbacks = []  # List of (callback_fn, key_filter_or_None)
        self._key_registry = load_theme_keys()
        self._suppress_callbacks = False
        self._temp_dirs = []  # Temp dirs to clean up on exit or reload
        self._theme_dir = None

    @property
    def theme_dir(self):
        """Directory containing the loaded theme file."""
        if self._theme_dir:
            return self._theme_dir
        if self.filepath:
            return os.path.dirname(self.filepath)
        return None

    @theme_dir.setter
    def theme_dir(self, value):
        self._theme_dir = value

    @property
    def is_temp(self):
        """Check if the current theme is located in a temporary directory."""
        if not self.theme_dir:
            return False
        current = os.path.normpath(self.theme_dir)
        for d in self._temp_dirs:
            if current.startswith(os.path.normpath(d)):
                return True
        return False

    def register_temp_dir(self, path):
        """Register a temporary directory to be cleaned up on next load or exit."""
        self._temp_dirs.append(path)

    def _cleanup_temp_dirs(self):
        """Remove any temporary directories from previous imports."""
        for d in self._temp_dirs:
            shutil.rmtree(d, ignore_errors=True)
        self._temp_dirs.clear()

    def load_file(self, filepath):
        """Load a theme from a file.

        Args:
            filepath: Path to default.theme file.
        """
        self._cleanup_temp_dirs()
        self.filepath = os.path.abspath(filepath)
        self.lines = theme_parser.parse_theme_file(filepath)
        self.values = theme_parser.extract_values(self.lines)
        self.dirty = False
        self._fire_callbacks(None)  # None = everything changed

    def load_from_lines(self, lines, filepath=None):
        """Load a theme from pre-parsed lines.

        Args:
            lines: List of ThemeLine objects.
            filepath: Optional associated file path.
        """
        self.filepath = filepath
        self.lines = lines
        self.values = theme_parser.extract_values(lines)
        self.dirty = False
        self._fire_callbacks(None)

    def new_theme(self, name="New Theme", author=""):
        """Create a new empty theme."""
        self._cleanup_temp_dirs()
        self.filepath = None
        self.lines = theme_parser.create_empty_theme(name, author)
        self.values = theme_parser.extract_values(self.lines)
        self.dirty = True
        self._fire_callbacks(None)

    def save(self, filepath=None):
        """Save the theme to a file.

        Args:
            filepath: Path to save to. Uses self.filepath if None.

        Raises:
            ValueError: If no filepath specified and none was loaded.
        """
        target = filepath or self.filepath
        if not target:
            raise ValueError("No filepath specified for saving")

        target_dir = os.path.dirname(os.path.abspath(target))
        current_dir = self.theme_dir

        # Sync model values back to lines
        for key, value in self.values.items():
            theme_parser.update_value(self.lines, key, value)

        # If saving to a new directory, copy existing assets first
        if current_dir and target_dir != current_dir and os.path.exists(current_dir):
            for item in os.listdir(current_dir):
                if item == "default.theme":
                    continue
                src = os.path.join(current_dir, item)
                dst = os.path.join(target_dir, item)
                if not os.path.exists(dst):
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        os.makedirs(target_dir, exist_ok=True)
                        shutil.copy2(src, dst)

        theme_parser.write_theme_file(target, self.lines)
        self.filepath = os.path.abspath(target)
        self.dirty = False

    def get(self, key, default=None):
        """Get a theme value as a string.

        Args:
            key: Theme key name.
            default: Default if key not set. Falls back to registry default.

        Returns:
            String value.
        """
        if key in self.values:
            return self.values[key]
        if default is not None:
            return default
        if key in self._key_registry:
            return self._key_registry[key].default
        return ""

    def get_int(self, key, default=0):
        """Get a theme value as an integer."""
        val = self.get(key)
        if val == "":
            return default
        try:
            return int(val)
        except (ValueError, TypeError):
            return default

    def get_bool(self, key, default=False):
        """Get a theme value as a boolean (1/0)."""
        val = self.get(key)
        if val == "":
            return default
        return val.strip() in ("1", "true", "True", "yes", "Yes")

    def get_color_rgba(self, key, default_hex="#808080"):
        """Get a color value as (r, g, b, a) floats.

        Args:
            key: Theme key name.
            default_hex: Fallback color as #RRGGBB.

        Returns:
            Tuple of (r, g, b, a) floats 0.0–1.0.
        """
        val = self.get(key)
        if not val:
            return color_utils.hex_to_rgba(default_hex)
        try:
            return color_utils.icewm_to_rgba(val)
        except ValueError:
            return color_utils.hex_to_rgba(default_hex)

    def get_color_hex(self, key, default_hex="#808080"):
        """Get a color value as #RRGGBB hex string."""
        val = self.get(key)
        if not val:
            return default_hex
        try:
            return color_utils.icewm_to_hex(val)
        except ValueError:
            return default_hex

    def set(self, key, value):
        """Set a theme value and fire callbacks.

        Args:
            key: Theme key name.
            value: New string value.
        """
        old = self.values.get(key)
        if old == value:
            return

        self.values[key] = value
        theme_parser.update_value(self.lines, key, value)
        self.dirty = True
        self._fire_callbacks(key)

    def set_color(self, key, r, g, b, a=1.0):
        """Set a color value from RGBA floats.

        Converts to IceWM rgb:XX/XX/XX format.
        """
        self.set(key, color_utils.rgba_to_icewm(r, g, b, a))

    def set_color_hex(self, key, hex_color):
        """Set a color value from a #RRGGBB hex string.

        Converts to IceWM rgb:XX/XX/XX format.
        """
        self.set(key, color_utils.hex_to_icewm(hex_color))

    def connect(self, callback, key_filter=None):
        """Register a callback for value changes.

        Args:
            callback: Function called as callback(key) where key is the
                      changed key name, or None if everything changed.
            key_filter: If set, only fire for this specific key.
                        Can be a string or a set/list of strings.

        Returns:
            An ID that can be used with disconnect().
        """
        entry = (callback, key_filter)
        self._callbacks.append(entry)
        return id(entry)

    def disconnect(self, callback_id):
        """Remove a callback by its ID."""
        self._callbacks = [e for e in self._callbacks if id(e) != callback_id]

    def _fire_callbacks(self, key):
        """Fire registered callbacks for a key change.

        A failing callback is logged but does not prevent other callbacks
        from executing.
        """
        if self._suppress_callbacks:
            return
        for callback, key_filter in self._callbacks:
            try:
                if key is None or key_filter is None:
                    callback(key)
                elif isinstance(key_filter, str) and key == key_filter:
                    callback(key)
                elif isinstance(key_filter, (set, list, tuple)) and key in key_filter:
                    callback(key)
            except Exception:
                logger.error("Error in model callback %s for key %r",
                             getattr(callback, '__qualname__', callback),
                             key, exc_info=True)

    def batch_update(self, updates):
        """Apply multiple value changes, firing callbacks once at the end.

        Args:
            updates: Dict of key→value pairs to set.
        """
        self._suppress_callbacks = True
        try:
            for key, value in updates.items():
                self.set(key, value)
        finally:
            self._suppress_callbacks = False
        self.dirty = True
        self._fire_callbacks(None)

    def restore_snapshot(self, snapshot):
        """Restore the model state to a complete snapshot of values.

        Unlike batch_update, this will remove keys that are present in the
        model but absent in the snapshot, ensuring an exact state match.

        Args:
            snapshot: Dict of key→value pairs.
        """
        self._suppress_callbacks = True
        try:
            # Remove keys that were added since the snapshot
            keys_to_remove = set(self.values.keys()) - set(snapshot.keys())
            for k in keys_to_remove:
                del self.values[k]
                theme_parser.remove_key(self.lines, k)

            # Set all keys from the snapshot
            for key, value in snapshot.items():
                self.values[key] = value
                theme_parser.update_value(self.lines, key, value)
        finally:
            self._suppress_callbacks = False
        self.dirty = True
        self._fire_callbacks(None)

    def get_keys_by_category(self, category):
        """Get all registered keys in a given category.

        Returns:
            List of ThemeKey objects.
        """
        return [tk for tk in self._key_registry.values() if tk.category == category]

    def get_categories(self):
        """Get sorted list of all key categories."""
        cats = set()
        for tk in self._key_registry.values():
            cats.add(tk.category)
        return sorted(cats)

    @property
    def key_registry(self):
        """Access the theme key registry."""
        return self._key_registry
