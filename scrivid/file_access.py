from __future__ import annotations

from pathlib import Path
from typing import Protocol, runtime_checkable


def call_close(file: FileAccess):
    file.close()


@runtime_checkable
class FileAccess(Protocol):
    """
    FileAccess classes must have two methods: open() and close(). The signature
    of its __init__ method must have one positional-only argument: 'file'.
    """
    def __init__(self, file: str | Path, /): ...
    @property
    def is_opened(self) -> bool: ...
    def open(self): ...
    def close(self): ...


class FileReference:
    __slots__ = ("_file", "_file_handler")

    def __init__(self, file: str | Path, /):
        if not isinstance(file, Path):
            file = Path(file)

        self._file = file
        self._file_handler = None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}({self._file!r}, "
            + ("is_opened" if self._file_handler is not None else "is_closed")
            + ")"
        )

    @property
    def is_opened(self):
        return self._file_handler is not None

    def open(self):
        self._file_handler = self._file.open()

    def close(self):
        if self._file_handler is None:
            return
        self._file_handler.close()
        self._file_handler = None
