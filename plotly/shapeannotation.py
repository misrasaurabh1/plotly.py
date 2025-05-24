# some functions defined here to avoid numpy import


def _mean(x):
    if len(x) == 0:
        raise ValueError("x must have positive length")
    return float(sum(x)) / len(x)


def _argmin(x):
    return sorted(enumerate(x), key=lambda t: t[1])[0][0]


def _argmax(x):
    return sorted(enumerate(x), key=lambda t: t[1], reverse=True)[0][0]


def _df_anno(xanchor, yanchor, x, y):
    """Default annotation parameters"""
    return dict(xanchor=xanchor, yanchor=yanchor, x=x, y=y, showarrow=False)


def _add_inside_to_position(pos):
    if not ("inside" in pos or "outside" in pos):
        pos.add("inside")
    return pos


def _prepare_position(position, prepend_inside=False):
    if position is None:
        position = "top right"
    pos_str = position
    position = set(position.split(" "))
    if prepend_inside:
        position = _add_inside_to_position(position)
    return position, pos_str


def annotation_params_for_line(shape_type, shape_args, position):
    # all x0, x1, y0, y1 are used to place the annotation, that way it could
    # work with a slanted line
    # even with a slanted line, there are the horizontal and vertical
    # conventions of placing a shape

    x0 = shape_args["x0"]
    x1 = shape_args["x1"]
    y0 = shape_args["y0"]
    y1 = shape_args["y1"]

    # Save memory by using tuples instead of lists
    X = (x0, x1)
    Y = (y0, y1)
    R = "right"
    T = "top"
    L = "left"
    C = "center"
    B = "bottom"
    M = "middle"

    # Compute values once
    aY, iY = (y1, y0) if y1 > y0 else (y0, y1)
    eY = _mean(Y)
    aaY = 0 if y0 >= y1 else 1
    aiY = 0 if y0 <= y1 else 1

    aX, iX = (x1, x0) if x1 > x0 else (x0, x1)
    eX = _mean(X)
    aaX = 0 if x0 >= x1 else 1
    aiX = 0 if x0 <= x1 else 1

    position_set, pos_str = _prepare_position(position)

    # Below: Use frozenset and dict lookup to avoid many set constructions
    if shape_type == "vline":
        key = frozenset(position_set)
        # Compose mapping keys before blocks to single-pass fast lookup
        mapping = {
            frozenset(("top", "left")):   (R, T, X[aaY], aY),
            frozenset(("top", "right")):  (L, T, X[aaY], aY),
            frozenset(("top",)):          (C, B, X[aaY], aY),
            frozenset(("bottom", "left")):(R, B, X[aiY], iY),
            frozenset(("bottom", "right")):(L, B, X[aiY], iY),
            frozenset(("bottom",)):       (C, T, X[aiY], iY),
            frozenset(("left",)):         (R, M, eX, eY),
            frozenset(("right",)):        (L, M, eX, eY)
        }
        if key in mapping:
            return _df_anno(*mapping[key][:2], mapping[key][2], mapping[key][3])
    elif shape_type == "hline":
        key = frozenset(position_set)
        mapping = {
            frozenset(("top", "left")):   (L, B, iX, Y[aiX]),
            frozenset(("top", "right")):  (R, B, aX, Y[aaX]),
            frozenset(("top",)):          (C, B, eX, eY),
            frozenset(("bottom", "left")):(L, T, iX, Y[aiX]),
            frozenset(("bottom", "right")):(R, T, aX, Y[aaX]),
            frozenset(("bottom",)):       (C, T, eX, eY),
            frozenset(("left",)):         (R, M, iX, Y[aiX]),
            frozenset(("right",)):        (L, M, aX, Y[aaX]),
        }
        if key in mapping:
            return _df_anno(*mapping[key][:2], mapping[key][2], mapping[key][3])
    raise ValueError('Invalid annotation position "%s"' % (pos_str,))


