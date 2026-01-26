from functions import assemble_arguments, categorize, unwrap_string
from samples import empty, figure_eight, image_drawing, overlap, slide

from scrivid import create_image_reference, errors, motion_tree

import pytest


# Alternative name for module to reduce typing
pytest_parametrize = pytest.mark.parametrize


def has_method(cls, method):
    if (n := getattr(cls, method, None)) and callable(n):
        return True
    else:
        return False


@categorize(category="motion_tree")
@pytest_parametrize("indent", [0, 2, 4, 8])
@pytest_parametrize(
    "sample_module,expected_string_raw", 
    assemble_arguments(
        (empty, unwrap_string(r"""
            MotionTree({\b}{\i}body=[{\b}{\i}{\i}Start(), {\b}{\i}{\i}HideImage(id='HIDDEN', time=0), {\b}{\i}{\i}Conti
            nue(length=1), {\b}{\i}{\i}MoveImage(id='HIDDEN', time=1, duration=11), {\b}{\i}{\i}InvokePrevious(length=1
            1), {\b}{\i}{\i}End()])
        """)),
        (figure_eight, unwrap_string(r"""
            MotionTree({\b}{\i}body=[{\b}{\i}{\i}Start(), {\b}{\i}{\i}Continue(length=6), {\b}{\i}{\i}MoveImage(id='BLO
            CK', time=6, duration=10), {\b}{\i}{\i}InvokePrevious(length=10), {\b}{\i}{\i}MoveImage(id='BLOCK', time=16
            , duration=5), {\b}{\i}{\i}InvokePrevious(length=5), {\b}{\i}{\i}MoveImage(id='BLOCK', time=21, duration=5)
            , {\b}{\i}{\i}InvokePrevious(length=10), {\b}{\i}{\i}MoveImage(id='BLOCK', time=26, duration=10), {\b}{\i}{
            \i}InvokePrevious(length=5), {\b}{\i}{\i}MoveImage(id='BLOCK', time=36, duration=5), {\b}{\i}{\i}InvokePrev
            ious(length=5), {\b}{\i}{\i}MoveImage(id='BLOCK', time=41, duration=5), {\b}{\i}{\i}InvokePrevious(length=5
            ), {\b}{\i}{\i}End()])
        """)),
        (image_drawing, unwrap_string(r"""
            MotionTree({\b}{\i}body=[{\b}{\i}{\i}Start(), {\b}{\i}{\i}HideImage(id='HIDDEN', time=0), {\b}{\i}{\i}Conti
            nue(length=20), {\b}{\i}{\i}ShowImage(id='HIDDEN', time=20), {\b}{\i}{\i}End()])
        """)),
        (overlap, unwrap_string(r"""
            MotionTree({\b}{\i}body=[{\b}{\i}{\i}Start(), {\b}{\i}{\i}Continue(length=12), {\b}{\i}{\i}MoveImage(id='RI
            GHT', time=12, duration=1), {\b}{\i}{\i}InvokePrevious(length=1), {\b}{\i}{\i}End()])
        """)),
        (slide, unwrap_string(r"""
            MotionTree({\b}{\i}body=[{\b}{\i}{\i}Start(), {\b}{\i}{\i}Continue(length=1), {\b}{\i}{\i}MoveImage(id='sto
            ne', time=1, duration=36), {\b}{\i}{\i}InvokePrevious(length=36), {\b}{\i}{\i}End()])
        """))
    )
)
def test_dump(indent, sample_module, expected_string_raw):
    expected = (
        expected_string_raw
        .replace(r"{\i}", " " * indent)
        .replace(r"{\b}", "\n" if indent else "")
    )

    instructions = sample_module.INSTRUCTIONS()
    parsed_motion_tree = motion_tree.parse(instructions)

    actual = motion_tree.dump(parsed_motion_tree, indent=indent)
    assert actual == expected


@categorize(category="motion_tree")
@pytest_parametrize(
    "node_cls,attr",
    assemble_arguments(
        (motion_tree.Continue, "length"),
        (motion_tree.HideImage, "id"),
        (motion_tree.HideImage, "time"),
        (motion_tree.InvokePrevious, "length"),
        (motion_tree.MotionTree, "body"),
        (motion_tree.MoveImage, "duration"),
        (motion_tree.MoveImage, "id"),
        (motion_tree.MoveImage, "time"),
        (motion_tree.ShowImage, "id"),
        (motion_tree.ShowImage, "time"),
        id_convention=lambda args: f"{args[0].__name__}.{args[1]}"
    )
)
def test_nodes_has_attributes(node_cls, attr):
    assert hasattr(node_cls, attr)


