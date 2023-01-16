import framework.meta
from framework.meta import *


SEVERITIES = framework.meta.LoggingSeverities
COLOURS = framework.meta.LoggingColours


class AssetLoadPhaseLogger(AbstractLogger, metaclass=AssetLoadPhaseLoggerSingletonManager):
    def __init__(self):
        super().__init__()


class AssetModifyPhaseLogger(AbstractLogger, metaclass=AssetModifyPhaseLoggerSingletonManager):
    def __init__(self):
        super().__init__()


class AssetOutputPhaseLogger(AbstractLogger, metaclass=AssetOutputPhaseLoggerSingletonManager):
    def __init__(self):
        super().__init__()


class AssetManagerLogger(AbstractLogger, metaclass=AssetManagerLoggerSingletonManager):
    def __init__(self):
        super().__init__()
