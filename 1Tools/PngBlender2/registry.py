from collections.abc import Callable
from typing import Dict

from models import BlendModeSpec
from blends import BlendStrategy
from blends import MixBlend
from blends import MixboxBlend
from blends import MultiplyBlend
from blends import NoOpBlendStrategy
from blends import PenteractBlend
from errors import report_error


class BlendStrategyRegistry:
    def __init__(self) -> None:
        self._registry: Dict[str, Callable[[BlendModeSpec], BlendStrategy]] = {
            "noop": self._noop,
            "mix": self._mix,
            "multiply": self._multiply,
            "mixbox": self._mixbox,
            "penteract": self._penteract,
        }

    def resolve(self, spec: BlendModeSpec) -> BlendStrategy:
        name = spec.name.lower()

        if name not in self._registry:
            report_error(f"Unknown blend mode: {spec.name}")
            return NoOpBlendStrategy()

        return self._registry[name](spec)

    def _noop(self, spec: BlendModeSpec):
        return NoOpBlendStrategy()

    def _mix(self, spec: BlendModeSpec):
        if not spec.args:
            report_error("mix() requires a weight argument")
            return NoOpBlendStrategy()
        return MixBlend(spec.args[0])

    def _multiply(self, spec: BlendModeSpec):
        return MultiplyBlend()

    def _mixbox(self, spec: BlendModeSpec):
        if not spec.args:
            report_error("mixbox() requires a weight argument")
            return NoOpBlendStrategy()
        return MixboxBlend(spec.args[0])

    def _penteract(self, spec: BlendModeSpec):
        return PenteractBlend(int(spec.args[0]) if spec.args else None)