@categorize(category="motion_tree")
@pytest_parametrize("node_cls,method", [
    (motion_tree.HideImage, "__eq__"),
    (motion_tree.HideImage, "__ge__"),
    (motion_tree.HideImage, "__gt__"),
    (motion_tree.HideImage, "__le__"),
    (motion_tree.HideImage, "__lt__"),
    (motion_tree.HideImage, "__ne__"),
    (motion_tree.MotionTree, "convert_to_string"),
    (motion_tree.MoveImage, "__eq__"),
    (motion_tree.MoveImage, "__ge__"),
    (motion_tree.MoveImage, "__gt__"),
    (motion_tree.MoveImage, "__le__"),
    (motion_tree.MoveImage, "__lt__"),
    (motion_tree.MoveImage, "__ne__"),
    (motion_tree.ShowImage, "__eq__"),
    (motion_tree.ShowImage, "__ge__"),
    (motion_tree.ShowImage, "__gt__"),
    (motion_tree.ShowImage, "__le__"),
    (motion_tree.ShowImage, "__lt__"),
    (motion_tree.ShowImage, "__ne__"),
])
def test_nodes_has_methods_additional(node_cls, method):
    # This test function accounts for motion_node classes that are not
    # accounted for regarding the matrix strategy in
    # `test_nodes_has_methods_required`.
    assert has_method(node_cls, method)


@categorize(category="motion_tree")
@pytest_parametrize("node_cls", [
    motion_tree.Continue, motion_tree.End, motion_tree.HideImage, motion_tree.InvokePrevious, motion_tree.MotionTree,
    motion_tree.MoveImage, motion_tree.ShowImage, motion_tree.Start
])
@pytest_parametrize("method", [
    "__init__", "__repr__", "__setattr__", "__delattr__", "__getstate__",
    "__setstate__"
])
def test_nodes_has_methods_required(node_cls, method):
    assert has_method(node_cls, method)


@categorize(category="motion_tree")
@pytest_parametrize(
    "node_cls,args",
    assemble_arguments(
        (motion_tree.Continue, (0,)),
        (motion_tree.End, ()),
        (motion_tree.HideImage, (0, 0)),
        (motion_tree.InvokePrevious, (0,)),
        (motion_tree.MotionTree, ()),
        (motion_tree.MoveImage, (0, 0, 0)),
        (motion_tree.ShowImage, (0, 0)),
        (motion_tree.Start, ())
    )
)
def test_nodes_inheritance(node_cls, args):
    node = node_cls(*args)
    assert isinstance(node, motion_tree._RootMotionTree)


@categorize(category="motion_tree")
@pytest_parametrize(
    "sample_module",
    assemble_arguments(
        (empty,),
        (figure_eight,),
        (image_drawing,),
        (overlap,),
        (slide,)
    )
)
def test_parse(sample_module):
    instructions = sample_module.INSTRUCTIONS()
    motion_tree.parse(instructions)


def test_parse_duplicate_id():
    references = (
        create_image_reference(0, ""),
        create_image_reference(0, "")
    )  # These two reference objects have the same ID field.
    with pytest.raises(errors.DuplicateIDError):
        motion_tree.parse(references)


@categorize(category="motion_tree")
@pytest_parametrize(
    "sample_module,expected_node_order",
    assemble_arguments(
        (empty, 
         [motion_tree.MotionTree, motion_tree.Start, motion_tree.HideImage, motion_tree.Continue,
          motion_tree.MoveImage, motion_tree.InvokePrevious, motion_tree.End]),
        (figure_eight,
         [motion_tree.MotionTree, motion_tree.Start, motion_tree.Continue, motion_tree.MoveImage,
          motion_tree.InvokePrevious, motion_tree.MoveImage, motion_tree.InvokePrevious, motion_tree.MoveImage,
          motion_tree.InvokePrevious, motion_tree.MoveImage, motion_tree.InvokePrevious, motion_tree.MoveImage,
          motion_tree.InvokePrevious, motion_tree.MoveImage, motion_tree.InvokePrevious, motion_tree.End]),
        (image_drawing, 
         [motion_tree.MotionTree, motion_tree.Start, motion_tree.HideImage, motion_tree.Continue,
          motion_tree.ShowImage, motion_tree.End]),
        (overlap,
         [motion_tree.MotionTree, motion_tree.Start, motion_tree.Continue, motion_tree.MoveImage,
          motion_tree.InvokePrevious, motion_tree.End]),
        (slide,
         [motion_tree.MotionTree, motion_tree.Start, motion_tree.Continue, motion_tree.MoveImage,
          motion_tree.InvokePrevious, motion_tree.End])
    )
)
def test_walk(sample_module, expected_node_order):
    instructions = sample_module.INSTRUCTIONS()
    parsed_motion_tree = motion_tree.parse(instructions)
    for actual, expected_node in zip(motion_tree.walk(parsed_motion_tree), expected_node_order):
        actual_node = type(actual)
        assert actual_node is expected_node
