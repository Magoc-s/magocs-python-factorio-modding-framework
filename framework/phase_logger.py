import sys
from threading import Lock
from enum import Enum

class LoggingSeverities(Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    SEVERE = "Severe"
    CRITICAL = "Critical"


class LoggingColours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    SEVERITY_TO_COL_MAP = {
        LoggingSeverities.LOW: [OKBLUE],
        LoggingSeverities.MEDIUM: [WARNING],
        LoggingSeverities.HIGH: [BOLD, WARNING],
        LoggingSeverities.SEVERE: [FAIL],
        LoggingSeverities.CRITICAL: [BOLD, FAIL]
    }

    def log(self, log_tup: tuple[LoggingSeverities, str]) -> str:
        _codes = self.SEVERITY_TO_COL_MAP[log_tup[0]]
        _str = ""
        for code in _codes:
            _str += code
        _str += log_tup[1]
        _str += self.ENDC
        return _str


class AssetLoadPhaseLoggerSingletonManager(type):
    """
    Singleton metaclass for managing the AssetLoadPhaseLogger singleton. Do not attempt to directly instantiate,
    reference or otherwise use this class. Its function is autonomous.
    """
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class AssetModifyPhaseLoggerSingletonManager(type):
    """
    Singleton metaclass for managing the AssetModifyPhaseLogger singleton. Do not attempt to directly instantiate,
    reference or otherwise use this class. Its function is autonomous.
    """
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class AbstractLogger:
    class CriticalLogRecievedError(Exception):
        def __init__(self, *args):
            super().__init__(*args)

    lines: list[(LoggingSeverities, str)] = None
    logger_pprint: LoggingColours = LoggingColours()

    def __init__(self):
        self.lines = []

    def output(self, filename: str = None, flush: bool = True) -> None:
        """
        output the currently stored logging data in `self.lines` to a file of the given filename.
        If no filename is given, send to `stdout`.

        :param filename: [optional] name of the file to write log output too. stdout if not specified.
        :param flush: [optional] whether to flush the `self.lines` list once output.
        :return: None
        """
        _sep = "\n\n" if len(self.lines) > 0 else ""
        _log = "\n".join(self.lines) + _sep
        if filename:
            fd = open(filename)
        else:
            fd = sys.stdout
        fd.write(_log)
        if fd is not sys.stdout:
            fd.close()
        if flush:
            self.lines = []


class AssetLoadPhaseLogger(AbstractLogger, metaclass=AssetLoadPhaseLoggerSingletonManager):

    def __init__(self):
        super().__init__()

    def log(self, severity: LoggingSeverities, log: str) -> None:
        """
        Add a log line to the class `self.lines` instance var.

        Raises:
            AbstractLogger.CriticalLogRecievedError if a log of SEVERE or CRITICAL severity is added.
            Do not attempt to catch this exception as the program has entered an unrecoverable state.

        :param severity: A LoggingSeverities enum element indicating the severity of the logged event.
        :param log: A string describing the event.
        :return: None
        """
        self.lines.append(self.logger_pprint.log((severity, log)))
        if severity == LoggingSeverities.CRITICAL or severity == LoggingSeverities.SEVERE:
            _log = "\n".join(self.lines)
            raise self.CriticalLogRecievedError(_log)


class AssetModifyPhaseLogger(AbstractLogger, metaclass=AssetModifyPhaseLoggerSingletonManager):

    def __init__(self):
        super().__init__()


    def log(self, severity: LoggingSeverities, log: str) -> None:
        """
        Add a log line to the class `self.lines` instance var.

        Raises:
            AbstractLogger.CriticalLogRecievedError if a log of SEVERE or CRITICAL severity is added.
            Do not attempt to catch this exception as the program has entered an unrecoverable state.

        :param severity: A LoggingSeverities enum element indicating the severity of the logged event.
        :param log: A string describing the event.
        :return: None
        """
        self.lines.append(self.logger_pprint.log((severity, log)))
        if severity == LoggingSeverities.CRITICAL or severity == LoggingSeverities.SEVERE:
            _log = "\n".join(self.lines)
            raise self.CriticalLogRecievedError(_log)