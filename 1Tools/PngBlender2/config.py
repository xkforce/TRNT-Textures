from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from errors import report_error
from models import (
    AppConfig,
    BlendConfig,
    BlendModeSpec,
    ColorSource,
    PathConfig,
    TexturePipelineConfig,
)


_HEX_COLOR_PATTERN = re.compile(r"^#([0-9a-fA-F]{6})\(([^)]+)\)$")

_MODE_PATTERN = re.compile(r"^(?P<name>[a-zA-Z_]+)(?:\((?P<args>[0-9.,\s]+)\))?$")


class ConfigLoader:
    """
    Loads and validates the application YAML configuration.
    """

    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path

    def load(self) -> AppConfig:
        """
        Load the YAML configuration file and return a typed AppConfig.

        Returns:
            Parsed application configuration.
        """
        data = self._load_yaml()
        paths = self._parse_paths(data.get("paths", {}))
        blends = self._parse_blends(data.get("blend", {}))

        return AppConfig(paths=paths, blends=blends)

    def _load_yaml(self) -> dict[str, Any]:
        """
        Load raw YAML data from disk.

        Returns:
            Raw YAML data as dictionary.
        """
        try:
            with self._config_path.open("r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
        except Exception as exc:
            report_error(f"Failed to load YAML file: {exc}")
            return {}

    def _parse_paths(self, raw: dict[str, Any]) -> PathConfig:
        """
        Parse the `paths` section.
        """
        input_dir = Path(raw.get("input", "input"))
        output_dir = Path(raw.get("output", "output"))

        return PathConfig(
            input_dir=input_dir,
            output_dir=output_dir,
        )

    def _parse_blends(self, raw: Any) -> BlendConfig:
        """
        Parse the `blend` section.

        Expected structure per texture:
            chain: bool (optional)
            modes: list[str] (optional)
            colors: list[str] (required)
        """
        textures: list[TexturePipelineConfig] = []

        if not isinstance(raw, dict):
            report_error("Blend section must be a mapping.")
            return BlendConfig(textures=[])

        for texture_name, entry in raw.items():
            if not isinstance(entry, dict):
                report_error(f"Blend entry for '{texture_name}' must be a mapping.")
                continue

            chain = bool(entry.get("chain", False))
            colors_raw = entry.get("colors")
            modes_raw = entry.get("modes", [])

            if not isinstance(colors_raw, list) or not colors_raw:
                report_error(
                    f"Blend entry for '{texture_name}' must define "
                    f"a non-empty 'colors' list."
                )
                continue

            colors = self._parse_colors(texture_name, colors_raw)
            modes = self._parse_modes(texture_name, modes_raw)

            # Default to NOOP if no valid modes are defined
            if not modes:
                modes = [BlendModeSpec(name="noop", args=[])]

            textures.append(
                TexturePipelineConfig(
                    texture_name=texture_name,
                    colors=colors,
                    modes=modes,
                    chain=chain,
                )
            )

        return BlendConfig(textures=textures)

    def _parse_colors(
        self,
        texture_name: str,
        raw_entries: Any,
    ) -> list[ColorSource]:
        """
        Parse the `colors` list for a texture.
        """
        colors: list[ColorSource] = []

        for entry in raw_entries:
            if not isinstance(entry, str):
                report_error(f"Invalid color entry for '{texture_name}': {entry!r}")
                continue

            color = self._parse_color_entry(texture_name, entry)
            if color:
                colors.append(color)

        return colors

    def _parse_color_entry(
        self,
        texture_name: str,
        value: str,
    ) -> ColorSource | None:
        """
        Parse a single color entry.

        Accepted formats:
            - filename.png / filename.pnm
            - #RRGGBB(name)
        """
        match = _HEX_COLOR_PATTERN.match(value)
        if match:
            return ColorSource(
                hex_color=f"#{match.group(1)}",
                color_name=match.group(2),
            )

        if value.lower().endswith((".png", ".pnm")):
            return ColorSource(file_name=value)

        report_error(f"Malformed color entry for '{texture_name}': '{value}'")
        return None

    def _parse_modes(
        self,
        texture_name: str,
        raw_entries: Any,
    ) -> list[BlendModeSpec]:
        """
        Parse the `modes` list for a texture.

        Modes are parsed structurally but not validated semantically yet.
        """
        if not raw_entries:
            return []

        if not isinstance(raw_entries, list):
            report_error(f"'modes' entry for '{texture_name}' must be a list.")
            return []

        modes: list[BlendModeSpec] = []

        for entry in raw_entries:
            if not isinstance(entry, str):
                report_error(f"Invalid mode entry for '{texture_name}': {entry!r}")
                continue

            match = _MODE_PATTERN.match(entry.strip())
            if not match:
                report_error(f"Malformed mode entry for '{texture_name}': '{entry}'")
                continue

            name = match.group("name").lower()
            args_raw = match.group("args")

            args: list[float] = []
            if args_raw:
                try:
                    args = [float(v.strip()) for v in args_raw.split(",")]
                except ValueError:
                    report_error(
                        f"Invalid arguments in mode '{entry}' for '{texture_name}'"
                    )
                    continue

            modes.append(BlendModeSpec(name=name, args=args))

        return modes
