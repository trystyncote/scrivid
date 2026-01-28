from __future__ import annotations

from ..abc import Qualm

from ._add_to_list import add_qualm
from ._coordinates import ImageCoordinates
from ._index import Index

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.images import ImageReference


class OutOfRange(Qualm):
    __slots__ = ("image", "index")

    code = "D102"
    severity = 3

    def __init__(self, index: int, image: ImageReference):
        self.index = Index(index)
        self.image = image

    def __repr__(self) -> str:
        image = self.image
        index = self.index

        return f"{self.__class__.__name__}({index=}, {image=})"

    def _comparison(self, other) -> bool:
        return self.image is other.image

    def _message(self) -> str:
        return f"image with ID \'{self.image.ID}\' may be printed outside of canvas boundaries"

    @classmethod
    def check(cls, qualms: list[Qualm], index: int, image: ImageReference, window_size: tuple[int, int]):
        if not image.is_opened:
            image.open()

        a = ImageCoordinates(image)

        if a.x < 0 or a.y < 0:
            add_qualm(qualms, cls, index, image)
            return

        if a.x_prime > window_size[0] or a.y_prime > window_size[1]:
            add_qualm(qualms, cls, index, image)
            return
