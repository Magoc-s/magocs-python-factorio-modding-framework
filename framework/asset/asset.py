import framework.asset.asset_load as loader
import framework.asset.asset_load
import framework.asset.asset_on_load
import framework.asset.asset_build
import framework.asset.build.build_meta_classes


class Assets:
    load_table: dict = None

    def __init__(self):
        self.load = framework.asset.asset_load.AssetLoader()
        self.triggers = framework.asset.asset_on_load.AssetParser()

        self.load_table = {}
        for parsed_asset in self.triggers.parsed:
            self.load_table[parsed_asset.asset.nickname] = parsed_asset
        self.load_table_wrapper = framework.asset.build.build_meta_classes.LoadTable()
        self.load_table_wrapper.set_ref(self.load_table)

        self.build = framework.asset.asset_build.AssetBuilder()

    def dispose(self) -> None:
        self.load.dispose()
