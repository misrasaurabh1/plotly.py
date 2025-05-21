"""
Stand-alone module to provide information about whether optional deps exist.

"""

from importlib import import_module
import logging
import sys
from _plotly_utils.data_utils import *
from _plotly_utils.utils import *

logger = logging.getLogger(__name__)
_not_importable = set()


def get_module(name, should_load=True):
    """
    Return module or None. Absolute import is required.

    :param (str) name: Dot-separated module path. E.g., 'scipy.stats'.
    :raise: (ImportError) Only when exc_msg is defined.
    :return: (module|None) If import succeeds, the module will be returned.

    """
    # Fast cache path
    m = sys.modules.get(name, None)
    if not should_load:
        return m
    if m is not None:
        return m

    # Avoid import and repeated failed lookups
    if name in _not_importable:
        return None

    try:
        mod = import_module(name)
        return mod
    except ImportError:
        _not_importable.add(name)
    except Exception:
        _not_importable.add(name)
        msg = f"Error importing optional module {name}"
        logger.exception(msg)
    return None
