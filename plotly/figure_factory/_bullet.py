import math

from plotly import exceptions, optional_imports
import plotly.colors as clrs
from plotly.figure_factory import utils

import plotly
import plotly.graph_objs as go
from _plotly_utils import exceptions

pd = optional_imports.get_module("pandas")


def _bullet(
    df,
    markers,
    measures,
    ranges,
    subtitles,
    titles,
    orientation,
    range_colors,
    measure_colors,
    horizontal_spacing,
    vertical_spacing,
    scatter_options,
    layout_options,
):
    num_of_lanes = len(df)
    orientation_is_h = orientation == "h"
    num_of_rows = num_of_lanes if orientation_is_h else 1
    num_of_cols = 1 if orientation_is_h else num_of_lanes
    if not horizontal_spacing:
        horizontal_spacing = 1.0 / num_of_lanes
    if not vertical_spacing:
        vertical_spacing = 1.0 / num_of_lanes
    fig = plotly.subplots.make_subplots(
        num_of_rows,
        num_of_cols,
        print_grid=False,
        horizontal_spacing=horizontal_spacing,
        vertical_spacing=vertical_spacing,
    )

    layout = fig["layout"]
    # Layout defaults
    layout.update(
        dict(
            shapes=[],
            title="Bullet Chart",
            height=600,
            width=1000,
            showlegend=False,
            barmode="stack",
            annotations=[],
            margin=dict(l=120 if orientation_is_h else 80),
        )
    )
    layout.update(layout_options)

    width_axis = "yaxis" if orientation_is_h else "xaxis"
    length_axis = "xaxis" if orientation_is_h else "yaxis"
    w1 = width_axis + "1"

    # Precompute keys for updating axis parameters
    axis_keys = [k for k in layout.keys() if "xaxis" in k or "yaxis" in k]
    for key in axis_keys:
        axis = layout[key]
        axis["showgrid"] = False
        axis["zeroline"] = False
        if length_axis in key:
            axis["tickwidth"] = 1
        if width_axis in key:
            axis["showticklabels"] = False
            axis["range"] = [0, 1]

    # narrow domain if 1 bar
    if num_of_lanes <= 1:
        layout[w1]["domain"] = [0.4, 0.6]

    if not range_colors:
        range_colors = ["rgb(200, 200, 200)", "rgb(245, 245, 245)"]
    if not measure_colors:
        measure_colors = ["rgb(31, 119, 180)", "rgb(176, 196, 221)"]

    # Precompute color interpolations for each row (saves a bunch of call!)
    range_ncolors = [
        clrs.n_colors(range_colors[0], range_colors[1], len(df.iloc[row]["ranges"]), "rgb")
        if len(df.iloc[row]["ranges"]) > 0 else []
        for row in range(num_of_lanes)
    ]
    measure_ncolors = [
        clrs.n_colors(measure_colors[0], measure_colors[1], len(df.iloc[row]["measures"]), "rgb")
        if len(df.iloc[row]["measures"]) > 0 else []
        for row in range(num_of_lanes)
    ]

    annotations = layout["annotations"]

    for row in range(num_of_lanes):
        # ranges bars
        ranges_data = df.iloc[row]["ranges"]
        curr_range_colors = range_ncolors[row]
        sorted_ranges = sorted(ranges_data) if ranges_data else []
        xaxis_str = "x{}".format(row + 1)
        yaxis_str = "y{}".format(row + 1)

        for idx, val in enumerate(sorted_ranges[::-1]):
            color_idx = -1 - idx
            val_list = [val]
            if orientation_is_h:
                bar = go.Bar(
                    x=val_list,
                    y=[0],
                    marker=dict(color=curr_range_colors[color_idx]),
                    name="ranges",
                    hoverinfo="x",
                    orientation="h",
                    width=2,
                    base=0,
                    xaxis=xaxis_str,
                    yaxis=yaxis_str,
                )
            else:
                bar = go.Bar(
                    x=[0],
                    y=val_list,
                    marker=dict(color=curr_range_colors[color_idx]),
                    name="ranges",
                    hoverinfo="y",
                    orientation="v",
                    width=2,
                    base=0,
                    xaxis=xaxis_str,
                    yaxis=yaxis_str,
                )
            fig.add_trace(bar)

        # measures bars
        measures_data = df.iloc[row]["measures"]
        curr_measure_colors = measure_ncolors[row]
        sorted_measures = sorted(measures_data) if measures_data else []
        for idx, val in enumerate(sorted_measures[::-1]):
            color_idx = -1 - idx
            if orientation_is_h:
                bar = go.Bar(
                    x=[val],
                    y=[0.5],
                    marker=dict(color=curr_measure_colors[color_idx]),
                    name="measures",
                    hoverinfo="x",
                    orientation="h",
                    width=0.4,
                    base=0,
                    xaxis=xaxis_str,
                    yaxis=yaxis_str,
                )
            else:
                bar = go.Bar(
                    x=[0.5],
                    y=[val],
                    marker=dict(color=curr_measure_colors[color_idx]),
                    name="measures",
                    hoverinfo="y",
                    orientation="v",
                    width=0.4,
                    base=0,
                    xaxis=xaxis_str,
                    yaxis=yaxis_str,
                )
            fig.add_trace(bar)

        # markers
        m = df.iloc[row]["markers"]
        scatter_args = {
            "x": m if orientation_is_h else [0.5],
            "y": [0.5] if orientation_is_h else m,
            "name": "markers",
            "hoverinfo": "x" if orientation_is_h else "y",
            "xaxis": xaxis_str,
            "yaxis": yaxis_str,
        }
        scatter_args.update(scatter_options)
        markers_trace = go.Scatter(**scatter_args)
        fig.add_trace(markers_trace)

        # titles and subtitles
        title = df.iloc[row]["titles"]
        subtitle = (
            "<br>{}".format(df.iloc[row].get("subtitles", ""))
            if "subtitles" in df
            else ""
        )
        label = "<b>{}</b>{}".format(title, subtitle)
        annot = utils.annotation_dict_for_label(
            label,
            (num_of_lanes - row if orientation_is_h else row + 1),
            num_of_lanes,
            vertical_spacing if orientation_is_h else horizontal_spacing,
            "row" if orientation_is_h else "col",
            orientation_is_h,
            False,
        )
        annotations.append(annot)

    return fig


