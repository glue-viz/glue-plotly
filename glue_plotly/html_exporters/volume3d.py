from __future__ import absolute_import, division, print_function

import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

from qtpy import compat
from glue.config import viewer_tool
from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from plotly.offline import plot
import plotly.graph_objs as go
import glue


DEFAULT_FONT = 'Arial, sans-serif'


@viewer_tool
class Plotly3DVolumeStaticExport(Tool):

    icon = PLOTLY_LOGO
    tool_id = 'save:plotly3dvolume'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        filename, _ = compat.getsavefilename(
            parent=self.viewer, basedir="plot.html")

        # when vispy viewer is in "native aspect ratio" mode, scale axes size by data
        if self.viewer.state.native_aspect == True:
            width = self.viewer.state.x_max-self.viewer.state.x_min
            height = self.viewer.state.y_max-self.viewer.state.y_min
            depth = self.viewer.state.z_max-self.viewer.state.z_min

        # otherwise, set all axes to be equal size
        else:
            width = 1200  # this 1200 size is arbitrary, could change to any width; just need to scale rest accordingly
            height = 1200
            depth = 1200

        # set the aspect ratio of the axes, the tick label size, the axis label sizes, and the axes limits
        layout = go.Layout(
            margin=dict(r=50, l=50, b=50, t=50),
            width=1200,
            scene=dict(
                xaxis=dict(
                    title=self.viewer.state.x_att.label,
                    titlefont=dict(
                        family=DEFAULT_FONT,
                        size=20,
                        color='black'
                    ),
                    showticklabels=True,
                    tickfont=dict(
                        family=DEFAULT_FONT,
                        size=12,
                        color='black'),
                    range=[0,self.viewer.state.resolution]),
                yaxis=dict(
                    title=self.viewer.state.y_att.label,
                    titlefont=dict(
                        family=DEFAULT_FONT,
                        size=20,
                        color='black'),
                    range=[0,self.viewer.state.resolution],
                    showticklabels=True,
                    tickfont=dict(
                        family=DEFAULT_FONT,
                        size=12,
                        color='black'),
                ),
                zaxis=dict(
                    title=self.viewer.state.z_att.label,
                    titlefont=dict(
                        family=DEFAULT_FONT,
                        size=20,
                        color='black'),
                    range=[0,self.viewer.state.resolution],
                    showticklabels=True,
                    tickfont=dict(
                        family=DEFAULT_FONT,
                        size=12,
                        color='black'),
                ),
                aspectratio=dict(x=1*self.viewer.state.x_stretch, y=height/width *
                                 self.viewer.state.y_stretch, z=depth/width*self.viewer.state.z_stretch),
                aspectmode='manual',),
        )


        #set up function that returns values of cube at different pixel positions in the fixed resolution grid
        f = lambda x, y, z, datacube:  datacube[z,y,x]

        bounds = [(self.viewer.state.z_min, self.viewer.state.z_max, self.viewer.state.resolution), (self.viewer.state.y_min, self.viewer.state.y_max, self.viewer.state.resolution), (self.viewer.state.x_min, self.viewer.state.x_max, self.viewer.state.resolution)]

        #generate array of vertices at fixed resolution
        X, Y, Z = np.mgrid[0:self.viewer.state.resolution,0:self.viewer.state.resolution,0:self.viewer.state.resolution]

        data=[]
        for layer_state in self.viewer.state.layers:
        
            #check if subset object
            if isinstance(layer_state.layer,glue.core.subset_group.GroupedSubset):
                subcube=layer_state.layer.data.compute_fixed_resolution_buffer(target_data=self.viewer.state.reference_data, bounds=bounds, subset_state=layer_state.layer.subset_state)
                datacube=layer_state.layer.data.compute_fixed_resolution_buffer(target_data=self.viewer.state.reference_data, bounds=bounds,target_cid=layer_state.attribute)
                datacube=subcube*datacube
                
                for i in range(0,len(self.viewer.state.layers)):
                    if self.viewer.state.layers[i].layer is layer_state.layer.data:
                        isomin=self.viewer.state.layers[i].vmin
                        isomax=self.viewer.state.layers[i].vmax

            #otherwise a data object
            else:            
                datacube=layer_state.layer.compute_fixed_resolution_buffer(target_data=self.viewer.state.reference_data, bounds=bounds, target_cid=layer_state.attribute)
                isomin=layer_state.vmin
                isomax=layer_state.vmax
                
            #fetch values of cube at different coordinate combination
            values=f(X.flatten().astype(int),Y.flatten().astype(int),Z.flatten().astype(int),datacube.copy())
                
            voltrace=go.Volume(x=X.flatten().astype(int),y=Y.flatten().astype(int),z=Z.flatten().astype(int),value=values.flatten(),
                        flatshading=True,
                        opacity=0.2,
                        isomin=isomin,
                        showscale=False,
                        isomax=isomax,
                        colorscale=[[0, 'white'], [1., layer_state.color]],
                        opacityscale='max',
                        reversescale=False,
                        surface=dict(show=True,count=25),
                        spaceframe=dict(show=True),#,
                        #slices=dict(x=dict(show=False),y=dict(show=False),z=dict(show=False)),
                        #caps=dict(x=dict(show=True),y=dict(show=True),z=dict(show=True)),
                        contour=dict(show=False,width=4))
            data.append(voltrace)
        
        fig = go.Figure(data=data,layout=layout)
        
        plot(fig, filename=filename, auto_open=False)

        

