from __future__ import annotations
import os
import yaml
from threading import Lock
from PIL import Image
import framework.phase_logger as logger
import framework.asset_load as loader
import framework.asset_onload as on_load
import re


BUILT_ASSETS_PATH = 'mod/assets/'
SUBSTITUTION_REGEX = r"\$[^\$]+\$"


class AssetBuilderSingletonManager(type):
    """
    Singleton metaclass for managing the AssetBuilder singleton. Do not attempt to directly instantiate, reference
    or otherwise use this class. Its function is autonomous.
    """
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class LoadTableSingletonManager(type):
    """
    Singleton metaclass for managing the LoadTable singleton. Do not attempt to directly instantiate, reference
    or otherwise use this class. Its function is autonomous.
    """
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


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


class AbstractAssetTask:
    def __init__(self):
        self.composite_mask: on_load.ParseAsset | None = None
        self.asset_to_composite_with: on_load.ParseAsset | None = None
        self.naming_map: dict | None = None


class AssetCompositor(AbstractAssetTask):
    def __init__(self, job_dict: dict):
        """
        TODO: implement functionality to reference assets from outside of `load`, like `base`.
        :param job_dict:
        """
        super().__init__()

        _composite_target: str = job_dict["asset"].strip()
        if _composite_target.startswith("load."):
            self.asset_to_composite_with = LoadTable().get_ref()[_composite_target.replace("load.", "", 1)]

        _mask_target: str = job_dict["mask"].strip()
        if _mask_target == "none":
            self.composite_mask = None
        elif _mask_target.startswith("load."):
            self.composite_mask = LoadTable().get_ref()[_mask_target.replace("load.", "", 1)]

        self.naming_map = {
            "$mask-target$": str(_mask_target).replace("load.", "", 1),
            "$composite-target$": str(_composite_target).replace("load.", "", 1)
        }

    def get_naming_map(self) -> dict:
        return self.naming_map


class BuildAsset:
    def __init__(self, yaml_dict: dict) -> None:
        self.build_reference = list(yaml_dict.keys())[0]
        self.output_type = yaml_dict[self.build_reference]["outputs"]["filetype"]
        self.output_dir = BUILT_ASSETS_PATH + yaml_dict[self.build_reference]["outputs"]["dir"]

        self.naming_scheme: BuiltAssetNamer = BuiltAssetNamer(yaml_dict[self.build_reference]["outputs"]["name"])

        _use_asset: str = yaml_dict[self.build_reference]["use"].strip()
        if _use_asset.startswith("load."):
            self.base_asset: on_load.ParseAsset = \
                LoadTable().get_ref()[_use_asset.replace("load.", "", 1)]

        self.jobs: list[tuple[str, AbstractAssetTask]] = []
        for job in yaml_dict[self.build_reference]["jobs"]:
            if list(job.keys())[0] == "composite-with":
                _compositor = AssetCompositor(job["composite-with"])
                _job_name = self.naming_scheme.perform_substitution(_compositor.get_naming_map())
                self.jobs.append((_job_name, _compositor))

        for name, job in self.jobs:
            if job is AssetCompositor:
                _composited_image = None
                if job.composite_mask is not None:
                    _composited_image = Image.composite(
                        self.base_asset.modified_image,
                        job.asset_to_composite_with.modified_image,
                        job.composite_mask.modified_image
                    )
                else:
                    _composited_image = Image.alpha_composite(
                        self.base_asset.modified_image,
                        job.asset_to_composite_with.modified_image
                    )
                _composited_image.save(os.path.join(self.output_dir, name), self.output_type)


class AssetBuilder(metaclass=AssetBuilderSingletonManager):
    def __init__(self) -> None:
        self.build_table = loader.AssetLoader().conf["build"]
        self.built: list[BuildAsset] = []
        self.logger: logger.AssetOutputPhaseLogger = logger.AssetOutputPhaseLogger()

        for build_target in self.build_table.keys():
            self.logger.log(f"Building {build_target}")
            self.built.append(BuildAsset({build_target: self.build_table[build_target]}))


class LoadTable(metaclass=LoadTableSingletonManager):
    class LoadTableNotLoadedYetError(Exception):
        def __init__(self, *args) -> None:
            super().__init__(*args)

    class LoadTableAlreadyLoadedError(Exception):
        def __init__(self, *args) -> None:
            super().__init__(*args)

    _load_table: dict | None = None

    def __init__(self):
        self._load_table = None

    def set_ref(self, load_table_ref: dict):
        if self._load_table is not None:
            raise self.LoadTableAlreadyLoadedError(f"LoadTable is NOT none.")
        self._load_table = load_table_ref

    def get_ref(self) -> dict:
        if self._load_table is None:
            raise self.LoadTableNotLoadedYetError(f"LoadTable is none.")
        return self._load_table
