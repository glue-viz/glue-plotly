from ipyvuetify.VuetifyTemplate import VuetifyTemplate
from traitlets import Bool, Int, List, observe

from glue_jupyter.vuetify_helpers import link_glue_choices

from ..base_save_hover import BaseSaveHoverDialog


class JupyterSaveHoverDialog(BaseSaveHoverDialog, VuetifyTemplate):

    template_file = (__file__, "save_hover.vue")
    dialog_open = Bool().tag(sync=True)

    data_items = List().tag(sync=True)
    data_selected = Int().tag(sync=True)

    component_items = List().tag(sync=True)
    component_selected = List().tag(sync=True)

    def __init__(self,
                 data_collection=None,
                 checked_dictionary=None,
                 on_cancel=None,
                 on_export=None):

        BaseSaveHoverDialog.__init__(self, data_collection=data_collection, checked_dictionary=checked_dictionary)
        VuetifyTemplate.__init__(self)

        self.on_cancel = on_cancel
        self.on_export = on_export

        link_glue_choices(self, self.state, 'data')

        self._on_data_change()

    def _on_data_change(self, *args):
        super()._on_data_change(*args)
        data_components = self.state.data.main_components
        self.component_items = [
            {"text": component.label, "value": index}
            for index, component in enumerate(data_components)
        ]
        current_selections = self.checked_dictionary[self.state.data.label]
        self.component_selected = [i for i in range(len(data_components)) if current_selections[i]]

    @observe('component_selected')
    def _on_component_selected_changed(self, change):
        selections = change["new"]
        current_layer = self.state.data.label
        self.checked_dictionary[current_layer] = [i in selections for i in range(len(self.state.data.main_components))]

    def vue_select_none(self, *args):
        self.component_selected = []

    def vue_select_all(self, *args):
        self.component_selected = list(range(len(self.component_items)))

    def vue_cancel_dialog(self, *args):
        # self.checked_dictionary = {}
        self.dialog_open = False
        if self.on_cancel is not None:
            self.on_cancel()

    def vue_export_viewer(self, *args):
        self.dialog_open = False
        if self.on_export is not None:
            self.on_export()
