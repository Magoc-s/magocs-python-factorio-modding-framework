import framework.asset_load as loader
from PIL import Image
from framework.license import AssetLicense
import framework.asset_load
import framework.asset_onload


class Assets:
    load_table: dict = None

    def __init__(self):
        self.load = framework.asset_load.AssetLoader()
        self.triggers = framework.asset_onload.AssetParser()

        self.load_table = {}
        for parsed_asset in self.triggers.parsed:
            self.load_table[parsed_asset.asset.nickname] = parsed_asset

    def dispose(self) -> None:
        self.load.dispose()
