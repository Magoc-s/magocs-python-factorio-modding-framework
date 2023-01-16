from __future__ import annotations
from PIL import Image

import os

import framework.phase_logger as logger
import framework.asset.asset_load as loader
import framework.asset.asset_on_load as on_load
import framework.asset.build.build_meta_classes as build_meta
import framework.asset.build.jobs as jobs
import framework.asset.build.build_helpers as helpers
import framework.asset.manager.manager as manager


class BuildAsset:
    class UnrecognisedAssetBuildJobIdentifierException(Exception):
        def __init__(self, *args) -> None:
            super().__init__(*args)

    class UnrecognisedJobClassException(Exception):
        def __init__(self, *args) -> None:
            super().__init__(*args)

    def __init__(self, yaml_dict: dict) -> None:
        self.build_reference = list(yaml_dict.keys())[0]
        self.output_type = yaml_dict[self.build_reference]["outputs"]["filetype"]
        self.output_dir = helpers.BUILT_ASSETS_PATH + yaml_dict[self.build_reference]["outputs"]["dir"]

        self.logger = logger.AssetOutputPhaseLogger()
        self.manager = manager.AssetManager()

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        self.naming_scheme: helpers.BuiltAssetNamer = \
            helpers.BuiltAssetNamer(yaml_dict[self.build_reference]["outputs"]["name"])

        _use_asset: str = yaml_dict[self.build_reference]["use"].strip()
        self.base_asset: on_load.ParseAsset = self.manager.get(_use_asset)

        self.jobs: list[tuple[str, jobs.AbstractAssetTask]] = []
        for idx, job in enumerate(yaml_dict[self.build_reference]["jobs"]):
            _self_ref = (idx, self.build_reference)
            if list(job.keys())[0] == "composite-with":
                _compositor = jobs.AssetCompositor(_self_ref, job["composite-with"])
                _job_name = self.naming_scheme.perform_substitution(_self_ref)
                self.jobs.append((_job_name, _compositor))

        for name, job in self.jobs:
            _composited_image = self.job_runner(name, job)
            _composited_image.save(os.path.join(self.output_dir, name) + ".png", self.output_type)

    def job_runner(self, name, job) -> Image:
        _composited_image = None
        if type(job) is jobs.AssetCompositor:
            _composited_image = self._run_asset_compositor_job(name, job)

        if _composited_image is None:
            raise self.UnrecognisedJobClassException(f"Job type {job} unrecognised/not implemented.")

        self.manager.register_asset(name, self, "build")
        return _composited_image

    def _run_asset_compositor_job(self, name, job) -> Image:
        self.logger.log(logger.LoggingSeverities.LOW, f"Running AssetCompositor job on {name}.")
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
        return _composited_image


class AssetBuilder(metaclass=build_meta.AssetBuilderSingletonManager):
    def __init__(self) -> None:
        self.build_table = loader.AssetLoader().conf["build"]
        self.built: list[BuildAsset] = []
        self.logger: logger.AssetOutputPhaseLogger = logger.AssetOutputPhaseLogger()

        for build_target in self.build_table.keys():
            self.logger.log(logger.LoggingSeverities.LOW, f"Building {build_target}")
            self.built.append(BuildAsset({build_target: self.build_table[build_target]}))