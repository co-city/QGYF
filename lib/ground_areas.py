"""
---------------------------------------------------------------------------
ground_areas.py
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

class GroundAreas:

    def init(self, path):

        con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))
        cur = con.cursor()

        tables = ['polygon_object', 'line_object', 'point_object']
        count = 0
        for table in tables:
            cur.execute("SELECT COUNT(*) FROM " + table)
            count += cur.fetchone()[0]
        
        if count != QSettings().value('objectCount'):

            cur.execute("DELETE FROM ground_areas")
            # Merge all objects together
            cur.execute("""INSERT INTO ground_areas (id, yta, geom) 
                SELECT NULL, AREA(st_unaryunion(st_collect(geom))), st_unaryunion(st_collect(geom)) as geom FROM 
                (SELECT NULL, geom FROM polygon_object 
                UNION ALL 
                SELECT NULL, CastToPolygon(ST_Buffer(geom, 0.5)) FROM line_object
                UNION ALL 
                SELECT NULL, CastToPolygon(ST_Buffer(geom, 3)) FROM point_object);""") # GROUP BY ytklass

            QSettings().setValue('objectCount', count)

        con.commit()
        cur.close()
        con.close()

        self.style = Style()
        root = QgsProject.instance().layerTreeRoot()
        lyr = QgsProject.instance().mapLayersByName('Grundytor')
        if not lyr:
            pathLayer = '{}\{}|layername={}'.format(path, QSettings().value('activeDataBase'), 'ground_areas')
            vlayer = QgsVectorLayer(pathLayer, 'Grundytor', 'ogr')
            self.style.styleGroundAreas(vlayer)
            QgsProject.instance().addMapLayer(vlayer, False)
            root.insertLayer(3, vlayer)