from typing import override, Optional
from abc import ABC, abstractmethod
from PIL import Image
import mixbox
import numpy as np

from errors import report_info


class BlendStrategy(ABC):
    """
    Base class for blend strategies.

    Applies a single layer to a base texture.
    """

    @abstractmethod
    def apply(
        self,
        base: Image.Image,
        layer: Image.Image,
    ) -> Image.Image:
        """
        Apply a single layer to the base image.
        """
        raise NotImplementedError


class NoOpBlendStrategy(BlendStrategy):
    """
    Placeholder strategy that returns the base image unchanged.
    """

    @override
    def apply(
        self,
        base: Image.Image,
        layer: Image.Image,
    ) -> Image.Image:
        return base.copy()


class MultiplyBlend(BlendStrategy):
    def apply(
        self,
        base: Image.Image,
        layer: Image.Image,
    ) -> Image.Image:
        base_arr = np.asarray(base, dtype=np.float32)
        layer_arr = np.asarray(layer, dtype=np.float32)

        result = (base_arr * layer_arr) / 255.0

        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image.fromarray(result, mode=base.mode)


class MixBlend(BlendStrategy):
    def __init__(self, weight: float) -> None:
        if not 0.0 <= weight <= 1.0:
            raise ValueError("Mix weight must be between 0 and 1.")
        self._weight = weight

    def apply(
        self,
        base: Image.Image,
        layer: Image.Image,
    ) -> Image.Image:
        base_arr = np.asarray(base, dtype=np.float32)
        layer_arr = np.asarray(layer, dtype=np.float32)

        result = base_arr * (1.0 - self._weight) + layer_arr * self._weight

        result = np.clip(result, 0, 255).astype(np.uint8)
        return Image.fromarray(result, mode=base.mode)


class MixboxBlend(BlendStrategy):
    """
    Perceptual color mixing using Mixbox.

    mixbox.lerp(a.rgb, b.rgb, weight) is applied per pixel.
    """

    def __init__(self, weight: float) -> None:
        if not 0.0 <= weight <= 1.0:
            raise ValueError("mixbox weight must be between 0 and 1.")
        self._weight = weight

    def apply(
        self,
        base: Image.Image,
        layer: Image.Image,
    ) -> Image.Image:
        base_arr = np.asarray(base, dtype=np.uint8)
        layer_arr = np.asarray(layer, dtype=np.uint8)

        # Ensure RGB(A)
        if base_arr.shape[-1] < 3 or layer_arr.shape[-1] < 3:
            raise ValueError("Mixbox requires RGB or RGBA images.")

        height, width, channels = base_arr.shape
        out = base_arr.copy()

        for y in range(height):
            for x in range(width):
                a = base_arr[y, x][:3]
                b = layer_arr[y, x][:3]

                mixed = mixbox.lerp(a, b, self._weight)
                out[y, x][:3] = mixed

        return Image.fromarray(out, mode=base.mode)


class PenteractBlend(BlendStrategy):
    """
    Experimental procedural blend algorithm.

    Uses grayscale averaging, value normalization, and dynamic range
    remapping to generate a new color transformation.
    """

    def __init__(self, average: Optional[int] = None) -> None:
        if average is not None and not 0 <= average <= 255:
            raise ValueError("Penteract average must be between 0 and 255.")
        self._average = average

    def apply(
        self,
        base: Image.Image,
        layer: Image.Image,
    ) -> Image.Image:
        # Ensure RGB
        base_rgb = base.convert("RGB")
        layer_rgb = layer.convert("RGB")

        # --- Step 1: grayscale average ---
        gray = base_rgb.convert("L")
        avg_gray = self._average or int(np.mean(np.asarray(gray)))
        report_info(f"    - Penteract average: {avg_gray}")

        # --- Step 2: flatten images ---
        base_arr = np.asarray(base_rgb, dtype=np.int32)
        layer_arr = np.asarray(layer_rgb, dtype=np.int32)

        flat_base = base_arr.flatten().tolist()
        flat_layer = layer_arr.flatten().tolist()

        if len(flat_base) != len(flat_layer):
            raise ValueError("Base and layer images must have same dimensions.")

        # --- Step 3: first pass ---
        result = []
        for b, c in zip(flat_base, flat_layer):
            if b == 255:
                result.append(255)
            else:
                result.append(b + c - avg_gray)

        # --- Step 4: normalize minimum ---
        min_val = min(result)
        if min_val < 0:
            report_info(f"    - Penteract minimum: {min_val}")
            result = [v if v == 255 else v - min_val for v in result]

        # --- Step 5: normalize maximum ---
        max_val = max(result)
        if max_val > 255:
            report_info(f"    - Penteract maximum: {max_val}")
            result = [v if v == 255 else v + 255 - max_val for v in result]

        # --- Step 6: clamp ---
        result = [255 if v > 255 else 0 if v < 0 else v for v in result]

        # --- Step 7: rebuild image ---
        out_arr = np.array(result, dtype=np.uint8).reshape(base_arr.shape)

        return Image.fromarray(out_arr, mode="RGB")
