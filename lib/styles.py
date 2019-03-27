"""
---------------------------------------------------------------------------
styles.py
Created on: 2019-03-27 16:20:53
---------------------------------------------------------------------------
"""
import os
import sys
from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol

class Style:
    
    def init(self):
        l = QgsProject.instance().mapLayersByName('polygon_object')
        if l:
            l = l[0]
            r = l.renderer()
            mySymbol1 = QgsFillSymbol.createSimple({
                'color':'255,0,0,50',
                'color_border':'#289e26',
                'width_border':'0.5'})
            r.setSymbol(mySymbol1)
            l.triggerRepaint()