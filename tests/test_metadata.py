from functions import assemble_arguments
from scrivid import errors, Metadata

import pytest


# ALIAS
parametrize = pytest.mark.parametrize

FILL_VALUE = object()

METADATA_DEFAULTS = {
    "frame_rate": 0,
    "save_location": "",
    "video_name": "",
    "window_size": (0, 0)
}


def _assemble_method_fillvalue(arguments, _):
    argument = arguments[0]
    for key in argument:
        current_values = argument.copy()
        current_values[key] = FILL_VALUE
        yield pytest.param(current_values, id=key)


@parametrize("attribute", ["frame_rate", "save_location", "video_name", "window_size"])
def test_attribute_deletion(attribute):
    metadata = Metadata(**METADATA_DEFAULTS)
    delattr(metadata, attribute)
    assert getattr(metadata, attribute) is None


@parametrize("current_values", assemble_arguments(METADATA_DEFAULTS, method=_assemble_method_fillvalue))
def test_validation_type(current_values):
    with pytest.raises(errors.AttributeError):
        Metadata(**current_values)


@parametrize("updated_window_size", [(5, 0), (0, 5)], ids=["width", "height"])
def test_validation_window_size_odd_numbers(updated_window_size):
    with pytest.raises(errors.AttributeError):
        metadata = Metadata(frame_rate=0, save_location="", video_name="")
        metadata.window_size = updated_window_size


def test_window_attributes():
    metadata = Metadata(window_size=(8, 6))
    assert metadata.window_size == (8, 6)
    assert metadata.window_height == 6
    assert metadata.window_width == 8

    metadata.window_size = (10, 8)
    assert metadata.window_size == (10, 8)


def test_window_attributes_exclusion():
    metadata = Metadata()
    assert metadata.window_height is None
    assert metadata.window_width is None
