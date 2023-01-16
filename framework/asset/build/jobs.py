from __future__ import annotations
import framework.asset.asset_on_load as on_load
import framework.asset.build.build_meta_classes as build_meta
import framework.asset.manager.manager as manager


class AbstractAssetTask:
    def __init__(self, handler_ref: tuple[int, str]):
        self.composite_mask: on_load.ParseAsset | None = None
        self.asset_to_composite_with: on_load.ParseAsset | None = None
        self.naming_map: dict | None = None
        self.manager = manager.AssetManager()
        self.handler = handler_ref


class AssetCompositor(AbstractAssetTask):
    def __init__(self, handler_ref: tuple[int, str], job_dict: dict):
        """
        TODO: implement functionality to reference assets from outside of `load`, like `base`.
        :param job_dict:
        """
        super().__init__(handler_ref)

        _composite_target: str = job_dict["asset"].strip()
        self.asset_to_composite_with = self.manager.get(_composite_target)

        _mask_target: str = job_dict["mask"].strip()
        if _mask_target == "none":
            self.composite_mask = None
        else:
            self.composite_mask = self.manager.get(_mask_target)

        self.manager.register_substitution(
            self.handler,
            "$composite-target$",
            self.asset_to_composite_with.asset.nickname
        )
        if self.composite_mask is not None:
            self.manager.register_substitution(
                self.handler,
                "$mask-target$",
                self.composite_mask.asset.nickname
            )
