"""
---------------------------------------------------------------------------
green_areas.py
Created on: 2019-04-16 16:20:53
---------------------------------------------------------------------------
"""
import os
import sys
from PyQt5.QtCore import QSettings
from qgis.utils import spatialite_connect, iface
from qgis.core import QgsProject, QgsVectorLayer
from .styles import Style
import processing

class GreenAreas:

    def init(self, path):

        con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))
        cur = con.cursor()

        

        
        con.commit()
        cur.close()
        con.close()

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup('Kvaliteter')
        if not mygroup:
            mygroup = root.insertGroup(1, 'Kvaliteter')

        self.style = Style()
        self.style.visibility('Klassificering', False)

        views = ['point_class', 'line_class', 'polygon_class']
        view_names =	{
		  'point_class': 'Punktkvalitet',
		  'line_class': 'Linjekvalitet',
		  'polygon_class': 'Ytkvalitet'
		}

        for view in views:
            lyr = QgsProject.instance().mapLayersByName(view_names[view])
            if not lyr:
                pathLayer = '{}\{}|layername={}'.format(path, QSettings().value('activeDataBase'), view)
                vlayer = QgsVectorLayer(pathLayer, view_names[view], 'ogr')
                vlayer.setProviderEncoding("utf-8")
                self.style.oneColor(vlayer)
                QgsProject.instance().addMapLayer(vlayer, False)
                mygroup.addLayer(vlayer)