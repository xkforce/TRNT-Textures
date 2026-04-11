from __future__ import annotations

from pathlib import Path

from PIL import Image

from registry import BlendStrategyRegistry
from errors import report_error, report_info
from filesystem import ResolvedPaths
from images import ImageLoader, ImageSaver, ColorImageFactory
from models import ColorSource, TexturePipelineConfig
from blends import BlendStrategy


class TextureMerger:
    """
    Generates output textures by applying blend pipelines.
    """

    def __init__(
        self,
        *,
        loader: ImageLoader,
        saver: ImageSaver,
        registry: BlendStrategyRegistry,
        color_factory: ColorImageFactory,
    ) -> None:
        self._loader = loader
        self._saver = saver
        self._registry = registry
        self._color_factory = color_factory

    def merge(
        self,
        paths: ResolvedPaths,
        blends: list[TexturePipelineConfig],
    ) -> None:
        """
        Execute the merger pipeline.
        """
        for texture_blend in blends:
            report_info(f"Processing {texture_blend.texture_name}")
            self._process_texture(paths, texture_blend)

    def _process_texture(
        self,
        paths: ResolvedPaths,
        blend: TexturePipelineConfig,
    ) -> None:
        texture_path = paths.textures_dir / blend.texture_name

        base_image = self._loader.load(texture_path)
        if base_image is None:
            report_error(f"Base texture missing or invalid: {texture_path}")
            return

        # Resolve blend strategies once per texture
        strategies = [self._registry.resolve(mode) for mode in blend.modes]

        for color in blend.colors:
            self._process_color(
                paths=paths,
                base_image=base_image,
                texture_name=blend.texture_name,
                color=color,
                strategies=strategies,
            )

    def _process_color(
        self,
        *,
        paths: ResolvedPaths,
        base_image: Image.Image,
        texture_name: str,
        color: ColorSource,
        strategies: list[BlendStrategy],
    ) -> None:
        """
        Apply all blend modes for a single color and generate one output image.
        """
        layer_image, layer_name = self._resolve_layer(
            paths,
            base_image,
            color,
        )

        if layer_image is None or layer_name is None:
            return

        result = base_image.copy()

        for strategy in strategies:
            report_info(f"  - Applying {strategy.__class__.__name__} to {layer_name}")
            result = strategy.apply(result, layer_image)

        output_name = f"{layer_name}{Path(texture_name).stem}.png"
        target_path = paths.generated_dir / output_name

        self._saver.save_png(result, target_path)

    def _resolve_layer(
        self,
        paths: ResolvedPaths,
        base_image: Image.Image,
        layer: ColorSource,
    ) -> tuple[Image.Image | None, str | None]:
        """
        Resolve a color source into an image and name prefix.
        """
        # File-based color
        if layer.file_name:
            path = paths.colors_dir / layer.file_name
            image = self._loader.load(path)
            if image is None:
                report_error(f"Blend layer image missing: {path}")
                return None, None

            return image, Path(layer.file_name).stem

        # Hex color
        if layer.hex_color and layer.color_name:
            image = self._color_factory.create_solid_color(
                size=base_image.size,
                hex_color=layer.hex_color,
            )
            return image, layer.color_name

        report_error("Invalid blend layer definition.")
        return None, None
