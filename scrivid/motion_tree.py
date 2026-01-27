from __future__ import annotations

from . import adjustments
from ._separating_instructions import separate_instructions, SeparatedInstructions

from collections.abc import Hashable
import operator
from typing import TYPE_CHECKING

from sortedcontainers import SortedList

if TYPE_CHECKING:
    from .abc import Adjustment
    from ._file_objects.images import ImageReference

    from collections.abc import Sequence
    from typing import Dict, Iterator, Optional, Union

    REFERENCES = ImageReference


def _compare_attribute_time(op: operator):
    def function(a, b):
        if not hasattr(b, "time"):
            return NotImplemented
        return op(a.time, b.time)

    return function


class _RootMotionTree:
    __slots__ = ()


class Continue(_RootMotionTree):
    __slots__ = ("_length",)

    def __new__(cls, length: int):
        self = super().__new__(cls)
        self._length = length
        return self

    @property
    def length(self):
        return self._length

    def __repr__(self):
        return f"{self.__class__.__name__}(length={self.length})"


class End(_RootMotionTree):
    __slots__ = ()

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class HideImage(_RootMotionTree):
    __slots__ = ("_identity", "_time")

    def __new__(cls, identity: Hashable, time: int):
        self = super().__new__(cls)
        self._identity = identity
        self._time = time
        return self

    @property
    def id(self):
        return self._identity

    @property
    def time(self):
        return self._time

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id!r}, time={self.time})"

    __eq__ = _compare_attribute_time(operator.eq)
    __ge__ = _compare_attribute_time(operator.ge)
    __gt__ = _compare_attribute_time(operator.gt)
    __le__ = _compare_attribute_time(operator.le)
    __lt__ = _compare_attribute_time(operator.lt)
    __ne__ = _compare_attribute_time(operator.ne)


class InvokePrevious(_RootMotionTree):
    __slots__ = ("_length",)

    def __new__(cls, length: int):
        self = super().__new__(cls)
        self._length = length
        return self

    @property
    def length(self):
        return self._length

    def __repr__(self):
        return f"{self.__class__.__name__}(length={self.length})"


class MoveImage(_RootMotionTree):
    __slots__ = ("_duration", "_identity", "_time")

    def __new__(cls, identity: Hashable, time: int, duration: int):
        self = super().__new__(cls)
        self._duration = duration
        self._identity = identity
        self._time = time
        return self

    @property
    def duration(self):
        return self._duration

    @property
    def id(self):
        return self._identity

    @property
    def time(self):
        return self._time

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id!r}, time={self.time}, duration={self.duration})"

    __eq__ = _compare_attribute_time(operator.eq)
    __ge__ = _compare_attribute_time(operator.ge)
    __gt__ = _compare_attribute_time(operator.gt)
    __le__ = _compare_attribute_time(operator.le)
    __lt__ = _compare_attribute_time(operator.lt)
    __ne__ = _compare_attribute_time(operator.ne)


class ShowImage(_RootMotionTree):
    __slots__ = ("_identity", "_time")

    def __new__(cls, identity: Hashable, time: int):
        self = super().__new__(cls)
        self._identity = identity
        self._time = time
        return self

    @property
    def id(self):
        return self._identity

    @property
    def time(self):
        return self._time

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id!r}, time={self.time})"

    __eq__ = _compare_attribute_time(operator.eq)
    __ge__ = _compare_attribute_time(operator.ge)
    __gt__ = _compare_attribute_time(operator.gt)
    __le__ = _compare_attribute_time(operator.le)
    __lt__ = _compare_attribute_time(operator.lt)
    __ne__ = _compare_attribute_time(operator.ne)


class Start(_RootMotionTree):
    __slots__ = ()

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class VideoInstructions(_RootMotionTree):
    __slots__ = ("_body",)

    _body: list[MOTION_NODES]

    def __new__(cls):
        self = super().__new__(cls)
        self._body = []
        return self

    @property
    def body(self) -> list[MOTION_NODES]:
        return self._body

    def convert_to_string(self, *, indent: int = 0, _previous_indent: int = 0) -> str:
        if len(self.body) == 0:
            return repr(self)

        indent_sequence = ""
        if indent > 0:
            indent_sequence = f"\n{' ' * _previous_indent}"

        return (
            f"{indent_sequence}{self.__class__.__name__}("
            + f"{indent_sequence}{' ' * indent}body=["
            + ', '.join(
                node.convert_to_string(indent=indent, _previous_indent=(2*indent)+_previous_indent)
                if getattr(node, "convert_to_string", False)
                else f"{indent_sequence}{' ' * (2 * indent)}{node!r}"
                for node in self.body
            )
            + "])"
        )


