from functions import assemble_arguments, categorize, get_current_directory
from samples import empty, figure_eight, image_drawing, overlap, slide

import scrivid

import pathlib
import tempfile

import cv2 as opencv
import imagehash
from PIL import Image
import pytest


# Alternative name for module to reduce typing
parametrize = pytest.mark.parametrize


def close_hash_match(phash_actual, phash_expected, threshold):
    return phash_actual - phash_expected < threshold


class ComparisonBlock:
    __slots__ = ("container", "frame", "hash", "image", "ret")

    def __init__(self, video_path):
        self.container = VideoFilePointer(video_path)
        self.ret = None
        self.frame = None

    def read_container(self):
        self.ret, self.frame = self.container.vid.read()

    def define_hash(self, hashing_function):
        self.image = Image.fromarray(opencv.cvtColor(self.frame, opencv.COLOR_BGR2RGB))
        self.hash = hashing_function(self.image)


def loop_over_video_objects(actual, expected):
    while True:
        actual.read_container()
        expected.read_container()

        if not actual.ret or not expected.ret:
            break

        actual.define_hash(imagehash.phash)
        expected.define_hash(imagehash.phash)

        assert close_hash_match(actual.hash, expected.hash, 5)


@pytest.fixture(scope="module")
def temp_dir():
    with tempfile.TemporaryDirectory(dir=get_current_directory(), prefix=".scrivid-cache-") as tempdir:
        yield pathlib.Path(tempdir)


class VideoFilePointer:
    def __init__(self, video_path):
        self._video_path = video_path
        self.vid = opencv.VideoCapture(video_path)

    def __enter__(self):
        self.vid = opencv.VideoCapture(self._video_path)

    def __exit__(self, *_):
        self.vid.release()


@categorize(category="video")
@parametrize(
    "sample_module",
    assemble_arguments(
        (empty,),
        (figure_eight,),
        (image_drawing,),
        (overlap,),
        (slide,),
        id_convention=lambda args: f"{args[0].NAME()}"
    )
)
def test_compile_video_output(temp_dir, sample_module):
    instructions, metadata = sample_module.ALL()
    metadata.save_location = temp_dir
    scrivid.compile_video(instructions, metadata)

    actual = ComparisonBlock(str(temp_dir / f"{metadata.video_name}.mp4"))
    expected = ComparisonBlock(str(get_current_directory() / f"videos/__scrivid_\'{sample_module.NAME()}\'__.mp4"))

    with actual.container, expected.container:
        loop_over_video_objects(actual, expected)
