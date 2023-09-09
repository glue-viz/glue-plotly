from math import floor

from glue.config import viewer_tool
from glue.core import BaseData
from glue_qt.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from qtpy import compat
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QDialog
from plotly.offline import plot
import plotly.graph_objs as go
from pandas import DataFrame

from ...sort_components import SortComponentsDialog

try:
    import dask.array as da
    DASK_INSTALLED = True
except ImportError:
    DASK_INSTALLED = False


@viewer_tool
class PlotlyTableExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlytable'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    # We use this instead of self.viewer.model.data_for_row_and_column
    # because we need the value (for sorting), and that method returns a string
    def _data_for_cell(self, row, column):
        model = self.viewer.model
        c = model.columns[column]
        idx = model.order_visible[row]
        comp = model._data[c]
        value = comp[idx]
        if isinstance(value, bytes):
            return value.decode('ascii')
        else:
            if DASK_INSTALLED and isinstance(value, da.Array):
                return value.compute()
            else:
                return comp[idx]

    def activate(self):

        model = self.viewer.model

        components = model.columns
        column_names = [c.label for c in model.columns]
        dialog = SortComponentsDialog(components=components)
        result = dialog.exec_()
        if result == QDialog.Rejected:
            return

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")
        if not filename:
            return

        sort_components = dialog.sort_components
        header = dict(values=column_names)
        n_rows = model.rowCount()
        n_cols = model.columnCount()

        data = [[self._data_for_cell(row, col) for row in range(n_rows)] for col in range(n_cols)]

        # Keep as strings for formatting consistency with table viewer
        cells = [[str(x) for x in col] for col in data]

        # Each row has a color, so we only need to get the data color for the first cell
        white = (256, 256, 256, 256)
        colors = []
        for row in range(n_rows):
            brush = model.data_by_row_and_column(row, 0, Qt.BackgroundRole)
            color = white if brush is None else brush.color().getRgb()
            color = tuple(color[:3] + (color[3]/256,))
            colors.append('rgba{0}'.format(color))

        table = go.Table(header=header, cells=dict(values=cells, fill_color=[colors]))
        fig = go.Figure(data=table)

        dx, dy = 0.2, 0.03
        x0 = 0.1 if len(sort_components) > 0 else 0
        y0 = 1.1
        layers = [layer for layer in self.viewer.layers if layer.state.visible and
                  not isinstance(layer.layer, BaseData)]
        for i, layer in enumerate(layers):
            layer_color = layer.layer.style.color
            color = 'gray' if layer_color == '0.35' else layer_color
            label = layer.layer.label + " ({0})".format(layer.layer.data.label)

            x = x0 + dx * floor(i / 3)
            y = y0 - dy * (i % 3)
            fig.add_annotation(dict(text=label,
                                    font=dict(color=color, size=14),
                                    xanchor="left",
                                    yanchor="top",
                                    showarrow=False,
                                    x=x, y=y))

        if len(sort_components) > 0:
            buttons = [dict(
                label="None",
                method="restyle",
                args=[dict(cells=dict(values=cells, fill=dict(color=[colors])))]
            )]
            df = DataFrame({c: data[i] for i, c in enumerate(column_names)})
            for col in sort_components:
                scores = df.sort_values(by=[col])
                sort_colors = [colors[i] for i in scores.index]
                button = dict(
                    label=col,
                    method="restyle",
                    args=[
                        dict(
                            cells=dict(
                                values=[[str(x) for x in scores[c].values] for c in column_names],
                                fill=dict(color=[sort_colors])
                            )
                        )
                    ],
                )
                buttons.append(button)

            fig.update_layout(
                updatemenus=[
                    dict(
                        buttons=buttons,
                        direction='down',
                        showactive=True,
                        x=0,
                        xanchor="left",
                        y=1.1,
                        yanchor="top"
                    )
                ])

        plot(fig, filename=filename, auto_open=False)
