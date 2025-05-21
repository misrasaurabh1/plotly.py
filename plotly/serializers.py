from .basedatatypes import Undefined
from .optional_imports import get_module

np = get_module("numpy")


def _py_to_js(v, widget_manager):
    """
    Python -> Javascript ipywidget serializer

    This function must repalce all objects that the ipywidget library
    can't serialize natively (e.g. numpy arrays) with serializable
    representations

    Parameters
    ----------
    v
        Object to be serialized
    widget_manager
        ipywidget widget_manager (unused)

    Returns
    -------
    any
        Value that the ipywidget library can serialize natively
    """

    # Fastest singletons check first
    if v is Undefined:
        return "_undefined_"

    # Dicts
    if _isinstance(v, _dict):
        return {k: _py_to_js(val, widget_manager) for k, val in v.items()}

    # List & Tuple
    if _isinstance(v, (_list, _tuple)):
        return [_py_to_js(item, widget_manager) for item in v]

    # Numpy array (if available)
    if _NDARRAY is not None and _isinstance(v, _NDARRAY):
        # Only map certain 1D numpy arrays to {"buffer", ...}
        if (
            v.ndim == 1
            and v.dtype.kind in ("u", "i", "f")
            and v.dtype != "int64"
            and v.dtype != "uint64"
        ):
            # Map to TypedArray-compatible dict
            return {"buffer": memoryview(v), "dtype": str(v.dtype), "shape": v.shape}
        else:
            return v.tolist()

    # Fallback
    return v


def _js_to_py(v, widget_manager):
    """
    Javascript -> Python ipywidget deserializer

    Parameters
    ----------
    v
        Object to be deserialized
    widget_manager
        ipywidget widget_manager (unused)

    Returns
    -------
    any
        Deserialized object for use by the Python side of the library
    """
    # Handle dict
    # -----------
    if isinstance(v, dict):
        return {k: _js_to_py(v, widget_manager) for k, v in v.items()}

    # Handle list/tuple
    # -----------------
    elif isinstance(v, (list, tuple)):
        return [_js_to_py(v, widget_manager) for v in v]

    # Handle Undefined
    # ----------------
    elif isinstance(v, str) and v == "_undefined_":
        return Undefined

    # Handle simple value
    # -------------------
    else:
        return v


# Custom serializer dict for use in ipywidget traitlet definitions
custom_serializers = {"from_json": _js_to_py, "to_json": _py_to_js}

_NDARRAY = getattr(np, "ndarray", None) if np is not None else None

_isinstance = isinstance

_list = list

_tuple = tuple

_dict = dict