if TYPE_CHECKING:
    # This is set up *after* the MotionTree Nodes are defined, to prevent type checking issues
    MOTION_NODES = Union[Continue, End, HideImage, VideoInstructions, ShowImage, Start]


def dump(motion_tree: VideoInstructions, *, indent: int = 0) -> str:
    if hasattr(motion_tree, "convert_to_string"):
        return motion_tree.convert_to_string(indent=indent).strip()
    else:
        return repr(motion_tree)


def _create_command_node(adjustment: Adjustment) -> Optional[Union[HideImage, MoveImage, ShowImage]]:
    adjustment_type = type(adjustment)
    adjustment_time = adjustment.activation_time
    relevant_id = adjustment.ID

    if adjustment_type == adjustments.core.HideAdjustment:
        return HideImage(relevant_id, adjustment_time)
    elif adjustment_type == adjustments.core.MoveAdjustment:
        return MoveImage(relevant_id, adjustment_time, adjustment.duration)
    elif adjustment_type == adjustments.core.ShowAdjustment:
        return ShowImage(relevant_id, adjustment_time)
    else:
        return None


def _create_motion_tree(separated_instructions: SeparatedInstructions) -> VideoInstructions:
    motion_tree = VideoInstructions()

    motion_tree.body.append(Start())

    for node in _loop_over_adjustments(separated_instructions.adjustments):
        motion_tree.body.append(node)

    motion_tree.body.append(End())

    return motion_tree


def _invoke_duration_value(duration_value: int, current_node: Union[HideImage, MoveImage, ShowImage]) -> int:
    if not hasattr(current_node, "duration"):
        return duration_value

    if duration_value == 0 or duration_value <= current_node.duration:
        return current_node.duration
    else:
        return duration_value


def _loop_over_adjustments(adjustments: Dict[Adjustment]) -> Iterator[MOTION_NODES]:
    current_node = None
    duration_value = 0
    sorted_adjustments = SortedList(
        id_of_adj_value 
        for adj_value in adjustments.values() 
        for id_of_adj_value in adj_value
    )
    time_index = 0

    while sorted_adjustments or current_node:
        if current_node is None:
            adjustment = sorted_adjustments.pop(0)
            current_node = _create_command_node(adjustment)

        if current_node.time <= time_index:
            yield current_node
            duration_value = _invoke_duration_value(
                duration_value, current_node
            )
            current_node = None
            continue

        time_difference = current_node.time - time_index

        if duration_value != 0 and duration_value <= time_difference:
            duration_value = _invoke_duration_value(duration_value, current_node)
            yield InvokePrevious(duration_value)
            time_index += duration_value
            duration_value = 0
            continue

        elif duration_value != 0 and duration_value > time_difference:
            yield InvokePrevious(time_difference)
            time_index += time_difference
            duration_value = _invoke_duration_value((duration_value - time_difference), current_node)
            continue

        else:
            yield Continue(time_difference)
            time_index += time_difference

        yield current_node

        duration_value = _invoke_duration_value(duration_value, current_node)
        current_node = None

    if current_node is not None:
        duration_value = _invoke_duration_value(duration_value, current_node)
    if duration_value != 0:
        yield InvokePrevious(duration_value)


def parse(instructions: Union[Sequence[REFERENCES], SeparatedInstructions]) -> VideoInstructions:
    if not isinstance(instructions, SeparatedInstructions):
        instructions = separate_instructions(instructions)

    return _create_motion_tree(instructions)


def walk(motion_tree: VideoInstructions) -> Iterator[MOTION_NODES]:
    yield motion_tree

    if not hasattr(motion_tree, "body"):
        return

    for node in motion_tree.body:
        if hasattr(node, "body"):
            for additional_node in walk(node):
                yield additional_node
            continue

        yield node
