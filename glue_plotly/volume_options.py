import os

from echo import SelectionCallbackProperty
from echo.qt import autoconnect_callbacks_to_qt
from glue_qt.utils import load_ui
from qtpy.QtWidgets import QDialog

from glue.core.data_combo_helper import ComboHelper
from glue.core.state_objects import State
from glue_plotly.html_exporters.qt.options_state import qt_export_options
from glue_plotly.html_exporters.qt.utils import layer_label, update_layout_for_state

__all__ = ["VolumeOptionsDialog"]


class VolumeDialogState(State):
    """
    State class representing options for a Plotly volume export from glue.

    Attributes
    ----------
        layer (glue.core.layer.LayerArtist): The currently selected layer
        layers (List[glue.core.layer.LayerArtist]): The list of layers to be exported
    """

    layer = SelectionCallbackProperty()

    def __init__(self, layers):
        super().__init__()

        self.layers = layers
        self.layer_helper = ComboHelper(self, "layer")
        self.layer_helper.choices = [layer_label(state) for state in self.layers]


class VolumeOptionsDialog(QDialog):
    """Dialog providing a GUI for selecting options for a Plotly volume export."""

    def __init__(self, parent=None, viewer=None):

        super().__init__(parent=parent)

        self.viewer = viewer
        layers = [layer for layer in self.viewer.layers
                  if layer.enabled and layer.state.visible]
        self.state = VolumeDialogState(layers)
        self.ui = load_ui("volume_options.ui", self,
                          directory=os.path.dirname(__file__))
        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui)

        self.state_dictionary = {
            layer_label(layer): self.state_for_layer(layer)
            for layer in layers
        }

        self.ui.button_cancel.clicked.connect(self.reject)
        self.ui.button_ok.clicked.connect(self.accept)

        self.state.add_callback("layer", self._on_layer_change)

        self._on_layer_change(self.state.layer)

    def state_for_layer(self, layer):
        t = qt_export_options.members.get(type(layer.state), None)
        if t:
            return t()
        return None

    def _on_layer_change(self, layer):
        self._layer_connections = update_layout_for_state(
                                      self.ui.layer_layout,
                                      self.state_dictionary.get(layer, None))
