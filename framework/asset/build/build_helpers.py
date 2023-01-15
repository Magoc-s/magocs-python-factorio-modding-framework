import re

SUBSTITUTION_REGEX = r"\$[^\$]+\$"
BUILT_ASSETS_PATH = 'mod/assets/'


class BuiltAssetNamer:
    def __init__(self, name_spec_str: str) -> None:
        self.raw_name = name_spec_str
        self.replaceable = re.findall(SUBSTITUTION_REGEX, self.raw_name)

    def perform_substitution(self, population_map: dict) -> str:
        _substituted = self.raw_name
        for sub_string in population_map.keys():
            if sub_string in _substituted:
                _substituted = _substituted.replace(sub_string, population_map[sub_string])
        return _substituted
