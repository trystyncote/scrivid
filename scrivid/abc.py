from __future__ import annotations

from . import errors

from abc import ABC, abstractmethod
import operator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .properties import Properties

    from typing import Hashable


class Adjustment(ABC):
    __slots__ = ()

    _ID: Hashable
    activation_time: int

    def __eq__(self, other) -> bool:
        return self._comparison(other, operator.eq)

    def __ge__(self, other) -> bool:
        return self._comparison(other, operator.ge)

    def __gt__(self, other) -> bool:
        return self._comparison(other, operator.gt)

    def __le__(self, other) -> bool:
        return self._comparison(other, operator.le)

    def __lt__(self, other) -> bool:
        return self._comparison(other, operator.lt)

    def __ne__(self, other) -> bool:
        return self._comparison(other, operator.ne)

    def __init_subclass__(cls):
        if not isinstance(getattr(cls, "activation_time", None), property):
            raise errors.TypeError(
                "abc.Adjustment subclass method `activation_time` must be implemented as a property."
            )

    def _comparison(self, other, operation):
        if not isinstance(other, Adjustment):
            raise errors.TypeError(f"Expected type Adjustment, got type \'{other.__class__.__name__}\'")
        else:
            return operation(self.activation_time, other.activation_time)

    @property
    @abstractmethod
    def activation_time(self):
        raise NotImplementedError

    @abstractmethod
    def _enact(self) -> Properties:
        raise NotImplementedError


class Qualm(ABC):
    __slots__ = ()

    code: str
    severity: int

    def __str__(self) -> str:
        message = self._message()
        return f":{self.code}:{self.severity}: {message}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Qualm):
            raise errors.TypeError(f"Expected type Qualm, got type \'{other.__class__.__name__}\'")
        elif type(self) is not type(other):
            return False
        else:
            return self._comparison(other)

    @abstractmethod
    def _comparison(self, other) -> bool:
        raise NotImplementedError

    @abstractmethod
    def _message(self) -> str:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def check(self):
        raise NotImplementedError
