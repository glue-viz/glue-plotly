from echo import CallbackProperty
from glue.config import DictRegistry
from glue.core.state_objects import State
from glue_vispy_viewers.volume.layer_state import VolumeLayerState


__all__ = ["qt_export_options", "VolumeExportOptionsState"]


class QtExportLayerOptionsRegistry(DictRegistry):

    def add(self, layer_state_cls, layer_options_state):
        if not issubclass(layer_options_state, State):
            raise ValueError("Layer options must be a glue State type")
        self._members[layer_state_cls] = layer_options_state

    def __call__(self, layer_state_cls):
        def adder(export_state_class):
            self.add(layer_state_cls, export_state_class)
        return adder


qt_export_options = QtExportLayerOptionsRegistry()


@qt_export_options(VolumeLayerState)
class VolumeExportOptionsState(State):
    isosurface_count = CallbackProperty(5)
