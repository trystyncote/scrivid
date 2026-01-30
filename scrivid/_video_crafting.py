from __future__ import annotations

from . import adjustments, errors, motion_tree, properties
from ._separating_instructions import separate_instructions
from ._utils import TemporaryAttribute, TemporaryDirectory

from copy import deepcopy
import itertools
import os
import subprocess
from typing import TYPE_CHECKING

from PIL import Image

if TYPE_CHECKING:
    from ._file_objects.images import ImageReference
    from ._separating_instructions import SeparatedInstructions
    from .abc import Adjustment
    from .metadata import Metadata

    from collections.abc import Sequence
    from pathlib import Path
    from typing import TypeAlias

    INSTRUCTIONS: TypeAlias = ImageReference | Adjustment
    MotionTree: TypeAlias = motion_tree.MotionTree


class _FrameCanvas:
    __slots__ = ("_canvas", "_pixel_canvas", "index")

    def __init__(self, index: int, window_size: tuple[int, int]):
        self._canvas = Image.new("RGB", window_size, (255, 255, 255))
        self._pixel_canvas = self._canvas.load()
        self.index = index

    def save(self, save_file: Path):
        self._canvas.save(save_file, "PNG")
        self._canvas.close()
        self._canvas = None
        self._pixel_canvas = None

    def set_pixel(self, coordinates: tuple[int, int], pixel_value: tuple[int, int, int]):
        # TODO: Implement behaviour for when the coordinates has a negative
        # value, to simply return instead of trying to draw it, since a 
        # negative value draws on the other side, but not vice versa.
        try:
            self._pixel_canvas.__setitem__(coordinates, pixel_value)
        except IndexError:
            pass


class _FrameInfo:
    __slots__ = ("canvas", "index", "temp_dir")

    def __init__(self, index: int, temp_dir: Path, window_size: tuple[int, int]):
        self.canvas = _FrameCanvas(index, window_size)
        self.index = index
        self.temp_dir = temp_dir

    @property
    def save_file(self):
        return self.temp_dir / f"{self.index:06d}.png"


def _call_close(value):
    value.close()


def _draw_on_frame(frame: _FrameInfo, references_dict):
    try:
        highest_layer = max(references_dict) + 1
    except ValueError:
        return

    for index in range(highest_layer):
        if index not in references_dict:
            continue

        references = references_dict[index]
        for reference in references:
            if not reference.is_opened:
                reference.open()

            ref_x = reference.x
            ref_y = reference.y

            for x, y in itertools.product(
                    range(ref_x, ref_x + reference.get_image_width()),
                    range(ref_y, ref_y + reference.get_image_height())
            ):
                frame.canvas.set_pixel((x, y), reference.get_pixel_value((x - ref_x, y - ref_y)))


def _invoke_adjustment_duration(index: int, adj: Adjustment):
    # Assume that the `adj` has a 'duration' attribute.
    duration = index - adj.activation_time
    if duration > adj.duration:
        return adj.duration
    else:
        return duration


def _create_frame(frame: _FrameInfo, split_instructions: SeparatedInstructions):
    index = frame.index
    instructions = deepcopy(split_instructions)  # Avoid modifying the
    # original objects.
    layer_reference = {}
    merge_settings = {"mode": properties.MergeMode.REVERSE_APPEND}

    for ID, reference in instructions.references.items():
        try:
            relevant_adjustments = instructions.adjustments[ID]
        except KeyError:
            relevant_adjustments = None

        while relevant_adjustments:
            adj = relevant_adjustments.pop(0)

            if adj.activation_time > index:
                break

            args = ()
            if type(adj) is adjustments.core.MoveAdjustment:
                args = (_invoke_adjustment_duration(index, adj),)

            reference._properties = reference._properties.merge(adj._enact(*args), **merge_settings)

        if reference.visibility is properties.VisibilityStatus.HIDE:
            continue

        layer = reference.layer
        if layer not in layer_reference:
            layer_reference[layer] = set()

        layer_reference[layer].add(reference)

    _draw_on_frame(frame, layer_reference)
    frame.canvas.save(frame.save_file)


def _fill_undrawn_frames(temporary_directory: Path, video_length: int):
    with TemporaryAttribute(cleanup=_call_close) as frame_assignment:
        for index in range(video_length):
            try:
                frame_assignment.value = Image.open(
                    str(temporary_directory / f"{index:06d}.png")
                )
            except FileNotFoundError:
                frame_assignment.value.save(
                    temporary_directory / f"{index:06d}.png"
                )


def _generate_frames(
        parsed_motion_tree: MotionTree,
        temporary_directory: Path,
        window_size: tuple[int, int]
) -> tuple[list[_FrameInfo], int]:
    # ...
    frames = []
    index = 0

    for node in parsed_motion_tree.body:
        type_ = type(node)
        if type_ is motion_tree.Start:
            frames.append(_FrameInfo(0, temporary_directory, window_size))
        elif type_ in (motion_tree.HideImage, motion_tree.MoveImage, motion_tree.ShowImage):
            if index == frames[-1].index:
                continue
            frames.append(_FrameInfo(index, temporary_directory, window_size))
        elif type_ is motion_tree.InvokePrevious:
            start = 0
            if index == frames[-1].index:
                start = 1
                index += 1
            for _ in range(start, node.length):
                frames.append(_FrameInfo(index, temporary_directory, window_size))
                index += 1
            del start
        elif type_ is motion_tree.Continue:
            index += node.length
        elif type_ is motion_tree.End:
            break

    return frames, index


def _concatenate(command):
    try:
        subprocess.run(command, capture_output=True)
    except subprocess.SubprocessError as exc:
        raise errors.InternalErrorFromFFMPEG(exc, exc.stdout, exc.stderr)


def _stitch_video(temporary_directory, metadata, video_length):
    input_file = os.path.join(temporary_directory, "%06d.png")
    output_file = str(metadata.save_location / f"{metadata.video_name}.mp4")
    dimensions = f"{metadata.window_width}x{metadata.window_height}"

    # I honest to god could not tell you how I figured this out. I just
    # couldn't figure out how to make a stable result for the life of me.
    command = [
        "ffmpeg",
        "-framerate", str(metadata.frame_rate),  # INPUT SETTINGS
        "-i", str(input_file),
        "-b:v", "4M",  # # # # # # # # # # # # # # OUTPUT SETTINGS
        "-vcodec", "libx264",
        "-pix_fmt", "yuv420p",
        "-s", dimensions,
        output_file
    ]

    _concatenate(command)


def compile_video(instructions: Sequence[INSTRUCTIONS], metadata: Metadata):
    """
    Converts the objects, taken as instructions, into a compiled video.

    :param instructions: A list of instances of ImageReference's, and/or a 
        class of the Adjustment hierarchy.
    :param metadata: An instance of Metadata that stores the attributes
        of the video.
    """
    metadata._validate()

    separated_instructions = separate_instructions(instructions)
    parsed_motion_tree = motion_tree.parse(separated_instructions)

    with TemporaryDirectory(metadata.save_location / ".scrivid-cache") as temp_dir:
        frames, video_length = _generate_frames(parsed_motion_tree, temp_dir.dir, metadata.window_size)

        for frame_information in frames:
            _create_frame(frame_information, separated_instructions)

        _fill_undrawn_frames(temp_dir.dir, video_length)
        _stitch_video(temp_dir.dir, metadata, video_length)
