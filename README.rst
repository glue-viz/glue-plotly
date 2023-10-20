|Actions Status| |Coverage Status|

Experimental plot.ly plugin for glue
------------------------------------

This package is a plugin for `glue <https://glueviz.org/>`_ that allows functionality linking glue
to `Plotly <https://plotly.com/>`_. This includes three main pieces of functionality:

- Export glue views to standalone HTML pages
- Export glue views to Plotly's `Chart Studio <https://chart-studio.plotly.com/feed/#/>`_
- Experimental glue viewers powered by Plotly


============
Installation
============

glue-plotly can be installed using pip::

    pip install glue-plotly

Additionally, glue-plotly is included in the glue `standalone applications <https://glueviz.org/install.html>_`
for MacOS and Windows.


==============
HTML Exporters
==============

The HTML exporters are exposed as viewer tools in both `glue-qt <https://github.com/glue-viz/glue-qt>`_
and `glue-jupyter <https://github.com/glue-viz/glue-jupyter>`_

For glue-qt, all of the built-in matplotlib viewers are supported, along with the dendrogram viewer 
and the 3D scatter viewer from the `glue-vispy-viewers <https://github.com/glue-viz/glue-vispy-viewers>`_ plugin.
For glue-jupyter, the bqplot scatter, image, profile, and histogram viewers are supported. In glue-qt,
these tools are subtools of the "save" meta-tool and can be accessed from its dropdown menu.

|Qt toolbar demo|

In glue-jupyter, the Plotly exporter tools are top-level toolbar tools (look for the Plotly logo!)

|bqplot toolbar|

============
Chart Studio
============

The Chart Studio exporter allows exporting a Qt glue session to Chart Studio, provided that all of the
viewers in the session are supported. Currently supported viewers are the matplotlib scatter, histogram,
and profile viewers.

To access the exporter inside Qt glue, navigate to File > Advanced Exporters > Plotly.

|Chart Studio demo|


========
Viewers
========

This package contains two experimental Plotly-powered viewers which can be used with glue-jupyter - a
scatter viewer and a histogram viewer. More viewers to come in the future!

`This notebook <https://github.com/glue-viz/glue-plotly/blob/main/doc/PlotlyViewerExample.ipynb>`_ demonstrates
basic usage of the these viewers, such as importing and viewer creation.


=================
Package Structure
=================

- ``common`` contains methods for creating Plotly `graph objects <https://plotly.com/python/graph-objects/>`_ traces to represent glue layers and viewers that are shared between the exporters and Plotly viewers.
- ``html_exporters`` contains the implementations of the HTML exporter tools for glue-qt and glue-jupyter
- ``web`` contains the implementation of the Chart Studio exporter for Qt glue
- ``viewers`` contains the implementations of the Plotly viewers


.. |Actions Status| image:: https://github.com/glue-viz/glue-plotly/workflows/ci_workflows.yml/badge.svg
    :target: https://github.com/glue-viz/glue-plotly/actions
    :alt: Glue-plotly's GitHub Actions CI Status
.. |Coverage Status| image:: https://codecov.io/gh/glue-viz/glue-plotly/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/glue-viz/glue-plotly
    :alt: Glue-plotly's Coverage Status
.. |Qt toolbar demo| image:: https://raw.githubusercontent.com/glue-viz/glue-plotly/main/doc/QtToolbarExport.gif
    :alt: Qt Plotly export demo
.. |bqplot toolbar| image:: https://raw.githubusercontent.com/glue-viz/glue-plotly/main/doc/BqplotToolbarHighlighted.png
    :alt: bqplot Plotly export tool
.. |Chart Studio demo| image:: https://raw.githubusercontent.com/glue-viz/glue-plotly/main/doc/QtChartStudioExport.gif
    :alt: Qt Chart Studio export demo
