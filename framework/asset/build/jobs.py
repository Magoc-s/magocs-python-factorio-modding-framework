from __future__ import annotations
import framework.asset.asset_on_load as on_load
import framework.asset.build.build_meta_classes as build_meta


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
            self.asset_to_composite_with = build_meta.LoadTable().get_ref()[_composite_target.replace("load.", "", 1)]

        _mask_target: str = job_dict["mask"].strip()
        if _mask_target == "none":
            self.composite_mask = None
        elif _mask_target.startswith("load."):
            self.composite_mask = build_meta.LoadTable().get_ref()[_mask_target.replace("load.", "", 1)]

        self.naming_map = {
            "$mask-target$": str(_mask_target).replace("load.", "", 1),
            "$composite-target$": str(_composite_target).replace("load.", "", 1)
        }

    def get_naming_map(self) -> dict:
        return self.naming_map
