from enum import Enum


class LicenseTypes(Enum):
    CreativeCommons = "CC0"
    CreativeCommons_1 = "CC 1.0"
    CreativeCommonsBY = "CC BY"
    CreativeCommonsBY_SA = "CC BY-SA"
    CreativeCommonsBY_NC = "CC BY-NC"
    CreativeCommonsBY_NC_SA = "CC BY-NC-SA"
    CreativeCommonsBY_ND = "CC BY-ND"
    CreativeCommonsBY_NC_ND = "CC BY-NC-ND"

    Apache_2_0 = "Apache 2.0"

    MIT = "MIT"

    GNU_GPL_Long = "GNU General Public License"
    GNU_GPL = "GNU GPL"
    GNU_LGPL_Long = "GNU Lesser General Public License"
    GNU_LGPL = "GNU LGPL"


class AbstractLicense:
    license: LicenseTypes = None
    attribution: str = None
    url: str = None

    def __init__(self, license_dict: dict):
        self.license = LicenseTypes(license_dict["license"].upper())
        self.attribution = license_dict["attribution"]
        self.url = license_dict["url"]

    def substitute_url(self, sub_map: dict) -> None:
        _substituted = self.url
        for sub_string in sub_map.keys():
            if sub_string in _substituted:
                _substituted = _substituted.replace(sub_string, sub_map[sub_string])
        self.url = _substituted


class AssetLicense(AbstractLicense):
    def __init__(self, license_dict: dict):
        super().__init__(license_dict)
