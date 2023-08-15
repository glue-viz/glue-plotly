import os

from qtpy.QtWidgets import QDialog, QListWidgetItem
from qtpy.QtCore import Qt

from echo import ChoiceSeparator, SelectionCallbackProperty
from echo.qt import autoconnect_callbacks_to_qt

from glue import config
from glue.core.data_combo_helper import ComponentIDComboHelper, DataCollectionComboHelper
from glue.core.state_objects import State
from glue_qt.utils import load_ui

import numpy as np


__all__ = ['SaveHoverDialog']


class SaveHoverState(State):

    data = SelectionCallbackProperty()
    subset = SelectionCallbackProperty()
    component = SelectionCallbackProperty()
    exporter = SelectionCallbackProperty()

    def __init__(self, data_collection=None):

        super(SaveHoverState, self).__init__()

        self.data_helper = DataCollectionComboHelper(self, 'data', data_collection)
        self.component_helper = ComponentIDComboHelper(self, 'component',
                                                       data_collection=data_collection)

        self.add_callback('data', self._on_data_change)
        self._on_data_change()

        self._sync_data_exporters()

    def _sync_data_exporters(self):

        exporters = list(config.data_exporter)

        def display_func(exporter):
            if exporter.extension == '':
                return "{0} (*)".format(exporter.label)
            else:
                return "{0} ({1})".format(exporter.label, ' '.join('*.' + ext for ext in exporter.extension))

        SaveHoverState.exporter.set_choices(self, exporters)
        SaveHoverState.exporter.set_display_func(self, display_func)

    def _on_data_change(self, event=None):
        self.component_helper.set_multiple_data([self.data])
        self._sync_subsets()

    def _sync_subsets(self):

        def display_func(subset):
            if subset is None:
                return "All data (no subsets applied)"
            else:
                return subset.label

        subsets = [None] + list(self.data.subsets)

        SaveHoverState.subset.set_choices(self, subsets)
        SaveHoverState.subset.set_display_func(self, display_func)


class SaveHoverDialog(QDialog):

    def __init__(self, data_collection=None, parent=None, checked_dictionary=None):

        super(SaveHoverDialog, self).__init__(parent=parent)

        self.checked_dictionary = checked_dictionary

        self.state = SaveHoverState(data_collection=data_collection)

        self.ui = load_ui('save_hover.ui', self,
                          directory=os.path.dirname(__file__))

        self._connections = autoconnect_callbacks_to_qt(self.state, self.ui)

        self.ui.button_cancel.clicked.connect(self.reject)
        self.ui.button_ok.clicked.connect(self.accept)
        self.ui.button_select_none.clicked.connect(self.select_none)
        self.ui.button_select_all.clicked.connect(self.select_all)

        self.ui.list_component.itemChanged.connect(self._on_check_change)

        self.state.add_callback('component', self._on_data_change)

        self._on_data_change()

    def _on_data_change(self, *event):

        components = getattr(type(self.state), 'component').get_choices(self.state)
        self.ui.list_component.clear()

        for (component, k) in zip(components, np.arange(0, len(components))):

            if isinstance(component, ChoiceSeparator):
                item = QListWidgetItem(str(component))
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                item.setForeground(Qt.gray)
            else:
                item = QListWidgetItem(component.label)
                if self.checked_dictionary[self.state.data.label][k]:
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)

            self.ui.list_component.addItem(item)

    def _on_check_change(self, *event):

        current_layer = self.state.data.label
        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            if item.checkState() == Qt.Checked:
                self.checked_dictionary[current_layer][idx] = True
            else:
                self.checked_dictionary[current_layer][idx] = False

        any_checked = False

        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            if item.checkState() == Qt.Checked:
                any_checked = True
                break

        self.button_ok.setEnabled(any_checked)

    def select_none(self, *event):
        self._set_all_checked(False)

    def select_all(self, *event):
        self._set_all_checked(True)

    def _set_all_checked(self, check_state):
        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            item.setCheckState(Qt.Checked if check_state else Qt.Unchecked)

    def accept(self):
        components = []
        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            if item.checkState() == Qt.Checked:
                components.append(self.state.data.id[item.text()])

        # if self.state.subset is None:
        #     data = self.state.data
        # else:
        #     data = self.state.subset

        # return checked_dictionary
        # export_data(data, components=components, exporter=self.state.exporter.function)
        super(SaveHoverDialog, self).accept()
