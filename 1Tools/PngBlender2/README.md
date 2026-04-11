# PngBlender2

PngBlender2 is a Python tool for batch editing PNG/PNM textures using a YAML configuration file. It supports blending layers, color transformations, and custom blending strategies, making it perfect for procedural texture generation or automated image adjustments.
Developed for [The Road not taken](https://github.com/xkforce/The-Road-Not-Taken).

## Features

* Merge textures with multiple color layers
* Apply various blending modes including:

  * `mix(weight)` — linear RGB blending
  * `multiply` — standard multiplicative blend
  * `mixbox(weight)` — perceptual color mixing using `mixbox`
  * `penteract(average)` — procedural blend using grayscale average normalization
* Supports both PNM and PNG input
* [NOT YET IMPLEMENTED] Chain multiple colors in a single image with `chain: true`
* CLI-driven, fully configurable via YAML

## Usage

```bash
uv sync
uv run main.py path/to/config.yml [options]
```

### Available CLI flags

* `-h, --help, -?` : Show help message
* `--default-mode MODE` : Override default blend mode if not specified in YAML
* Additional flags may control converter/merger mode, output directories, etc.

## YAML Configuration

Example configuration:

```yaml
paths:
  input: input
  output: output

blend:
  stone.pnm:
    chain: false
    modes:
      - mix(0.2)
      - multiply
    colors:
      - red.png
      - #FFFFFF(white)

  marble.png:
    chain: true
    modes:
      - mixbox(0.5)
      - penteract(128)
    colors:
      - #3AB3DA(blue)
      - green.pnm
```

### Configuration Sections

* `paths`:

  * `input`: Directory containing `textures` and `colors` subfolders
  * `output`: Directory containing `converted` and `generated` subfolders

* `blend`:

  * Key: Texture filename (relative to `textures` folder)
  * `chain`: Boolean, if true all colors are applied to a single image
  * `modes`: List of blend mode invocations
  * `colors`: List of color sources, either image filenames or hex values with names

## Output

* `converted/` : PNM-to-PNG conversions (converter mode)
* `generated/` : Final merged PNGs (merger mode)

Output naming scheme:

```
[colorname][texturename].png
```

When `chain: true` the output is named the same as the base texture.

## Extending

* Add new blending strategies by implementing `BlendStrategy` and registering in `BlendStrategyRegistry`
* Modes accept arguments via YAML (`mix(0.3)`, `penteract(128)`, etc.)
* Fully compatible with chaining and multi-layer merges
