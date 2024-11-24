<template>
  <v-dialog
    v-model="dialog_open"
    width="600px"
  >
    <v-card class="pa-3">
      <v-card-title>
        Save Hover
      </v-card-title>

      <p>Choose the layer you want to add hover info to:</p>
      <v-select
        v-model="data_selected"
        :items="data_items"
      >
      </v-select>

      <p>Choose component of the layer you want to appear in hover over:</p>
      <v-list>
        <v-list-item-group
          v-model="component_selected"
          multiple
        >
          <v-list-item
            v-for="(component, index) in component_items"
            :key="index"
            :value="index"
          >
            {{ component.text }}
          </v-list-item>
        </v-list-item-group>
      </v-list>
      <v-row>
        <v-btn @click="select_none">
          Select None
        </v-btn>
        <v-spacer></v-spacer>
        <v-btn @click="select_all">
          Select All
        </v-btn>
      </v-row>
      <p>Once you click on "Export" you will be prompted to choose the filename.
      <v-row>
        <v-spacer></v-spacer>
        <v-btn @click="cancel_dialog">Cancel</v-btn>
        <v-btn @click="export_viewer">Export</v-btn>
      </v-row>
      
    </v-card>
  <v-dialog>
</template>
