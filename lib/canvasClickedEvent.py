from qgis.gui import QgsMapToolEmitPoint
from ..ui.qgyf_dockwidget import QGYFDockWidget
from qgis.utils import iface

class CanvasClick(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        self.dockwidget = QGYFDockWidget()
        QgsMapToolEmitPoint.__init__(self, self.canvas)

    def canvasPressEvent( self, e ):
        lyr = iface.activeLayer()
        if lyr:
            if lyr.selectedFeatures():
                print('I am here!')
                self.canvas.selectionChanged.connect(self.dockwidget.highlightRows)
