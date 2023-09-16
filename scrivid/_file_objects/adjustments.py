from __future__ import annotations

from . import images
from .. import errors
from ._operations import comparison_function, return_not_implemented, should_raise_operator_error
from ._status import Status

from abc import abstractmethod


class RootAdjustment:
    __slots__ = ("_activation_time",)

    def __init__(self, activation_time: int):
        self._activation_time = activation_time

    def __repr__(self):
        return f"{self.__class__.__name__}(activation_time={self._activation_time!r})"

    def __hash__(self):
        return hash(self._activation_time)

    """ self << other """
    __lshift__ = return_not_implemented()  # This function does not handle the
    # error that should be raised for incorrect syntax, because doing so in the
    # forward function would be too eager. If someone inherits from
    # ImageReference and wants this syntax to work, we should give it a chance
    # to invoke the reverse method.

    def __rlshift__(self, other):
        """ other << self """
        if not isinstance(other, images.ImageReference):
            raise errors.TypeError(f"Expected types ImageReference, got type {other.__name__}")
        other.add_adjustment(self)

    def __rshift__(self, other):
        """ self >> other """
        if not isinstance(other, images.ImageReference):
            raise errors.TypeError(f"Expected types ImageReference, got type {other.__name__}")
        other.add_adjustment(self)

    """ other >> self """
    __rrshift__ = should_raise_operator_error(correct=">>", reverse="<<")

    @property
    def activation_time(self):
        return self._activation_time

    @abstractmethod
    def utilize(self, reference):
        raise NotImplementedError


""" self == other """
RootAdjustment.__eq__ = comparison_function("_activation_time", "==", RootAdjustment)

""" self >= other """
RootAdjustment.__ge__ = comparison_function("_activation_time", ">=", RootAdjustment)

""" self > other """
RootAdjustment.__gt__ = comparison_function("_activation_time", ">", RootAdjustment)

""" self <= other """
RootAdjustment.__le__ = comparison_function("_activation_time", "<=", RootAdjustment)

""" self < other """
RootAdjustment.__lt__ = comparison_function("_activation_time", "<", RootAdjustment)

""" self != other """
RootAdjustment.__ne__ = comparison_function("_activation_time", "!=", RootAdjustment)


class HideAdjustment(RootAdjustment):
    def utilize(self, reference):
        reference._status = Status.HIDE


class ShowAdjustment(RootAdjustment):
    def utilize(self, reference):
        reference._status = Status.SHOW