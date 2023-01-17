import framework.asset.manager.manager as manager
from framework.conf.conf_meta_classes import ModConfigLoaderSingletonManager
import yaml


MOD_CONFIG_FILENAME: str = "mod-config.yml"
DEFAULT_CONTEXT_INSTANCE: int = 0


class ModConfigLoader(metaclass=ModConfigLoaderSingletonManager):
    def __init__(self) -> None:
        with open(MOD_CONFIG_FILENAME, 'r') as h:
            self.config_dict: dict = yaml.safe_load(h)

        self.manager = manager.AssetManager()
        _context_info: tuple[int, str] = (DEFAULT_CONTEXT_INSTANCE, "mod-info")
        for info in self.config_dict["info"].keys():
            if info is "dependencies":
                continue

            self.manager.register_substitution(_context_info, f"$mod.{info}$", self.config_dict["info"][info])

        _context_info: tuple[int, str] = (DEFAULT_CONTEXT_INSTANCE, "build-info")
        self.manager.register_substitution(_context_info, "$build.path_format$",
                                           self.config_dict["build"]["path_format"])
        self.manager.register_substitution(_context_info, "$build.zip_options.store_only$",
                                           self.config_dict["build"]["zip_options"]["store_only"])
        self.manager.register_substitution(_context_info, "$build.zip_options.refresh_only$",
                                           self.config_dict["build"]["zip_options"]["refresh_only"])
        self.manager.register_substitution(_context_info, "$build.factorio_dirs.game_path$",
                                           self.config_dict["build"]["factorio_dirs"]["game_path"])
        self.manager.register_substitution(_context_info, "$build.factorio_dirs.mods_path$",
                                           self.config_dict["build"]["factorio_dirs"]["mods_path"])