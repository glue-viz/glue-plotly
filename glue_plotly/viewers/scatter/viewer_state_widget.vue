<template>
    <div class="glue-viewer-scatter-plotly">
        <div>
            <v-select label="x axis" :items="x_att_items" v-model="x_att_selected" hide-details />
        </div>
        <div>
            <v-select label="y axis" :items="y_att_items" v-model="y_att_selected" hide-details />
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">x log</v-subheader>
            <v-switch v-model="glue_state.x_log" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">y log</v-subheader>
            <v-switch v-model="glue_state.y_log" hide-details style="margin-top: 0"/>
        </div>
        <div>
            <v-subheader class="pl-0 slider-label">show axes</v-subheader>
            <v-switch v-model="glue_state.show_axes" hide-details style="margin-top: 0"/>
        </div>
    </div>
</template>

<style id="viewer_scatter">
.glue-viewer-scatter-plotly .v-subheader.slider-label {
    font-size: 12px;
    height: 16px;
    margin-top: 6px;
}
</style>
