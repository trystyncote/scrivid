from __future__ import annotations

from ..abc import Qualm

from ._add_to_list import add_qualm
from ._coordinates import ImageCoordinates
from ._index import Index

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._file_objects.images import ImageReference


def _above(a: ImageCoordinates, b: ImageCoordinates):
    return a.y_prime < b.y


def _left_of(a: ImageCoordinates, b: ImageCoordinates):
    return a.x_prime < b.x


class DrawingConfliction(Qualm):
    __slots__ = ("image_a", "image_b", "index")

    code = "D101"
    severity = 4

    def __init__(self, index: int, image_a: ImageReference, image_b: ImageReference):
        self.image_a = image_a
        self.image_b = image_b
        self.index = Index(index)

    def __repr__(self):
        image_a = self.image_a
        image_b = self.image_b
        index = self.index

        return f"{self.__class__.__name__}({index=}, {image_a=}, {image_b=})"

    def _comparison(self, other) -> bool:
        return self.image_a is other.image_a and self.image_b is other.image_b

    def _message(self) -> str:
        return f"images with IDs \'{self.image_a.ID}\' and \'{self.image_b.ID}\' overlap with each other"

    @classmethod
    def check(cls, qualms: list[Qualm], index: int, image_a: ImageReference, image_b: ImageReference):
        if not image_a.is_opened:
            image_a.open()
        if not image_b.is_opened:
            image_b.open()

        a = ImageCoordinates(image_a)
        b = ImageCoordinates(image_b)

        if _left_of(a, b) or _left_of(b, a):
            return

        if _above(a, b) or _above(b, a):
            return

        add_qualm(qualms, cls, index, image_a, image_b)
