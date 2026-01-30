from __future__ import annotations

from .. import errors, properties
from .._utils.sentinel_objects import sentinel
from ..file_access import call_close, FileAccess

from copy import copy, deepcopy
from pathlib import Path
from typing import TYPE_CHECKING
import weakref

from PIL import Image

if TYPE_CHECKING:
    from collections.abc import Hashable
    from typing import TypeAlias

    Properties: TypeAlias = properties.Properties
    VisibilityStatus: TypeAlias = properties.VisibilityStatus


_NS = sentinel("_NOT_SPECIFIED")
EXCLUDED = properties.EXCLUDED


class ImageFileReference:
    __slots__ = ("_file", "_file_handler", "_pixel_handler")

    def __init__(self, file: str | Path, /):
        if not isinstance(file, Path):
            file = Path(file)

        self._file = file
        self._file_handler = None
        self._pixel_handler = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self._file!r}, "
            + ("is_opened" if self._file_handler is not None else "is_closed")
            + ")"
        )

    @property
    def is_opened(self):
        return self._file_handler is not None

    def get_image_height(self):
        if not self.is_opened:
            return None
        else:
            return self._file_handler.height

    def get_image_width(self):
        if not self.is_opened:
            return None
        else:
            return self._file_handler.width

    def get_pixel_value(self, coordinates: tuple[int, int]):
        if not self.is_opened:
            return None
        else:
            return self._pixel_handler.__getitem__(coordinates)

    def open(self):
        if self._file_handler is not None:
            return
        self._file_handler = Image.open(self._file)
        self._pixel_handler = self._file_handler.load()

    def close(self):
        if self._file_handler is None:
            return
        self._file_handler.close()
        self._file_handler = None
        self._pixel_handler = None


class ImageReference:
    __slots__ = ("_file", "_finalizer", "_ID", "_properties", "__weakref__")

    _file: FileAccess
    _finalizer: weakref.finalize
    _ID: Hashable
    _properties: Properties

    def __init__(
            self,
            ID: Hashable,
            file: FileAccess,
            properties: Properties,
            /
    ):
        self._file = file
        self._finalizer = weakref.finalize(self, call_close, self._file)
        self._ID = ID
        self._properties = properties

    def __repr__(self):
        id = self._ID
        file = self._file
        properties = self._properties

        return f"{self.__class__.__name__}({id=}, {file=}, {properties=})"

    def __hash__(self):
        return hash(self._ID)

    # I'm allowing both lowercase and uppercase 'ID' access, since I'm
    # primarily using the uppercase equivalent to prevent name shadowing.
    @property
    def id(self):
        return self._ID

    @property
    def ID(self):
        return self._ID

    @property
    def is_opened(self):
        return self._file.is_opened

    @property
    def layer(self):
        return self._properties.layer

    @property
    def scale(self):
        return self._properties.scale

    @property
    def visibility(self):
        return self._properties.visibility

    @property
    def x(self):
        return self._properties.x

    @property
    def y(self):
        return self._properties.y

    def copy(self, new_ID: Hashable):
        c = copy(self)
        c._ID = new_ID
        return c

    def deepcopy(self, new_ID: Hashable, memo: dict | None = None):
        if memo is None:
            memo = {}
        dc = deepcopy(self, memo)
        dc._ID = new_ID
        return dc

    def get_image_height(self):
        self._file: ImageFileReference
        return self._file.get_image_height()

    def get_image_width(self):
        self._file: ImageFileReference
        return self._file.get_image_width()

    def get_pixel_value(self, coordinates: tuple[int, int]):
        self._file: ImageFileReference
        return self._file.get_pixel_value(coordinates)

    def open(self):
        # ImageReference is not responsible for opening/closing a file. It's
        # purpose is to hold the data for it. As such, it only calls the 'open'
        # method of its ._file attribute.
        self._file.open()

    def close(self):
        # This 'close' method is automatically called when the object is
        # deleted, but ImageReference is not responsible for what comes out of
        # ._file.close(). Make sure the FileAccess-like class returns early if
        # the file is closed, because this method will not catch it.
        self._file.close()


def create_image_reference(
        ID: Hashable,
        file: str | Path | FileAccess,
        properties_: Properties | _NS = _NS,
        /, *,
        layer: int | EXCLUDED = EXCLUDED,
        scale: int | EXCLUDED = EXCLUDED,
        visibility: VisibilityStatus | EXCLUDED = EXCLUDED,
        x: int | EXCLUDED = EXCLUDED,
        y: int | EXCLUDED = EXCLUDED
) -> ImageReference:
    # ...
    if isinstance(file, str):
        file = Path(file)
    if isinstance(file, Path):
        file = ImageFileReference(file)

    if properties_ is _NS:
        properties_ = properties.create(
            layer=layer,
            scale=scale,
            visibility=visibility,
            x=x,
            y=y
        )
    else:
        for name, attr in (
                ("layer", layer),
                ("scale", scale),
                ("visibility", visibility),
                ("x", x),
                ("y", y)
        ):
            if attr is not EXCLUDED:
                raise errors.AttributeError(f"Attribute \'{name}\' should not be specified if \'properties\' is.")

    return ImageReference(ID, file, properties_)
