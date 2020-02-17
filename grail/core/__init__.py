# -*- coding: UTF-8 -*-
"""
    grail.core
    ~~~~~~~~~~

    :copyright: (c) 2016-2020 by Oleksii Lytvyn (http://alexlitvin.name)
    :license: GNU, see LICENSE for more details.
"""

import functools
from .plugin import Plugin, Viewer, Configurator
from .osc_host import OSCHost


def debug(func):
    """Print the function signature and return value"""

    @functools.wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        value = func(*args, **kwargs)

        print(f"Calling {func.__name__}({signature}) => {value!r}")

        return value

    return wrapper_debug