def create_bullet(
    data,
    markers=None,
    measures=None,
    ranges=None,
    subtitles=None,
    titles=None,
    orientation="h",
    range_colors=("rgb(200, 200, 200)", "rgb(245, 245, 245)"),
    measure_colors=("rgb(31, 119, 180)", "rgb(176, 196, 221)"),
    horizontal_spacing=None,
    vertical_spacing=None,
    scatter_options={},
    **layout_options,
):
    """
    **deprecated**, use instead the plotly.graph_objects trace
    :class:`plotly.graph_objects.Indicator`.

    :param (pd.DataFrame | list | tuple) data: either a list/tuple of
        dictionaries or a pandas DataFrame.
    :param (str) markers: the column name or dictionary key for the markers in
        each subplot.
    :param (str) measures: the column name or dictionary key for the measure
        bars in each subplot. This bar usually represents the quantitative
        measure of performance, usually a list of two values [a, b] and are
        the blue bars in the foreground of each subplot by default.
    :param (str) ranges: the column name or dictionary key for the qualitative
        ranges of performance, usually a 3-item list [bad, okay, good]. They
        correspond to the grey bars in the background of each chart.
    :param (str) subtitles: the column name or dictionary key for the subtitle
        of each subplot chart. The subplots are displayed right underneath
        each title.
    :param (str) titles: the column name or dictionary key for the main label
        of each subplot chart.
    :param (bool) orientation: if 'h', the bars are placed horizontally as
        rows. If 'v' the bars are placed vertically in the chart.
    :param (list) range_colors: a tuple of two colors between which all
        the rectangles for the range are drawn. These rectangles are meant to
        be qualitative indicators against which the marker and measure bars
        are compared.
        Default=('rgb(200, 200, 200)', 'rgb(245, 245, 245)')
    :param (list) measure_colors: a tuple of two colors which is used to color
        the thin quantitative bars in the bullet chart.
        Default=('rgb(31, 119, 180)', 'rgb(176, 196, 221)')
    :param (float) horizontal_spacing: see the 'horizontal_spacing' param in
        plotly.tools.make_subplots. Ranges between 0 and 1.
    :param (float) vertical_spacing: see the 'vertical_spacing' param in
        plotly.tools.make_subplots. Ranges between 0 and 1.
    :param (dict) scatter_options: describes attributes for the scatter trace
        in each subplot such as name and marker size. Call
        help(plotly.graph_objs.Scatter) for more information on valid params.
    :param layout_options: describes attributes for the layout of the figure
        such as title, height and width. Call help(plotly.graph_objs.Layout)
        for more information on valid params.

    Example 1: Use a Dictionary

    >>> import plotly.figure_factory as ff

    >>> data = [
    ...   {"label": "revenue", "sublabel": "us$, in thousands",
    ...    "range": [150, 225, 300], "performance": [220,270], "point": [250]},
    ...   {"label": "Profit", "sublabel": "%", "range": [20, 25, 30],
    ...    "performance": [21, 23], "point": [26]},
    ...   {"label": "Order Size", "sublabel":"US$, average","range": [350, 500, 600],
    ...    "performance": [100,320],"point": [550]},
    ...   {"label": "New Customers", "sublabel": "count", "range": [1400, 2000, 2500],
    ...    "performance": [1000, 1650],"point": [2100]},
    ...   {"label": "Satisfaction", "sublabel": "out of 5","range": [3.5, 4.25, 5],
    ...    "performance": [3.2, 4.7], "point": [4.4]}
    ... ]

    >>> fig = ff.create_bullet(
    ...     data, titles='label', subtitles='sublabel', markers='point',
    ...     measures='performance', ranges='range', orientation='h',
    ...     title='my simple bullet chart'
    ... )
    >>> fig.show()

    Example 2: Use a DataFrame with Custom Colors

    >>> import plotly.figure_factory as ff
    >>> import pandas as pd
    >>> data = pd.read_json('https://cdn.rawgit.com/plotly/datasets/master/BulletData.json')

    >>> fig = ff.create_bullet(
    ...     data, titles='title', markers='markers', measures='measures',
    ...     orientation='v', measure_colors=['rgb(14, 52, 75)', 'rgb(31, 141, 127)'],
    ...     scatter_options={'marker': {'symbol': 'circle'}}, width=700)
    >>> fig.show()
    """
    # validate df
    if not pd:
        raise ImportError("'pandas' must be installed for this figure factory.")

    SEQ = utils.is_sequence(data)
    if SEQ:
        if not all(isinstance(item, dict) for item in data):
            raise exceptions.PlotlyError(
                "Every entry of the data argument list, tuple, etc must be a dictionary."
            )
    elif not isinstance(data, pd.DataFrame):
        raise exceptions.PlotlyError(
            "You must input a pandas DataFrame, or a list of dictionaries."
        )

    # make DataFrame from data with correct column headers
    col_names = ["titles", "subtitle", "markers", "measures", "ranges"]
    n = len(data)
    if SEQ:
        df = pd.DataFrame(
            [
                [d[titles] if titles else "" for d in data],
                [d[subtitles] if subtitles else "" for d in data],
                [d[markers] if markers else [] for d in data],
                [d[measures] if measures else [] for d in data],
                [d[ranges] if ranges else [] for d in data]
            ],
            index=col_names
        )
    else:
        df = pd.DataFrame(
            [
                data[titles].tolist() if titles else [""] * len(data),
                data[subtitles].tolist() if subtitles else [""] * len(data),
                data[markers].tolist() if markers else [[]] * len(data),
                data[measures].tolist() if measures else [[]] * len(data),
                data[ranges].tolist() if ranges else [[]] * len(data),
            ],
            index=col_names,
        )
    df = df.transpose()

    # make sure ranges, measures, 'markers' are not NAN or NONE
    for needed_key in ["ranges", "measures", "markers"]:
        for idx, r in enumerate(df[needed_key]):
            try:
                if r is None or (isinstance(r, float) and math.isnan(r)):
                    df.at[idx, needed_key] = []
            except TypeError:
                pass

    # validate custom colors (don't call convert_colors_to_same_type; it returns new list, but not used)
    for colors_list in [range_colors, measure_colors]:
        if colors_list and len(colors_list) != 2:
            raise exceptions.PlotlyError(
                "Both 'range_colors' or 'measure_colors' must be a list of two valid colors."
            )
        clrs.validate_colors(colors_list)

    # default scatter options
    default_scatter = {
        "marker": {"size": 12, "symbol": "diamond-tall", "color": "rgb(0, 0, 0)"}
    }
    marker_opts = scatter_options.get("marker", {})
    if not marker_opts:
        scatter_options["marker"] = default_scatter["marker"].copy()
    else:
        for k, v in default_scatter["marker"].items():
            marker_opts.setdefault(k, v)

    fig = _bullet(
        df,
        markers,
        measures,
        ranges,
        subtitles,
        titles,
        orientation,
        range_colors,
        measure_colors,
        horizontal_spacing,
        vertical_spacing,
        scatter_options,
        layout_options,
    )

    return fig
