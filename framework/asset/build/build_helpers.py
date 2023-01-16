import re
import framework.asset.manager.manager
import framework.phase_logger

SUBSTITUTION_REGEX = r"\$[^\$]+\$"
BUILT_ASSETS_PATH = 'mod/assets/'


class BuiltAssetNamer:
    def __init__(self, name_spec_str: str) -> None:
        self.raw_name = name_spec_str
        self.replaceable = re.findall(SUBSTITUTION_REGEX, self.raw_name)
        self.logger = framework.phase_logger.AssetManagerLogger()

    def perform_substitution(self, handler_ref: tuple[int, str]) -> str:
        self.logger.log(framework.phase_logger.LoggingSeverities.LOG, f"Running name-substitution on {self.raw_name}.")
        _substituted = self.raw_name
        _manager = framework.asset.manager.manager.AssetManager()
        _map = _manager.name_substitutions(handler_ref)
        for repl, replace_with in _map:
            if repl in _substituted:
                _substituted = _substituted.replace(repl, replace_with)
                self.logger.log(
                    framework.phase_logger.LoggingSeverities.LOG,
                    f"+--> substituted {repl} with {replace_with}."
                )
        return _substituted
