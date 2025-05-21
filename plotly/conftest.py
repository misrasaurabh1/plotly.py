import os


def pytest_ignore_collect(path):
    # Ignored files, most of them are raising a chart studio error
    path_str = str(path)
    # Use set for O(1) lookup
    if (
        os.path.basename(path_str) in _IGNORED_PATHS_SET
        or "plotly/plotly/plotly/__init__.py" in path_str
        or "plotly/api/utils.py" in path_str
    ):
        return True

_IGNORED_PATHS_SET = {
    "exploding_module.py",
    "chunked_requests.py",
    "v2.py",
    "v1.py",
    "presentation_objs.py",
    "widgets.py",
    "dashboard_objs.py",
    "grid_objs.py",
    "config.py",
    "presentation_objs.py",
    "session.py",
}
