from echo import SelectionCallbackProperty
from glue import config
from glue.core.data_combo_helper import ComponentIDComboHelper, DataCollectionComboHelper
from glue.core.state_objects import State


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


class BaseSaveHoverDialog:

    def __init__(self, data_collection=None, checked_dictionary=None):
        
        self.checked_dictionary = checked_dictionary
        self.state = SaveHoverState(data_collection=data_collection)

        self.state.add_callback('component', self._on_component_change)
        self.state.add_callback('data', self._on_data_change)

    def _on_component_change(self, *args):
        pass

    def _on_data_change(self, *args):
        pass
