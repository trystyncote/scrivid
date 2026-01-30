from __future__ import annotations

from . import errors
from ._utils import sentinel, SentinelBase

import enum


EXCLUDED = sentinel("EXCLUDED")


def _calculate_append(property_: str, a: Properties, b: Properties):
    a_attr, b_attr = getattr(a, property_), getattr(b, property_)
    return (
        a_attr + b_attr if EXCLUDED not in (a_attr, b_attr)
        else a_attr if a_attr is not EXCLUDED
        else b_attr
    )


def _calculate_replacement(property_: str, a: Properties, b: Properties):
    a_attr, b_attr = getattr(a, property_), getattr(b, property_)
    return a_attr if a_attr is not EXCLUDED else b_attr


class MergeMode(enum.Enum):
    APPEND = enum.auto()
    REPLACEMENT = enum.auto()
    REVERSE_APPEND = enum.auto()
    REVERSE_REPLACEMENT = enum.auto()
    REVERSE_STRICT_REPLACEMENT = enum.auto()
    STRICT_REPLACEMENT = enum.auto()


_APPENDING_MODES = (MergeMode.APPEND, MergeMode.REVERSE_APPEND)
_FORWARD_MODES = (MergeMode.APPEND, MergeMode.REPLACEMENT, MergeMode.STRICT_REPLACEMENT)
_REPLACEMENT_MODES = (
    MergeMode.REPLACEMENT, MergeMode.REVERSE_REPLACEMENT, MergeMode.REVERSE_STRICT_REPLACEMENT,
    MergeMode.STRICT_REPLACEMENT
)
_REVERSE_MODES = (MergeMode.REVERSE_APPEND, MergeMode.REVERSE_REPLACEMENT, MergeMode.REVERSE_STRICT_REPLACEMENT)
_STRICT_MODES = (MergeMode.REVERSE_STRICT_REPLACEMENT, MergeMode.STRICT_REPLACEMENT)


class VisibilityStatus(enum.Enum):
    HIDE = enum.auto()
    SHOW = enum.auto()
    UNKNOWN = enum.auto()


class Properties:
    __slots__ = ("layer", "scale", "visibility", "x", "y")

    def __init__(
            self, *,
            layer: int | SentinelBase = EXCLUDED,
            scale: float | int | SentinelBase = EXCLUDED,
            visibility: VisibilityStatus | SentinelBase = EXCLUDED,
            x: int | SentinelBase = EXCLUDED,
            y: int | SentinelBase = EXCLUDED
    ):
        self.layer = layer
        self.scale = scale
        self.visibility = visibility
        self.x = x
        self.y = y

    def __repr__(self):
        layer = getattr(self, "layer", "<NOT_FOUND>")
        scale = getattr(self, "scale", "<NOT_FOUND>")
        visibility = getattr(self, "visibility", "<NOT_FOUND>")
        x = getattr(self, "x", "<NOT_FOUND>")
        y = getattr(self, "y", "<NOT_FOUND>")

        return f"{self.__class__.__name__}({layer=}, {scale=}, {visibility=}, {x=}, {y=})"

    def __and__(self, other):
        return self.merge(other)

    def _check_confliction(self, other):
        NO_RETURN = sentinel("NO_RETURN")

        for attr in self.__slots__:
            a = getattr(self, attr, NO_RETURN)
            b = getattr(other, attr, NO_RETURN)

            if a is NO_RETURN:
                raise errors.AttributeError(
                    f"Attribute \'{attr}\' not found in {self.__class__.__name__} instance \'{self}\'"
                )
            elif b is NO_RETURN:
                raise errors.AttributeError(
                    f"Attribute \'{attr}\' not found in {other.__class__.__name__} instance \'{other}\'"
                )

            if (EXCLUDED in (a, b)) or (a == b):
                continue

            raise errors.ConflictingAttributesError(
                first_name=attr,
                first_value=a,
                second_name=attr,
                second_value=b
            )

    def merge(self, other: Properties, /, *, mode: MergeMode = MergeMode.STRICT_REPLACEMENT):
        if not isinstance(other, Properties):
            raise errors.TypeError(
                f"Expected Properties object, got type {type(other)}."
            )
        elif mode in _STRICT_MODES:
            self._check_confliction(other)

        if mode in _FORWARD_MODES:
            a, b = self, other
        elif mode in _REVERSE_MODES:
            a, b = other, self

        visibility = _calculate_replacement("visibility", a, b)

        if mode in _REPLACEMENT_MODES:
            layer = _calculate_replacement("layer", a, b)
            scale = _calculate_replacement("scale", a, b)
            x = _calculate_replacement("x", a, b)
            y = _calculate_replacement("y", a, b)
        elif mode in _APPENDING_MODES:
            layer = _calculate_append("layer", a, b)
            scale = _calculate_append("scale", a, b)
            x = _calculate_append("x", a, b)
            y = _calculate_append("y", a, b)

        return self.__class__(layer=layer, scale=scale, visibility=visibility, x=x, y=y)


def create(
        *,
        layer: int | SentinelBase = EXCLUDED,
        scale: float | int | SentinelBase = EXCLUDED,
        visibility: VisibilityStatus | SentinelBase = EXCLUDED,
        x: int | SentinelBase = EXCLUDED,
        y: int | SentinelBase = EXCLUDED
) -> Properties:
    # Define default values for non-required variables. If it's intended to be
    # used specifically for merging, you may wish to instantiate it directly,
    # instead of using this factory function.
    if visibility is EXCLUDED:
        visibility = VisibilityStatus.SHOW
    return Properties(layer=layer, scale=scale, visibility=visibility, x=x, y=y)
