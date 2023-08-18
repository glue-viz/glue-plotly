import os

from qtpy.QtWidgets import QDialog, QListWidgetItem
from qtpy.QtCore import Qt

from echo import ChoiceSeparator, SelectionCallbackProperty
from echo.qt import autoconnect_callbacks_to_qt

from glue.core.state_objects import State
from glue.core.data_combo_helper import ComboHelper
from glue_qt.utils import load_ui

import numpy as np


__all__ = ['SortComponentsDialog']


class SortComponentsState(State):

    component = SelectionCallbackProperty()

    def __init__(self, components=component):

        super(SortComponentsState, self).__init__()

        self.component_helper = ComboHelper(self, 'component')
        self.component_helper.choices = components


class SortComponentsDialog(QDialog):

    def __init__(self, components=None, parent=None):

        super(SortComponentsDialog, self).__init__(parent=parent)

        self.ui = load_ui('sort_components.ui', self,
                          directory=os.path.dirname(__file__))

        self.state = SortComponentsState(components=components)

        self._connections = autoconnect_callbacks_to_qt(self, self.ui)
        self.sort_components = []

        self.ui.button_cancel.clicked.connect(self.reject)
        self.ui.button_ok.clicked.connect(self.accept)
        self.ui.button_select_none.clicked.connect(self.select_none)
        self.ui.button_select_all.clicked.connect(self.select_all)

        self.ui.list_component.itemChanged.connect(self._on_check_change)

        self._populate_list()

    def _populate_list(self):

        components = getattr(type(self.state), 'component').get_choices(self.state)
        self.ui.list_component.clear()

        for (component, k) in zip(components, np.arange(0, len(components))):

            if isinstance(component, ChoiceSeparator):
                item = QListWidgetItem(str(component))
                item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
                item.setForeground(Qt.gray)
            else:
                item = QListWidgetItem(component.label)

            item.setCheckState(Qt.Unchecked)
            self.ui.list_component.addItem(item)

    def _on_check_change(self, *event):

        self.sort_components = []
        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            if item.checkState() == Qt.Checked:
                self.sort_components.append(item.text())

    def select_none(self, *event):
        self._set_all_checked(False)

    def select_all(self, *event):
        self._set_all_checked(True)

    def _set_all_checked(self, check_state):
        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            item.setCheckState(Qt.Checked if check_state else Qt.Unchecked)

    def accept(self):
        self.sort_components = []
        for idx in range(self.ui.list_component.count()):
            item = self.ui.list_component.item(idx)
            if item.checkState() == Qt.Checked:
                self.sort_components.append(item.text())
        super(SortComponentsDialog, self).accept()
