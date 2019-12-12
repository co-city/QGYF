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
from ..ui.export import ExportDialog
from PyQt5.QtWidgets import QMessageBox

class GroundAreas:

    def initAP(self):

        con = spatialite_connect("{}\{}".format(QSettings().value('dataPath'), QSettings().value('activeDataBase')))
        cur = con.cursor()

        tables = ['polygon_object', 'line_object', 'point_object']
        count = 0
        total_area = 0
        line_heights = []
        points_x = 0
        for table in tables:
            cur.execute("SELECT COUNT(*) FROM " + table)
            c = cur.fetchone()[0]
            count += c
            if c != 0:
                cur.execute("SELECT SUM(yta) FROM " + table)
                total_area += int(cur.fetchone()[0])

                if table == 'line_object':
                    cur.execute("SELECT AREA(ST_Buffer(geom, 0.5)), yta/AREA(ST_Buffer(geom, 0.5)), gid FROM " + table)
                    line_heights = [[j[0], round(j[1], 0), j[2]] for j in cur.fetchall() if round(j[1], 0) != 1]

            if table == 'point_object':
                cur.execute("SELECT SUM(X(geom)) FROM " + table)
                result = cur.fetchone()
                if result and result[0]:
                    points_x += result[0]

        if count != QSettings().value('objectCount') or total_area != QSettings().value('groundArea') or points_x != QSettings().value('pointsCoord'):

            cur.execute("""SELECT gid FROM polygon_object WHERE ST_IsValid(geom) != 1""")
            failed = cur.fetchall()
            if failed:
                QMessageBox.warning(ExportDialog(), 'Fel geometri', 'Din polygon data verkar innehålla objekt med fel geometri (dvs. a bow-tie polygon). Det ska försöka behandlas automatiskt.\nOm det inte går ska lager med grundytor inte byggas upp. I detta fall måste problemet åtgärdas manuellt.\n\nGlobala ID för felobjekt:\n' + str(failed))
                cur.execute("""UPDATE polygon_object SET geom = ST_MakeValid(geom) WHERE ST_IsValid(geom) != 1""")

            cur.execute("DELETE FROM ground_areas")
            # Merge all objects together
            cur.execute("""INSERT INTO ground_areas (id, faktor, yta, poang, geom)
                SELECT NULL, 1, AREA(st_unaryunion(st_collect(geom))), AREA(st_unaryunion(st_collect(geom))), 
                CastToMultiPolygon(st_unaryunion(st_collect(geom))) FROM
                (SELECT NULL, geom FROM polygon_object
                UNION ALL
                SELECT NULL, CastToPolygon(ST_Buffer(geom, 0.5)) FROM line_object
                UNION ALL
                SELECT NULL, CastToPolygon(ST_Buffer(geom, POWER(yta/3.14159, 0.5))) FROM point_object);""") # GROUP BY ytklass

            QSettings().setValue('objectCount', count)
            QSettings().setValue('groundArea', total_area)
            QSettings().setValue('pointsCoord', points_x)

            if line_heights:
                minus_area = sum(j[0] for j in line_heights)
                plus_area = sum(j[0]*j[1] for j in line_heights)
                cur.execute("SELECT yta from ground_areas;")
                area = cur.fetchone()[0]
                area = area - minus_area + plus_area
                cur.execute("UPDATE ground_areas SET yta = (?);", [area])

        con.commit()
        cur.close()
        con.close()

    def mergeGA(self, cur):
        cur.execute("DELETE FROM ground_areas")
        cur.execute('''INSERT INTO ground_areas (id, ytgrupp, ytklass, faktor, yta, poang, geom)
            SELECT  NULL, ytgrupp, ytklass, faktor, SUM(yta), SUM(poang), 
            CastToMultiPolygon(ST_Union(geom)) AS geom FROM ga_template 
            GROUP BY ytklass''')
        cur.execute('''SELECT RecoverGeometryColumn('ground_areas', 'geom',  ''' + str(QSettings().value('CRS')) + ''', 'MULTIPOLYGON', 'XY')''')
        cur.execute("DELETE FROM ga_template")
        cur.execute('''INSERT INTO ga_template SELECT * FROM ground_areas''')


    def showGA(self):
        self.style = Style()
        root = QgsProject.instance().layerTreeRoot()
        lyr = QgsProject.instance().mapLayersByName('Grundytor')
        if not lyr:
            pathLayer = '{}\{}|layername={}'.format(QSettings().value('dataPath'), QSettings().value('activeDataBase'), 'ground_areas')
            vlayer = QgsVectorLayer(pathLayer, 'Grundytor', 'ogr')
            self.style.styleGroundAreas(vlayer)
            QgsProject.instance().addMapLayer(vlayer, False)
            root.insertLayer(3, vlayer)
        else:
            lyr[0].triggerRepaint()