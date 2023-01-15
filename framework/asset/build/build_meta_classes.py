from __future__ import annotations
from threading import Lock


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
