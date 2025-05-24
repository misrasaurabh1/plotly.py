from typing import List

import plotly
import plotly.graph_objs as go
from plotly.offline import get_plotlyjs_version


def validate_coerce_fig_to_dict(fig, validate):
    from plotly.basedatatypes import BaseFigure

    if isinstance(fig, BaseFigure):
        fig_dict = fig.to_dict()
    elif isinstance(fig, dict):
        if validate:
            # This will raise an exception if fig is not a valid plotly figure
            fig_dict = plotly.graph_objs.Figure(fig).to_plotly_json()
        else:
            fig_dict = fig
    elif hasattr(fig, "to_plotly_json"):
        fig_dict = fig.to_plotly_json()
    else:
        raise ValueError(
            """
The fig parameter must be a dict or Figure.
    Received value of type {typ}: {v}""".format(
                typ=type(fig), v=fig
            )
        )
    return fig_dict


def validate_coerce_output_type(output_type):
    if output_type == "Figure" or output_type == go.Figure:
        cls = go.Figure
    elif output_type == "FigureWidget" or (
        hasattr(go, "FigureWidget") and output_type == go.FigureWidget
    ):
        cls = go.FigureWidget
    else:
        raise ValueError(
            """
Invalid output type: {output_type}
    Must be one of: 'Figure', 'FigureWidget'"""
        )
    return cls


def broadcast_args_to_dicts(**kwargs: dict) -> List[dict]:
    """
    Given one or more keyword arguments which may be either a single value or a list of values,
    return a list of keyword dictionaries by broadcasting the single valuesacross all the dicts.
    If more than one item in the input is a list, all lists must be the same length.

    Parameters
    ----------
    **kwargs: dict
        The keyword arguments

    Returns
    -------
    list of dicts
        A list of dictionaries

    Raises
    ------
    ValueError
        If any of the input lists are not the same length
    """
    # Collect keys and their values
    items = []
    list_length = None

    for k, v in kwargs.items():
        if isinstance(v, list):
            if list_length is None:
                list_length = len(v)
            elif len(v) != list_length:
                raise ValueError("All list arguments must have the same length.")
            items.append((k, v))
        else:
            items.append((k, None))  # mark for later

    # If there are no lists, every singleton broadcasts to length 1
    if list_length is None:
        list_length = 1
        broadcasted = [tuple(v if not v_ is None else [kwargs[k]] for k, v_ in items)]
        return [{k: kwargs[k] for k, _ in items}]
    else:
        # Expand singletons to lists
        broadcasted = []
        for k, v in items:
            if v is None:
                broadcasted.append([kwargs[k]] * list_length)
            else:
                broadcasted.append(v)
        # Use zip to batch build the result dictionaries efficiently
        # Equivalent to: [{k: v[i] for k, v in expanded_kwargs.items()} ...]
        keys = [k for k, _ in items]
        return [dict(zip(keys, vals)) for vals in zip(*broadcasted)]


def plotly_cdn_url(cdn_ver=get_plotlyjs_version()):
    """Return a valid plotly CDN url."""
    return "https://cdn.plot.ly/plotly-{cdn_ver}.min.js".format(
        cdn_ver=cdn_ver,
    )
