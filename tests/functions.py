from pathlib import Path
import textwrap

import pytest


def _assemble_method_simple(arguments, id_convention):
    for args in arguments:
        yield pytest.param(*args, id=id_convention(args))


def assemble_arguments(*arguments, id_convention=lambda args: f"{args[0].__name__}", method=_assemble_method_simple):
    return tuple(param for param in method(arguments, id_convention))


def categorize(*, category):
    marks = [
        getattr(pytest.mark, category)
    ]

    def decorator(function):
        for mark in marks:
            function = mark(function)
        return function

    return decorator


def get_current_directory():
    return Path(__file__).absolute().parent


def hacky_import(file, module_name):
    # Borrowed and adapted from the documentation: 
    # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
    import importlib.util

    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def _unpack_arg(arg):
    try:
        return [a for a in arg]
    except TypeError:
        return [arg]


def _recursive_relational_unpacking(complete_args, iters, prev_values):
    if len(iters) == 1:
        for item in _unpack_arg(iters):
            complete_args.append((*prev_values, item))
        return complete_args

    for item in _unpack_arg(iters[0]):
        _recursive_relational_unpacking(complete_args, iters[1:], (*prev_values, item))

    return complete_args


def relational_unpacking(*iters):
    return _recursive_relational_unpacking([], iters, ())


def unwrap_string(string):
    return textwrap.dedent(string).replace("\n", "")
