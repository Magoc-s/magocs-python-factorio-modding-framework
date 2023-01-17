import framework.asset.asset_load as loader
import framework.asset.asset_load
import framework.asset.asset_on_load
import framework.asset.asset_build
import framework.asset.build.build_meta_classes
import framework.asset.manager.manager
import framework.conf.mod_config


class Assets:
    load_table: dict = None

    def __init__(self):
        self.manager = framework.asset.manager.manager.AssetManager()

        self.config = framework.conf.mod_config.ModConfigLoader()

        self.load = framework.asset.asset_load.AssetLoader()
        self.triggers = framework.asset.asset_on_load.AssetParser()

        for parsed_asset in self.triggers.parsed:
            self.manager.register_asset(parsed_asset.asset.nickname, parsed_asset, "load")

        self.build = framework.asset.asset_build.AssetBuilder()

    def dispose(self) -> None:
        self.load.dispose()
