import importlib
from _plotly_utils.basevalidators import LiteralValidator


class ValidatorCache(object):
    _cache = {}

    @staticmethod
    def get_validator(parent_path, prop_name):
        # Use a local reference to the cache for faster access
        cache = ValidatorCache._cache
        key = (parent_path, prop_name)

        if key not in cache:

            if "." not in parent_path and prop_name == "type":
                # Special case for .type property of traces
                validator = LiteralValidator("type", parent_path, parent_path)
            else:
                lookup_name = None
                if parent_path == "layout":
                    from .graph_objects import Layout

                    match = Layout._subplotid_prop_re.match(prop_name)
                    if match:
                        lookup_name = match.group(1)

                if not lookup_name:
                    lookup_name = prop_name
                # Use f-string for string formatting
                class_name = f"{lookup_name.title()}Validator"
                # Cache imported functions locally
                module = importlib.import_module(f"plotly.validators.{parent_path}")
                validator_class = getattr(module, class_name)
                validator = validator_class(plotly_name=prop_name)

            cache[key] = validator

        return cache[key]
