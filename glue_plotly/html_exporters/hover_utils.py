from glue.core import Data, DataCollection
from numpy import ones


def hover_dummy_data(data_or_subset):
    components = {}
    for component in data_or_subset.components:
        components[component.label] = ones(10)

    dummy_data = Data(**components, label=data_or_subset.label)

    seen = set()
    for component in dummy_data.components:
        if component.label in seen:
            dummy_data.remove_component(component)
        else:
            seen.add(component.label)
    return dummy_data


def hover_data_collection_for_viewer(viewer,
                                     layer_condition=None):
    if layer_condition is None:
        layer_condition = lambda layer: layer.enabled and layer.state.visible

    return DataCollection([hover_dummy_data(layer.layer) for layer in viewer.layers if layer_condition(layer)])
