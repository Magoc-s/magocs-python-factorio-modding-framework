import os
import yaml
from PIL import Image
import framework.phase_logger as logger
import framework.asset.load.load_meta_classes as load_meta
import framework.license as license

BUILDABLE_ASSETS_PATH = 'mod/build/assets/'
BUILDABLE_ASSETS_CONFIG_FILE = 'assets-config.yml'


class LoadAsset:
    """
    Takes a yaml dict of the specified asset from the conf file and imports the relevant data and loads the image
    asset using PIL.Image.

    ## Instance Methods:
        * self.dispose()

    ## Instance Vars:
        * self.path
        * self.nickname
        * self.image
        * self.finalised
    """
    class AssetAlreadyDisposedException(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    def __init__(self, yaml_key: dict) -> None:
        self.nickname: str = list(yaml_key.keys())[0]
        self.path: str = yaml_key[self.nickname]["path"]
        self.image: Image = Image.open(os.path.join(BUILDABLE_ASSETS_PATH, self.path))
        self.finalised: bool = False
        self.license: dict = yaml_key[self.nickname]["licensing"]
        # self.license: license.AssetLicense = license.AssetLicense(yaml_key[self.nickname]["licensing"])
        self.on_load: dict = yaml_key[self.nickname]["on_load"] if "on_load" in yaml_key[self.nickname].keys() else None

    def dispose(self) -> None:
        if self.finalised:
            raise self.AssetAlreadyDisposedException(f"{self.__repr__()} already disposed of.")
        if self.image is not None:
            self.image.close()
            self.finalised = True

    def __repr__(self):
        return f"{self.nickname} [{self.path}] => {self.image}"


class AssetLoader(metaclass=load_meta.AssetLoaderSingletonManager):
    """
    The AssetLoader is a (thread-safe) singleton class designed to read the `load` key of the
    assets-config.yml file and load each respective asset mentioned there, storing a list of
    LoadAsset objects. Essentially this class acts as its own self-contained factory object
    for the LoadAsset class. I optionally choose to follow design patterns.

    WARNING: ALWAYS call this.dispose() at the end of code. (The LoadAsset objects do not implicitly
    close their open fd's). This is to ensure thread and runtime safety. The python GC will automatically
    and implicitly close FDs when no longer referenced, but we will not rely on implicit behaviour.

    ## Instance Methods:
        * self.dispose()
        * self.log_assets()

    ## Instance Vars:
        * self.conf
        * self.assets
    """
    class NoLoadableAssetsPresentException(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    conf: dict = None
    assets: list[LoadAsset] = None

    def __init__(self):
        if not os.path.exists(BUILDABLE_ASSETS_PATH):
            raise self.NoLoadableAssetsPresentException(f"{BUILDABLE_ASSETS_PATH=} not present.")
        self.logger = logger.AssetLoadPhaseLogger()
        with open(BUILDABLE_ASSETS_PATH + BUILDABLE_ASSETS_CONFIG_FILE, 'r') as h:
            self.conf: dict = yaml.safe_load(h)
        self.assets: list[LoadAsset] = []
        for asset_key in self.conf["load"].keys():
            self.assets.append(LoadAsset({asset_key: self.conf["load"][asset_key]}))
            self.logger.log(logger.LoggingSeverities.LOW, f"Loaded asset {asset_key}")
        self.logger.output()

    def dispose(self):
        for asset in self.assets:
            try:
                asset.dispose()
            except LoadAsset.AssetAlreadyDisposedException:
                self.logger.log(
                    logger.LoggingSeverities.MEDIUM,
                    f"Asset {asset.nickname} attempted to be disposed() when already finalised."
                )
        self.logger.output()
