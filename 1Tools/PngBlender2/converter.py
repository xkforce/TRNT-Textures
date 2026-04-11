from __future__ import annotations

from pathlib import Path

from filesystem import ResolvedPaths
from images import ImageLoader, ImageSaver, iter_image_files


class TextureConverter:
    """
    Converts texture images from PNM to PNG format.
    """

    def __init__(
        self,
        *,
        loader: ImageLoader,
        saver: ImageSaver,
    ) -> None:
        self._loader = loader
        self._saver = saver

    def convert(self, paths: ResolvedPaths) -> None:
        """
        Convert all PNM texture files to PNG.

        Args:
            paths: Resolved filesystem paths.
        """
        for source_path in iter_image_files(paths.textures_dir):
            if source_path.suffix.lower() != ".pnm":
                continue

            image = self._loader.load(source_path)
            if image is None:
                continue

            target_path = self._build_target_path(
                source_path,
                paths.converted_dir,
            )

            self._saver.save_png(image, target_path)

    def _build_target_path(self, source: Path, target_dir: Path) -> Path:
        """
        Build the target PNG path for a converted image.

        Args:
            source: Source PNM file path.
            target_dir: Output directory.

        Returns:
            Target PNG file path.
        """
        return target_dir / f"{source.stem}.png"
