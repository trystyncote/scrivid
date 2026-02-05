from __future__ import annotations

from . import errors

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, Callable


class _ValidatingDescriptor:
    def __init__(self, validator: Callable[[Any], bool], expected: type):
        self._validator = validator
        self._expected = expected

    def __get__(self, obj, *_):
        if obj is None:
            return self
        else:
            return getattr(obj, self._stored_name)

    def __set_name__(self, _, name):
        self._called_name = name
        self._stored_name = f"_{name}"

    def __set__(self, instance, value):
        if not self._validator(value) and value is not None:
            raise errors.AttributeError(
                f"Metadata attribute \'{self._called_name}\' expected type(s) {self._expected}; got type {type(value)}"
                "."
            )
        setattr(instance, self._stored_name, value)

    def __delete__(self, instance):
        setattr(instance, self._stored_name, None)


def _validate_window_size(x: Any, /) -> bool:
    if x is None:
        return True

    if not isinstance(x, (tuple, Sequence)):
        return False

    if len(x) != 2:
        return False

    for x_ in x:
        if not isinstance(x_, int):
            return False

        if x_ % 2 != 0:
            raise errors.AttributeError("Metadata attribute \'window_size\' must contain even numbers.")

    return True


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

    __slots__ = ("_window_size", "_frame_rate", "_save_location", "_video_name")

    frame_rate = _ValidatingDescriptor(lambda x: isinstance(x, int), int)
    save_location = _ValidatingDescriptor(lambda x: isinstance(x, Path), Path)
    video_name = _ValidatingDescriptor(lambda x: isinstance(x, str), str)
    window_size = _ValidatingDescriptor(_validate_window_size, Sequence)

    def __init__(
        self,
        *,
        frame_rate: int | None = None,
        save_location: str | Path | None = None,
        video_name: str | None = None,
        window_size: tuple[int, int] | None = None
    ):
        if isinstance(save_location, str):
            save_location = Path(save_location)
        self.save_location = save_location

        self.window_size = window_size
        self.frame_rate = frame_rate
        self.video_name = video_name

    @property
    def window_height(self):
        """ Equivalent to `window_size[1]` """
        if self.window_size is None:
            return None
        else:
            return self.window_size[1]

    @property
    def window_width(self):
        """ Equivalent to `window_size[0]` """
        if self.window_size is None:
            return None
        else:
            return self._window_size[0]
