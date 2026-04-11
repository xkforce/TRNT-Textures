from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass(frozen=True)
class AppConfig:
    """
    Fully resolved application configuration.
    """

    paths: PathConfig
    blends: BlendConfig


@dataclass(slots=True)
class PathConfig:
    """
    Path configuration loaded from the YAML file.
    All paths are resolved relative to main.py later.
    """

    input_dir: Path
    output_dir: Path


@dataclass(slots=True)
class BlendConfig:
    """
    Collection of blend configurations indexed by texture name.
    """

    textures: List[TexturePipelineConfig]


@dataclass(frozen=True)
class TexturePipelineConfig:
    """
    Full processing configuration for a single texture.
    """

    texture_name: str
    colors: List[ColorSource]
    modes: List[BlendModeSpec]
    chain: bool

    def __repr__(self) -> str:
        return f"TexturePipelineConfig(texture_name={self.texture_name!r}, colors={self.colors!r}, modes={self.modes!r}, chain={self.chain!r})"


@dataclass(frozen=True)
class ColorSource:
    """
    Represents a color input, either a file or a hex color.
    """

    file_name: Optional[str] = None
    hex_color: Optional[str] = None
    color_name: Optional[str] = None


@dataclass(frozen=True)
class BlendModeSpec:
    """
    Describes a single blend mode invocation.
    Example: mix(0.2), multiply
    """

    name: str
    args: List[float]
