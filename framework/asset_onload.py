import copy
from threading import Lock
from enum import Enum
from PIL import Image
import framework.phase_logger as logger
import framework.asset_load as loader
import framework.license as licenser


def get_order_val(op_tuple: tuple) -> int:
    return op_tuple[0]


class SupportedOnLoadFunctions(Enum):
    TILE = "tile"
    SCALE = "scale"
    CROP = "crop"
    ROTATE = "rotate"
    TRANSLATE = "translate"
    # TODO: implement TINT/HUE/FILTER


class AssetParserSingletonManager(type):
    """
    Singleton metaclass for managing the AssetLoader singleton. Do not attempt to directly instantiate, reference
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


class EffectResolution:
    def __init__(self, res_str: str) -> None:
        if "x" not in res_str:
            self.x = int(res_str)
        else:
            _x = res_str.split("x")[0]
            _y = res_str.split("x")[1]
            self.x = int(_x) if _x != "" else None
            self.y = int(_y) if _x != "" else None

    def get_tup(self) -> tuple[int, int]:
        _x = self.x if self.x is not None else -1
        _y = self.y if self.y is not None else -1
        return _x, _y


class PixelBox:
    def __init__(self, res_list: list[int]) -> None:
        self.tup = None
        if len(res_list) == 1:
            self.tup = (res_list[0], res_list[0], res_list[0], res_list[0])
        elif len(res_list) == 2:
            self.tup = (0, 0, res_list[0], res_list[1])
        elif len(res_list) == 3:
            self.tup = (0, res_list[0], res_list[1], res_list[2])
        elif len(res_list) == 4:
            self.tup = (res_list[0], res_list[1], res_list[2], res_list[3])


class AssetOnLoad:
    def __init__(self, on_load_dict: dict) -> None:
        self.operations: list[tuple[int, SupportedOnLoadFunctions, dict]] = []
        for on_load_func in on_load_dict.keys():
            _on_load_function = SupportedOnLoadFunctions(on_load_func)
            _params = {
                "amount": on_load_dict[on_load_func]["amount"]
            }
            self.operations.append((on_load_dict[on_load_func]["order"], _on_load_function, _params))
        self.operations.sort(key=get_order_val)


class ParseAsset:
    def __init__(self, asset: loader.LoadAsset):
        self.asset = asset
        self.license = licenser.AssetLicense(self.asset.license)
        self.on_load = AssetOnLoad(self.asset.on_load)
        self.modified_image: Image = None
        self.logger: logger.AssetModifyPhaseLogger = logger.AssetModifyPhaseLogger()

        for op in self.on_load.operations:
            _image = None
            if self.modified_image is not None:
                _image = self.modified_image
            else:
                _image = self.asset.image

            _res = None
            _val = None
            if "until_resolution" in op[2]["amount"].keys():
                _res = EffectResolution(op[2]["amount"]["until_resolution"])
            elif "by_value" in op[2]["amount"].keys():
                _val = PixelBox(op[2]["amount"]["by_value"])
            pre_image_res = (_image.width, _image.height)

            if op[1] == SupportedOnLoadFunctions.CROP:
                if _res:
                    _centre_xy = (int(pre_image_res[0] / 2), int(pre_image_res[1] / 2))
                    _half_crop_width = int(_res.x/2) if _res.x is not None else 0
                    _half_crop_height = int(_res.y/2) if _res.y is not None else 0

                    _val_1 = (_centre_xy[0] - _half_crop_width) if _half_crop_width != 0 else 0
                    _val_2 = (_centre_xy[1] - _half_crop_height) if _half_crop_height != 0 else 0

                    _val_3 = (_centre_xy[0] + _half_crop_width) if _half_crop_width != 0 else pre_image_res[0]-1
                    _val_4 = (_centre_xy[1] + _half_crop_height) if _half_crop_height != 0 else pre_image_res[1]-1

                    self.modified_image = _image.crop(
                        (
                            _val_1,
                            _val_2,
                            _val_3,
                            _val_4
                         )
                    )
                    self.logger.log(logger.LoggingSeverities.LOW, f"Cropped {self.asset.nickname} by resolution")
                elif _val:
                    self.modified_image = _image.crop(
                        (
                            _val.tup[0],
                            _val.tup[1],
                            _val.tup[2],
                            _val.tup[3]
                        )
                    )
                    self.logger.log(logger.LoggingSeverities.LOW, f"Cropped {self.asset.nickname} by value box")
            elif op[1] == SupportedOnLoadFunctions.SCALE:
                if _res:
                    _tup = _res.get_tup()
                    if _tup[0] == -1:
                        _tup = (pre_image_res[0], _tup[1])
                    if _tup[1] == -1:
                        _tup = (_tup[0], pre_image_res[1])
                    self.modified_image = _image.resize(_tup)
                    self.logger.log(logger.LoggingSeverities.LOW, f"Scaled {self.asset.nickname} by resolution")
                elif _val:
                    _tup = (
                        pre_image_res[0] * _val.tup[2],
                        pre_image_res[1] * _val.tup[3],
                    )
                    self.modified_image = _image.resize(_tup)
                    self.logger.log(logger.LoggingSeverities.LOW, f"Scaled {self.asset.nickname} by value box")
            elif op[1] == SupportedOnLoadFunctions.TILE:
                if _res:
                    _tup = _res.get_tup()
                    if _tup[0] == -1:
                        _tup = (pre_image_res[0], _tup[1])
                    if _tup[1] == -1:
                        _tup = (_tup[0], pre_image_res[1])
                    _temp_image = Image.new('RGBA', _tup)

                    for i in range(0, _temp_image.width, pre_image_res[0]):
                        for j in range(0, _temp_image.height,  pre_image_res[1]):
                            _temp_image.paste(_image, (i, j))

                    self.modified_image = copy.deepcopy(_temp_image)
                    self.logger.log(logger.LoggingSeverities.LOW, f"Tiled {self.asset.nickname} by resolution")
                elif _val:
                    _tup = (
                        _val.tup[2] * pre_image_res[0],
                        _val.tup[3] * pre_image_res[1]
                    )
                    _temp_image = Image.new('RGBA', _tup)

                    for i in range(0, _temp_image.width, pre_image_res[0]):
                        for j in range(0, _temp_image.height, pre_image_res[1]):
                            _temp_image.paste(_image, (i, j))

                    self.modified_image = copy.deepcopy(_temp_image)
                    self.logger.log(logger.LoggingSeverities.LOW, f"Tiled {self.asset.nickname} by value box")


class AssetParser(metaclass=AssetParserSingletonManager):
    def __init__(self) -> None:
        self.loaded = loader.AssetLoader()  # Get singleton instance of AssetLoader
        self.parsed = [ParseAsset(asset_) for asset_ in self.loaded.assets]

    def save_test_images(self) -> None:
        _test_counter = 0
        self.parsed[0].logger.output()
        for parsed in self.parsed:
            parsed.modified_image.save(f"test_image_{_test_counter}.png", "PNG")
            _test_counter += 1
