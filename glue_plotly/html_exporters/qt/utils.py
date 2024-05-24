from echo.qt import connect_checkable_button, connect_float_text

from glue.core import Subset

from qtpy.QtWidgets import QCheckBox, QHBoxLayout, QLabel, QLineEdit
from qtpy.QtGui import QIntValidator, QDoubleValidator


def display_name(prop_name):
    return prop_name.replace("_", " ").capitalize()


def layer_label(layer):
    label = layer.layer.label
    if isinstance(layer.layer, Subset):
        label += f" ({layer.layer.data.label})"
    return label


def clear_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                clear_layout(item.layout())


def widgets_for_property(instance, property, display_name=None):
    value = getattr(instance, property)
    t = type(value)
    connections = []
    widgets = []
    display_name = display_name or property
    if t is bool:
        widget = QCheckBox()
        widget.setChecked(value)
        widget.setText(display_name)
        connections.append(connect_checkable_button(instance, property, widget))
        widgets.append(widget)
    elif t in [int, float]:
        label = QLabel()
        prompt = f"{display_name}:"
        label.setText(prompt)
        widget = QLineEdit()
        validator = QIntValidator() if t is int else QDoubleValidator()
        widget.setText(str(value))
        widget.setValidator(validator)
        connections.append(connect_float_text(instance, property, widget))
        widgets.extend((label, widget))

    return connections, widgets


def widgets_for_state(state):
    connections = []
    widgets = []
    if state is not None:
        for property in state.callback_properties():
            conns, wdgts = widgets_for_property(state, property, display_name(property))
            connections.extend(conns)
            widgets.extend(wdgts)

    return connections, widgets


def update_layout_for_state(layout, state):
    clear_layout(layout)
    connections, widgets = widgets_for_state(state)
    for widget in widgets:
        row = QHBoxLayout()
        row.addWidget(widget)
        layout.addRow(row)

    return connections
