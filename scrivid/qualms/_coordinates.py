from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._images import ImageReference


class ImageCoordinates:
    __slots__ = ("x", "x_prime", "y", "y_prime")

    def __init__(self, image: ImageReference):
        x = image.x
        y = image.y

        self.x = x
        self.x_prime = x + image.get_image_width()
        self.y = y
        self.y_prime = y + image.get_image_height()
