from __future__ import annotations

from .. import abc, properties

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Hashable
    from typing import TypeAlias

    Properties: TypeAlias = properties.Properties


EXCLUDED = properties.EXCLUDED


def _increment_value(
        full_value: float | int | EXCLUDED,
        duration: int,
        length: int,
        precision: float | int
):
    if full_value is EXCLUDED:
        return full_value

    value, remainder = divmod(full_value, duration)
    value *= length
    remainder *= length

    excess_precision = remainder // precision
    if excess_precision < 1:
        return value

    return value + (remainder - (excess_precision * precision))


class HideAdjustment(abc.Adjustment):
    __slots__ = ("_activation_time", "_ID")

    def __init__(self, ID: Hashable, activation_time: int):
        self._ID = ID
        self._activation_time = activation_time

    def __repr__(self) -> str:
        id = self._ID
        activation_time = self._activation_time

        return f"{self.__class__.__name__}({id=!r}, {activation_time=!r})"

    def __hash__(self):
        return hash((self._ID, self._activation_time))

    @property
    def activation_time(self):
        return self._activation_time

    @property
    def id(self):
        return self._ID

    @property
    def ID(self):
        return self._ID

    def _enact(self) -> Properties:
        return properties.Properties(visibility=properties.VisibilityStatus.HIDE)


class MoveAdjustment(abc.Adjustment):
    __slots__ = ("_activation_time", "_change", "_ID", "duration")

    def __init__(
            self,
            ID: Hashable,
            activation_time: int,
            change: properties.Properties,
            duration: int
    ):
        self._change = change
        self.duration = duration
        self._ID = ID
        self._activation_time = activation_time

    def __repr__(self):
        id = self._ID
        activation_time = self._activation_time
        change = self._change
        duration = self.duration

        return f"{self.__class__.__name__}({id=!r}, {activation_time=!r}, {change=!r}, {duration=!r})"

    @property
    def activation_time(self):
        return self._activation_time

    @property
    def change(self):
        return self._change

    @property
    def id(self):
        return self._ID

    @property
    def ID(self):
        return self._ID

    def _enact(self, length: int) -> Properties:
        if self.duration == 1 or self.duration == length:
            return self._change
        else:
            return self._split_change(length)

    def _split_change(self, length: int = 1) -> Properties:
        scale = _increment_value(
            self._change.scale,
            self.duration,
            length,
            0.1
        )
        x = _increment_value(self._change.x, self.duration, length, 1)
        y = _increment_value(self._change.y, self.duration, length, 1)

        return properties.Properties(scale=scale, x=x, y=y)


class ShowAdjustment(abc.Adjustment):
    __slots__ = ("_activation_time", "_ID")

    def __init__(self, ID: Hashable, activation_time: int):
        self._ID = ID
        self._activation_time = activation_time

    def __repr__(self) -> str:
        id = self._ID
        activation_time = self._activation_time

        return f"{self.__class__.__name__}({id=!r}, {activation_time=!r})"

    def __hash__(self):
        return hash((self._ID, self._activation_time))

    @property
    def activation_time(self):
        return self._activation_time

    @property
    def id(self):
        return self._ID

    @property
    def ID(self):
        return self._ID

    def _enact(self) -> Properties:
        return properties.Properties(visibility=properties.VisibilityStatus.SHOW)
