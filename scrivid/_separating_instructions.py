from __future__ import annotations

from . import errors
from .abc import Adjustment
from ._file_objects.images import ImageReference

from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Hashable, TypeAlias

    INSTRUCTIONS: TypeAlias = ImageReference | Adjustment
    REFERENCES: TypeAlias = ImageReference


class SeparatedInstructions:
    __slots__ = ("adjustments", "references")

    adjustments: dict[Hashable, SortedList[Adjustment]]
    references: dict[Hashable, ImageReference]

    def __init__(self):
        self.adjustments = {}
        self.references = {}


def _handle_adjustment(separated_instructions: SeparatedInstructions, adjustment: Adjustment):
    if adjustment.ID not in separated_instructions.adjustments:
        separated_instructions.adjustments[adjustment.ID] = SortedList()

    if adjustment in separated_instructions.adjustments[adjustment.ID]:
        return

    separated_instructions.adjustments[adjustment.ID].add(adjustment)


def _handle_reference(separated_instructions: SeparatedInstructions, reference: REFERENCES):
    if reference.ID in separated_instructions.references:
        raise errors.DuplicateIDError(duplicate_id=reference.ID)

    separated_instructions.references[reference.ID] = reference


def separate_instructions(instructions: Sequence[INSTRUCTIONS]) -> SeparatedInstructions:
    separated_instructions = SeparatedInstructions()

    for instruction in instructions:
        if isinstance(instruction, ImageReference):
            _handle_reference(separated_instructions, instruction)
        elif isinstance(instruction, Adjustment):
            _handle_adjustment(separated_instructions, instruction)

    return separated_instructions
