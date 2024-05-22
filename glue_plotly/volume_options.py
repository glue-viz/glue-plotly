import os

from qtpy.QtWidgets import QDialog

from echo import CallbackProperty, SelectionCallbackProperty
from echo.qt import autoconnect_callbacks_to_qt

from glue.core.data_combo_helper import ComboHelper
from glue.core.state_objects import State
from glue_qt.utils import load_ui


class VolumeDialogState(State):

    layer = SelectionCallbackProperty()
    isosurface_count = CallbackProperty(5)

    def __init__(self, layers):
        super(VolumeDialogState, self).__init__()

        self.layers = layers

        self.layer_helper = ComboHelper(self, 'layer')
        self.layer_helper.choices = [state.layer.label for state in self.layers]


class VolumeOptionsDialog(QDialog):

    def __init__(self, parent=None, viewer=None):

        super(VolumeOptionsDialog, self).__init__(parent=parent)

        self.viewer = viewer
        layers = [layer for layer in self.viewer.layers if layer.enabled and layer.state.visible]
        self.state = VolumeDialogState(layers)
        self.ui = load_ui('volume_options.ui', self, directory=os.path.dirname(__file__))
        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui)

        self.state_dictionary = { layer.layer.label: {} for layer in layers }

        self.ui.button_cancel.clicked.connect(self.reject)
        self.ui.button_ok.clicked.connect(self.accept)

        self.state.add_callback('layer', self._on_layer_change)
        self.state.add_callback('isosurface_count', self._on_isosurface_count_change)

    def _on_layer_change(self, layer):
        count = self.state_dictionary[self.state.layer].get("isosurface_count", 5)
        self.ui.valuetext_isosurface_count.setText(int(count))

    def _on_isosurface_count_change(self, count):
        self.state_dictionary[self.state.layer]["isosurface_count"] = int(count)
