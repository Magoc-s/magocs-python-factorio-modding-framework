import framework.asset_load as loader
from PIL import Image
from framework.license import AssetLicense
import framework.asset_load
import framework.asset_onload


class Assets:
    def __init__(self):
        self.load = framework.asset_load.AssetLoader()
        self.triggers = framework.asset_onload.AssetParser()

    def dispose(self) -> None:
        self.load.dispose()
