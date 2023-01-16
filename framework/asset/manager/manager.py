from __future__ import annotations
import framework.asset.manager.manager_meta_classes as manager_meta
import framework.phase_logger as logger
import framework.asset.asset_on_load as asset_on_load
import framework.asset.asset_build as asset_build


class AssetManager(metaclass=manager_meta.AssetManagerSingletonManager):
    class AssetNotFoundError(Exception):
        def __init__(self, *args) -> None:
            super().__init__(*args)

    logger: logger.AssetManagerLogger = None
    name_substitution_table: dict = None
    asset_nickname_ref_table: dict = None

    def __init__(self):
        if self.name_substitution_table is None:
            self.name_substitution_table = {}
        if self.asset_nickname_ref_table is None:
            self.asset_nickname_ref_table = {"load": {}, "build": {}, "base": {}}
        if self.logger is None:
            self.logger = logger.AssetManagerLogger()

    def register_substitution(self, context: tuple[int, str], replace: str, replace_with: str) -> None:
        if context[1] not in self.name_substitution_table.keys():
            self.name_substitution_table[context[1]] = {}
        if str(context[0]) not in self.name_substitution_table[context[1]].keys():
            self.name_substitution_table[context[1]][str(context[0])] = {}

        self.name_substitution_table[context[1]][str(context[0])][replace] = replace_with
        self.logger.log(
            logger.LoggingSeverities.LOW,
            f"Registered substitution in context {context[1]}-{context[0]}: "
            f"{replace} -> {replace_with}."
        )

    def register_asset(
            self,
            nickname: str,
            asset: asset_on_load.ParseAsset | asset_build.BuildAsset,
            phase: str
    ) -> None:
        self.asset_nickname_ref_table[phase][nickname] = asset
        self.logger.log(logger.LoggingSeverities.LOW, f"Registered asset: {phase}.{nickname}")

    def get(self, asset_nickname: str) -> asset_on_load.ParseAsset | asset_build.BuildAsset:
        _phase: str = asset_nickname.split(".")[0]
        _nickname: str = asset_nickname.split(".")[1]
        try:
            _asset_ref: asset_on_load.ParseAsset | asset_build.BuildAsset = \
                self.asset_nickname_ref_table[_phase][_nickname]
        except KeyError:
            raise self.AssetNotFoundError(f"Could not find key {asset_nickname} in table.")
        return _asset_ref

    def name_substitutions(self, context: tuple[int, str]) -> list[tuple[str, str]]:
        _map_with_context = self.name_substitution_table[context[1]][str(context[0])]
        _returnable = []
        for placeholder in _map_with_context.keys():
            _returnable.append((placeholder, _map_with_context[placeholder]))
        return _returnable
