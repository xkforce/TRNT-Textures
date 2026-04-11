from __future__ import annotations

from cli import parse_cli_arguments
from config import ConfigLoader
from converter import TextureConverter
from enums import Mode
from filesystem import FilesystemResolver
from images import ImageLoader, ImageSaver, ColorImageFactory
from merger import TextureMerger
from registry import BlendStrategyRegistry


def main() -> None:
    """
    Application entry point.
    """
    args = parse_cli_arguments()

    config = ConfigLoader(args.config_path).load()
    paths = FilesystemResolver(config.paths).resolve()

    loader = ImageLoader()
    saver = ImageSaver()
    color_factory = ColorImageFactory()
    registry = BlendStrategyRegistry()

    match args.mode:
        case Mode.CONVERTER:
            converter = TextureConverter(
                loader=loader,
                saver=saver,
            )
            converter.convert(paths)

        case Mode.MERGER:
            merger = TextureMerger(
                loader=loader,
                saver=saver,
                registry=registry,
                color_factory=color_factory,
            )
            merger.merge(paths, config.blends.textures)

        case _:
            raise RuntimeError("Unhandled application mode")


if __name__ == "__main__":
    main()
