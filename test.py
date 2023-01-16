import framework.asset.asset
import framework.phase_logger

_inst = framework.asset.asset.Assets()
# _inst.triggers.save_test_images()
_inst.dispose()

_inst.load.logger.output()
framework.phase_logger.AssetModifyPhaseLogger().output()
_inst.manager.logger.output()
_inst.build.logger.output()


