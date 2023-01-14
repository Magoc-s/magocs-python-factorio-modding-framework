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


class AssetLicense(AbstractLicense):
    def __init__(self, license_dict: dict):
        super().__init__(license_dict)
