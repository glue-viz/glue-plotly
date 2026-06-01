<template>
    <div class="glue-plotly-layer-scatter">
        <div class="text-subtitle-2 font-weight-bold">Color</div>
        <div>
            <v-select label="color" :items="cmap_mode_items" v-model="cmap_mode_selected" hide-details />
        </div>
        <template v-if="(cmap_mode_items[cmap_mode_selected] || {}).text === 'Linear'">
            <div>
                <v-select label="attribute" :items="cmap_att_items" v-model="cmap_att_selected" hide-details />
            </div>
            <div>
                <glue-float-field label="min" :value.sync="cmap_vmin" echo-type="float" />
            </div>
            <div>
                <glue-float-field label="max" :value.sync="cmap_vmax" echo-type="float" />
            </div>
            <div>
                <v-select label="colormap" :items="cmap_items" v-model="cmap" hide-details/>
            </div>
        </template>
        <div>
            <v-subheader class="pl-0 slider-label">opacity</v-subheader>
            <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="alpha" echo-type="float" hide-details />
        </div>
        <div class="text-subtitle-2 font-weight-bold">Points</div>
        <div>
            <v-subheader class="pl-0 slider-label">show points</v-subheader>
            <v-switch v-model="markers_visible" hide-details style="margin-top: 0" />
        </div>
        <template v-if="markers_visible">
            <div>
                <v-select label="type" :items="points_mode_items" v-model="points_mode_selected" hide-details />
            </div>
            <div v-if="density_map === false">
                <v-select label="size" :items="size_mode_items" v-model="size_mode_selected" hide-details />
            </div>
            <template v-if="(size_mode_items[size_mode_selected] || {}).text === 'Linear'">
                <div>
                    <v-select label="attribute" :items="size_att_items" v-model="size_att_selected" hide-details />
                </div>
                <div>
                    <glue-float-field label="min" :value.sync="size_vmin" echo-type="float" />
                </div>
                <div>
                    <glue-float-field label="max" :value.sync="size_vmax" echo-type="float" />
                </div>
            </template>
            <template v-if="density_map">
                <div>
                    <v-subheader class="pl-0 slider-label">dpi</v-subheader>
                    <glue-throttled-slider wait="300" min="12" max="144" step="1" :value.sync="dpi" echo-type="float" hide-details />
                </div>
                <div>
                    <v-subheader class="pl-0 slider-label">contrast</v-subheader>
                    <glue-throttled-slider wait="300" min="0" max="1" step="0.01" :value.sync="density_contrast" echo-type="float" hide-details />
                </div>
            </template>
            <template v-else>
               <div>
                    <v-subheader class="pl-0 slider-label">size scaling</v-subheader>
                    <glue-throttled-slider wait="300" min="0.1" max="10" step="0.01" :value.sync="size_scaling" echo-type="float" hide-details />
                </div>
                <div>
                      <v-subheader class="pl-0 slider-label">fill markers</v-subheader>
                      <v-switch v-model="fill" hide-details style="margin-top: 0" />
                </div>
                <div>
                      <v-subheader class="pl-0 slider-label">show borders</v-subheader>
                      <v-switch v-model="border_visible" hide-details style="margin-top: 0" />
                </div>
                <div>
                    <v-subheader class="pl-0 slider-label">border size</v-subheader>
                    <glue-throttled-slider wait="300" min="0" max="10" step="1" :value.sync="border_size" echo-type="float" hide-details />
                </div>
                <div>
                    <v-subheader class="pl-0 slider-label">match border color to layer</v-subheader>
                      <v-switch v-model="border_color_match_layer" hide-details style="margin-top: 0" />
                </div>
                <div>
                    <v-subheader class="pl-0 slider-label">border color</v-subheader>
                    <v-menu ref="menu" :disabled="border_color_match_layer">
                        <template v-slot:activator="{ on, props }">
                            <span class="glue-color-menu"
                                  :style="`background: ${border_color_match_layer ? 'gray' : border_color}`"
                                  @click.stop="on.click"
                            >&nbsp;</span>
                        </template>
                        <div @click.stop="" style="text-align: end; background-color: white">
                            <v-btn icon @click="$refs.menu.save()">
                                <v-icon>mdi-close</v-icon>
                            </v-btn>
                            <v-color-picker v-model="border_color" echo-type="text" ></v-color-picker>
                        </div>
                    </v-menu>
                </div>
            </template>
        </template>
        <div class="text-subtitle-2 font-weight-bold" :style="markers_visible ? {} : {marginTop: '6px'}">Line</div>
        <div>
            <v-subheader class="pl-0 slider-label">show line</v-subheader>
            <v-switch v-model="line_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="line_visible">
            <div>
                <v-subheader class="pl-0 slider-label">width</v-subheader>
                <glue-throttled-slider wait="300" min="1" max="20" step="1" :value.sync="linewidth" echo-type="float" hide-details />
            </div>
            <div>
                <v-select label="linestyle" :items="linestyle_items" v-model="linestyle_selected" hide-details />
            </div>
        </template>
        <div class="text-subtitle-2 font-weight-bold" :style="markers_visible ? {} : {marginTop: '6px'}">Vectors</div>
        <div>
            <v-subheader class="pl-0 slider-label">show vectors</v-subheader>
            <v-switch v-model="vector_visible" hide-details style="margin-top: 0"/>
        </div>
        <template v-if="vector_visible">
            <div>
                <v-select label="vx" :items="vx_att_items" v-model="vx_att_selected" hide-details />
            </div>
            <div>
                <v-select label="vy" :items="vy_att_items" v-model="vy_att_selected" hide-details />
            </div>
        </template>
    </div>
</template>
<script>
</script>
<style id="layer_scatter">
.glue-plotly-layer-scatter .v-subheader.slider-label {
    font-size: 12px;
    height: 16px;
    margin-top: 6px;
}
</style>
