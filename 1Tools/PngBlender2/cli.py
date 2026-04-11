from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

from enums import Mode


class CliArguments:
    """
    Container object holding parsed CLI arguments.
    """

    def __init__(
        self,
        *,
        config_path: Path,
        mode: Mode,
    ) -> None:
        self.config_path = config_path
        self.mode = mode


def _build_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="PngBlender2",
        description=(
            "PngBlender2 is a CLI tool for converting and merging PNG/PNM images "
            "based on a YAML configuration file."
        ),
        add_help=False,  # we handle help manually to support -?
    )

    # Help flags
    parser.add_argument(
        "-h",
        "--help",
        "-?",
        action="help",
        help="Show this help message and exit.",
    )

    # Positional YAML config path
    parser.add_argument(
        "config",
        nargs="?",
        type=Path,
        help="Path to the YAML configuration file.",
    )

    # Mode selection
    parser.add_argument(
        "--mode",
        choices=[m.value for m in Mode],
        default=Mode.MERGER.value,
        help="Operating mode (default: merger).",
    )

    return parser


def parse_cli_arguments(argv: list[str] | None = None) -> CliArguments:
    """
    Parse CLI arguments and return them as a structured object.

    Args:
        argv:
            Optional argument list (useful for testing). If None, sys.argv is used.

    Returns:
        Parsed CLI arguments.

    Raises:
        SystemExit:
            If required arguments are missing or invalid.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Enforce config path unless help was invoked
    if args.config is None:
        parser.error("the following arguments are required: config")

    return CliArguments(
        config_path=args.config,
        mode=Mode(args.mode),
    )
