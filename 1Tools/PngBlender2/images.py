from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

from PIL import Image, UnidentifiedImageError

from errors import report_error


SUPPORTED_EXTENSIONS = (".png", ".pnm")


class ImageLoader:
    """
    Loads images from disk in a unified way.

    All loaded images are converted to RGBA.
    """

    def load(self, path: Path) -> Image.Image | None:
        """
        Load an image from disk.

        Args:
            path: Path to the image file.

        Returns:
            PIL Image in RGBA mode, or None on failure.
        """
        if not path.exists():
            report_error(f"Image file does not exist: {path}")
            return None

        if not path.is_file():
            report_error(f"Image path is not a file: {path}")
            return None

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            report_error(f"Unsupported image format: {path}")
            return None

        try:
            with Image.open(path) as img:
                return img.convert("RGBA")
        except UnidentifiedImageError:
            report_error(f"Unrecognized image format: {path}")
        except Exception as exc:
            report_error(f"Failed to load image {path}: {exc}")

        return None


class ImageSaver:
    """
    Saves images to disk in a safe and consistent way.
    """

    def save_png(self, image: Image.Image, path: Path) -> None:
        """
        Save an image as a PNG file.

        Args:
            image: PIL Image to save.
            path: Target file path.
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            image.save(path, format="PNG")
        except Exception as exc:
            report_error(f"Failed to save image {path}: {exc}")


class ColorImageFactory:
    """
    Creates image layers from color definitions.
    """

    def create_solid_color(
        self,
        *,
        size: tuple[int, int],
        hex_color: str,
    ) -> Image.Image:
        """
        Create a solid-color RGBA image.

        Args:
            size: (width, height) of the image.
            hex_color: Color in '#RRGGBB' format.

        Returns:
            PIL Image filled with the given color.
        """
        rgba = hex_to_rgba(hex_color)
        return Image.new("RGBA", size, rgba)


def iter_image_files(directory: Path) -> Iterable[Path]:
    """
    Iterate over supported image files in a directory.

    Args:
        directory: Directory to scan.

    Yields:
        Paths to image files.
    """
    if not directory.exists():
        return

    for path in directory.iterdir():
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def hex_to_rgba(hex_color: str) -> Tuple[int, int, int, int]:
    """
    Convert a hex color string to an RGBA tuple.

    Args:
        hex_color: Color in the form '#RRGGBB'.

    Returns:
        RGBA color tuple.
    """
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return r, g, b, 255