def annotation_params_for_rect(shape_type, shape_args, position):
    x0 = shape_args["x0"]
    x1 = shape_args["x1"]
    y0 = shape_args["y0"]
    y1 = shape_args["y1"]

    min_x, max_x = (x0, x1) if x0 <= x1 else (x1, x0)
    min_y, max_y = (y0, y1) if y0 <= y1 else (y1, y0)

    mean_x = _mean((x0, x1))
    mean_y = _mean((y0, y1))

    position_set, pos_str = _prepare_position(position, prepend_inside=True)
    key = frozenset(position_set)

    # Use mapping dictionary for fast lookup and minimize temporary values
    inside_mapping = {
        frozenset(("inside", "top", "left")):    ("left", "top", min_x, max_y),
        frozenset(("inside", "top", "right")):   ("right", "top", max_x, max_y),
        frozenset(("inside", "top")):            ("center", "top", mean_x, max_y),
        frozenset(("inside", "bottom", "left")): ("left", "bottom", min_x, min_y),
        frozenset(("inside", "bottom", "right")):("right", "bottom", max_x, min_y),
        frozenset(("inside", "bottom")):         ("center", "bottom", mean_x, min_y),
        frozenset(("inside", "left")):           ("left", "middle", min_x, mean_y),
        frozenset(("inside", "right")):          ("right", "middle", max_x, mean_y),
        frozenset(("inside",)):                  ("center", "middle", mean_x, mean_y)
    }
    if key in inside_mapping:
        vals = inside_mapping[key]
        return _df_anno(*vals)
    outside_mapping = {
        frozenset(("outside", "top", "left")): (
            "right" if shape_type == "vrect" else "left",
            "bottom" if shape_type == "hrect" else "top",
            min_x, max_y
        ),
        frozenset(("outside", "top", "right")): (
            "left" if shape_type == "vrect" else "right",
            "bottom" if shape_type == "hrect" else "top",
            max_x, max_y
        ),
        frozenset(("outside", "top")): (
            "center", "bottom", mean_x, max_y
        ),
        frozenset(("outside", "bottom", "left")): (
            "right" if shape_type == "vrect" else "left",
            "top" if shape_type == "hrect" else "bottom",
            min_x, min_y
        ),
        frozenset(("outside", "bottom", "right")): (
            "left" if shape_type == "vrect" else "right",
            "top" if shape_type == "hrect" else "bottom",
            max_x, min_y
        ),
        frozenset(("outside", "bottom")): (
            "center", "top", mean_x, min_y
        ),
        frozenset(("outside", "left")): (
            "right", "middle", min_x, mean_y
        ),
        frozenset(("outside", "right")): (
            "left", "middle", max_x, mean_y
        )
    }
    if key in outside_mapping:
        vals = outside_mapping[key]
        return _df_anno(*vals)
    raise ValueError("Invalid annotation position %s" % (pos_str,))


def axis_spanning_shape_annotation(annotation, shape_type, shape_args, kwargs):
    """
    annotation: a go.layout.Annotation object, a dict describing an annotation, or None
    shape_type: one of 'vline', 'hline', 'vrect', 'hrect' and determines how the
                x, y, xanchor, and yanchor values are set.
    shape_args: the parameters used to draw the shape, which are used to place the annotation
    kwargs:     a dictionary that was the kwargs of a
                _process_multiple_axis_spanning_shapes spanning shapes call. Items in this
                dict whose keys start with 'annotation_' will be extracted and the keys with
                the 'annotation_' part stripped off will be used to assign properties of the
                new annotation.

    Property precedence:
    The annotation's x, y, xanchor, and yanchor properties are set based on the
    shape_type argument. Each property already specified in the annotation or
    through kwargs will be left as is (not replaced by the value computed using
    shape_type). Note that the xref and yref properties will in general get
    overwritten if the result of this function is passed to an add_annotation
    called with the row and col parameters specified.

    Returns an annotation populated with fields based on the
    annotation_position, annotation_ prefixed kwargs or the original annotation
    passed in to this function.
    """
    prefix = "annotation_"
    len_prefix = len(prefix)
    # Only iterate once (generator) and collect to list if nonempty
    annotation_keys = [k for k in kwargs if k.startswith(prefix)]

    if annotation is None and not annotation_keys:
        return None
    if annotation is None:
        annotation = {}

    # Avoid redundant .keys() and not needed lambda filtering
    for k in annotation_keys:
        if k == "annotation_position":
            continue
        subk = k[len_prefix:]
        annotation[subk] = kwargs[k]

    # Only lookup position once
    annotation_position = kwargs.get("annotation_position", None)

    if shape_type.endswith("line"):
        shape_dict = annotation_params_for_line(
            shape_type, shape_args, annotation_position
        )
    elif shape_type.endswith("rect"):
        shape_dict = annotation_params_for_rect(
            shape_type, shape_args, annotation_position
        )
    else:
        shape_dict = {}

    # Avoid calling dict.keys() multiple times
    for k, v in shape_dict.items():
        if (k not in annotation) or (annotation[k] is None):
            annotation[k] = v
    return annotation


def split_dict_by_key_prefix(d, prefix):
    """
    Returns two dictionaries, one containing all the items whose keys do not
    start with a prefix and another containing all the items whose keys do start
    with the prefix. Note that the prefix is not removed from the keys.
    """
    no_prefix = dict()
    with_prefix = dict()
    for k in d.keys():
        if k.startswith(prefix):
            with_prefix[k] = d[k]
        else:
            no_prefix[k] = d[k]
    return (no_prefix, with_prefix)
