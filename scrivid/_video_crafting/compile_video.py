from __future__ import annotations

from ._frame_drawing import create_frame, fill_undrawn_frames, generate_frames
from ._video_stitching import stitch_video

from .. import motion_tree

from .._separating_instructions import separate_instructions
from .._utils import TemporaryDirectory

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..abc import Adjustment
    from .._file_objects.images import ImageReference
    from ..metadata import Metadata

    from collections.abc import Sequence
    from typing import Union

    INSTRUCTIONS = Union[ImageReference, Adjustment]


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
        frames, video_length = generate_frames(parsed_motion_tree, temp_dir.dir, metadata.window_size)

        for frame_information in frames:
            create_frame(frame_information, separated_instructions)

        fill_undrawn_frames(temp_dir.dir, video_length)
        stitch_video(temp_dir.dir, metadata, video_length)
