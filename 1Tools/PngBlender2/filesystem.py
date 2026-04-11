from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from errors import report_error
from models import PathConfig


@dataclass(slots=True)
class ResolvedPaths:
    """
    Fully resolved filesystem paths used by the application.
    """

    base_dir: Path
    input_dir: Path
    textures_dir: Path
    colors_dir: Path
    output_dir: Path
    converted_dir: Path
    generated_dir: Path

    def __str__(self) -> str:
        """
        Return a human-readable tree representation of the resolved paths.
        """
        return (
            "ResolvedPaths\n"
            f"├── base_dir: {self.base_dir}\n"
            "├── input/\n"
            f"│   ├── textures: {self.textures_dir}\n"
            f"│   └── colors:   {self.colors_dir}\n"
            "└── output/\n"
            f"    ├── converted: {self.converted_dir}\n"
            f"    └── generated: {self.generated_dir}"
        )


class FilesystemResolver:
    """
    Resolves and validates filesystem paths for PngMerger2.
    """

    def __init__(self, path_config: PathConfig) -> None:
        self._path_config = path_config

    def resolve(self) -> ResolvedPaths:
        """
        Resolve all filesystem paths relative to main.py.

        Returns:
            ResolvedPaths object.
        """
        base_dir = self._get_base_dir()

        input_dir = base_dir / self._path_config.input_dir
        output_dir = base_dir / self._path_config.output_dir

        textures_dir = input_dir / "textures"
        colors_dir = input_dir / "colors"

        converted_dir = output_dir / "converted"
        generated_dir = output_dir / "generated"

        self._validate_input_dir(input_dir)
        self._validate_input_subdir(textures_dir, "textures")
        self._validate_input_subdir(colors_dir, "colors")

        self._ensure_output_dir(output_dir)
        self._ensure_output_dir(converted_dir)
        self._ensure_output_dir(generated_dir)

        return ResolvedPaths(
            base_dir=base_dir,
            input_dir=input_dir,
            textures_dir=textures_dir,
            colors_dir=colors_dir,
            output_dir=output_dir,
            converted_dir=converted_dir,
            generated_dir=generated_dir,
        )

    def _get_base_dir(self) -> Path:
        """
        Determine the directory containing main.py.

        Returns:
            Base directory path.
        """
        return Path(__file__).resolve().parent

    def _validate_input_dir(self, path: Path) -> None:
        """
        Validate the main input directory.

        Args:
            path: Input directory path.
        """
        if not path.exists():
            report_error(f"Input directory does not exist: {path}")
        elif not path.is_dir():
            report_error(f"Input path is not a directory: {path}")

    def _validate_input_subdir(self, path: Path, name: str) -> None:
        """
        Validate an input subdirectory.

        Args:
            path: Subdirectory path.
            name: Human-readable directory name.
        """
        if not path.exists():
            report_error(f"Missing input/{name} directory: {path}")
        elif not path.is_dir():
            report_error(f"input/{name} is not a directory: {path}")

    def _ensure_output_dir(self, path: Path) -> None:
        """
        Ensure an output directory exists.

        Args:
            path: Output directory path.
        """
        try:
            path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            report_error(f"Failed to create output directory {path}: {exc}")
