from __future__ import annotations

from . import errors
from ._utils.sentinel_objects import sentinel

from pathlib import Path


_NOT_SPECIFIED = sentinel("_NOT_SPECIFIED")


def _check_attribute_presense(metadata, name):
    value = getattr(metadata, name, _NOT_SPECIFIED)
    if value is _NOT_SPECIFIED:
        raise errors.AttributeError(f"Metadata object missing required attribute \'{name}\'.")


def _check_attribute_type(metadata, name, types, validator):
    value = getattr(metadata, name, _NOT_SPECIFIED)
    if value is _NOT_SPECIFIED:
        return

    if not validator(value):
        raise errors.AttributeError(f"Metadata attribute \'{name}\' expected type(s) {types}; got type {type(value)}.")


def _is_specified(obj):
    return obj is not _NOT_SPECIFIED


class _TypeValidatingCallables:
    @staticmethod
    def int_(value):
        return isinstance(value, int) and not isinstance(value, bool)

    @staticmethod
    def str_(value):
        return isinstance(value, str)

    @staticmethod
    def str_or_path(value):
        return isinstance(value, str) or isinstance(value, Path)

    @staticmethod
    def tuple_of_two_ints(value):
        return (
            isinstance(value, tuple)
            and len(value) == 2
            and _TypeValidatingCallables.int_(value[0])
            and _TypeValidatingCallables.int_(value[1])
        )


class Metadata:
    """
    Metadata stores all of the attributes for a Scrivid-generated video.
    The attributes are not required to be specified on construction, but
    four attributes must be specified before the Metadata is passed into
    Scrivid to be compiled into a video.

    The four required attributes are frame_rate, save_location, video_name,
    window_size.

    :param frame_rate: `(int)` The frame rate of the video.
    :param save_location: `(str | Path)` The path of the location where the
        file should be saved. Recommended to be a pathlib.Path object.
    :param video_name: `(str)` The final name of the video file that's to be
        generated.
    :param window_size: `(tuple[int, int])` A tuple of (width, height) for the
        dimensions of the video.
    """

    __slots__ = ("_window_size", "frame_rate", "save_location", "video_name")

    _window_size: tuple[int, int]

    def __init__(
        self,
        *,
        frame_rate: int | _NOT_SPECIFIED = _NOT_SPECIFIED,
        save_location: str | Path | _NOT_SPECIFIED = _NOT_SPECIFIED,
        video_name: str | _NOT_SPECIFIED = _NOT_SPECIFIED,
        window_size: tuple[int, int] | _NOT_SPECIFIED = _NOT_SPECIFIED
    ):
        if isinstance(save_location, str):
            save_location = Path(save_location)
        self.save_location = save_location

        self._window_size = window_size
        self.frame_rate = frame_rate
        self.video_name = video_name

    @property
    def window_height(self):
        """ Equivalent to `window_size[1]` """
        if self._window_size is _NOT_SPECIFIED:
            return None
        else:
            return self._window_size[1]

    @property
    def window_size(self):
        return self._window_size

    @window_size.setter
    def window_size(self, new_value: tuple[int, int]):
        self._window_size = new_value

    @property
    def window_width(self):
        """ Equivalent to `window_size[0]` """
        if self._window_size is _NOT_SPECIFIED:
            return None
        else:
            return self._window_size[0]

    def _validate(self):
        _check_attribute_presense(self, "frame_rate")
        _check_attribute_presense(self, "save_location")
        _check_attribute_presense(self, "video_name")
        _check_attribute_presense(self, "window_size")

        _check_attribute_type(self, "frame_rate", "int", _TypeValidatingCallables.int_)
        _check_attribute_type(self, "save_location", "str, Path", _TypeValidatingCallables.str_or_path)
        _check_attribute_type(self, "video_name", "str", _TypeValidatingCallables.str_)
        _check_attribute_type(self, "window_size", "tuple[int, int]", _TypeValidatingCallables.tuple_of_two_ints)

        if self.window_width % 2 != 0 or self.window_height % 2 != 0:
            raise errors.AttributeError("Metadata attribute \'window_size\' must contain even numbers.")
