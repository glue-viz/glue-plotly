import os

from echo import ChoiceSeparator
from echo.qt import autoconnect_callbacks_to_qt
from glue_qt.utils import load_ui
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog, QListWidgetItem

from glue_plotly.html_exporters.base_save_hover import BaseSaveHoverDialog

__all__ = ["SaveHoverDialog"]


class SaveHoverDialog(BaseSaveHoverDialog, QDialog):

    def __init__(self, data_collection=None, parent=None, checked_dictionary=None):

        BaseSaveHoverDialog.__init__(self,
                                     data_collection=data_collection,
                                     checked_dictionary=checked_dictionary)
        QDialog.__init__(self, parent=parent)

        self.ui = load_ui("save_hover.ui", self,
                          directory=os.path.dirname(__file__))

        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui)

        self.ui.button_cancel.clicked.connect(self.reject)
        self.ui.button_ok.clicked.connect(self.accept)
        self.ui.button_select_none.clicked.connect(self.select_none)
        self.ui.button_select_all.clicked.connect(self.select_all)

        self.ui.list_component.itemChanged.connect(self._on_check_change)

        self._on_component_change()

    def _on_component_change(self, *event):
        super()._on_component_change(*event)

        components = type(self.state).component.get_choices(self.state)
        self.ui.list_component.clear()

        for component in components:

            if isinstance(component, ChoiceSeparator):
                item = QListWidgetItem(str(component))
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                item.setForeground(Qt.gray)
            else:
                item = QListWidgetItem(component.label)
                data_label = self.state.data.label
                if self.checked_dictionary[data_label].get(component.label, False):
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)

            self.ui.list_component.addItem(item)

    def _on_check_change(self, *event):

        current_layer = self.state.data.label
        any_checked = False
        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            label = item.text()
            checked = item.checkState() == Qt.Checked
            any_checked = any_checked or checked
            self.checked_dictionary[current_layer][label] = checked

        self.button_ok.setEnabled(any_checked)

    def select_none(self, *event):
        self._set_all_checked(False)

    def select_all(self, *event):
        self._set_all_checked(True)

    def _set_all_checked(self, checked):
        state = Qt.Checked if checked else Qt.Unchecked
        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            item.setCheckState(state)
