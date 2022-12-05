from glue.config import viewer_tool

try:
    from glue.viewers.common.qt.tool import Tool
except ImportError:
    from glue.viewers.common.tool import Tool

from glue_plotly import PLOTLY_LOGO

from qtpy import compat
from qtpy.QtCore import Qt
from plotly.offline import plot
import plotly.graph_objs as go


@viewer_tool
class PlotlyTableExport(Tool):
    icon = PLOTLY_LOGO
    tool_id = 'save:plotlytable'
    action_text = 'Save Plotly HTML page'
    tool_tip = 'Save Plotly HTML page'

    def activate(self):

        filename, _ = compat.getsavefilename(parent=self.viewer, basedir="plot.html")

        model = self.viewer.model

        header = dict(values=[c.label for c in model.columns])
        n_rows = model.rowCount()
        n_cols = model.columnCount()

        data = [[model.data_by_row_and_column(row, col, Qt.DisplayRole) for row in range(n_rows)] for col in range(n_cols)]

        # Each row has a color, so we only need to get the data color for the first cell
        white = (256, 256, 256, 256)
        colors = []
        for row in range(n_rows):
            brush = model.data_by_row_and_column(row, 0, Qt.BackgroundRole)
            color = white if brush is None else brush.color().getRgb()
            color = tuple(color[:3] + (color[3]/256,))
            colors.append('rgba{0}'.format(color))

        table = go.Table(header=header, cells=dict(values=data, fill_color=[colors]))
        fig = go.Figure(table)

        plot(fig, filename=filename, auto_open=False)
