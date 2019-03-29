"""
---------------------------------------------------------------------------
db_view.py
Created on: 2019-03-25 16:20:53
---------------------------------------------------------------------------
"""
import os
import sys
sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis\python')
from qgis.utils import spatialite_connect, iface
from qgis.core import QgsProject, QgsVectorLayer, QgsDataSourceUri
from .styles import Style

class DbView:

    def init(self, path):
        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()

        cur.execute('DROP VIEW IF EXISTS polygon_class')
        cur.execute('DROP VIEW IF EXISTS line_class')
        cur.execute('DROP VIEW IF EXISTS point_class')

        cur.execute("""CREATE VIEW polygon_class AS
            SELECT class.id AS id,
                class.id_ini AS id_new,
                class.geometri_typ,
                class.grupp AS grupp,
                class.kvalitet AS kvalitet,
                class.faktor AS faktor,
                polygon_object.id AS id_ini,
                polygon_object.geom AS geom
            FROM polygon_object
            JOIN classification AS class ON (polygon_object.id = class.id_ini)
            WHERE class.geometri_typ = 'yta';""")

        cur.execute("""INSERT OR IGNORE INTO views_geometry_columns
            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
            VALUES ('polygon_class', 'geom', 'id', 'polygon_object', 'geom', 1);""")

        cur.execute("""CREATE VIEW line_class AS
            SELECT class.id AS id,
                class.id_ini AS id_new,
                class.geometri_typ,
                class.grupp AS grupp,
                class.kvalitet AS kvalitet,
                class.faktor AS faktor,
                line_object.id AS id_ini,
                line_object.geom AS geom
            FROM line_object
            JOIN classification AS class ON (line_object.id = class.id_ini)
            WHERE class.geometri_typ = 'linje';""")

        cur.execute("""INSERT OR IGNORE INTO views_geometry_columns
            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
            VALUES ('line_class', 'geom', 'id', 'line_object', 'geom', 1);""")

        cur.execute("""CREATE VIEW point_class AS
            SELECT class.id AS id,
                class.id_ini AS id_new,
                class.geometri_typ,
                class.grupp AS grupp,
                class.kvalitet AS kvalitet,
                class.faktor AS faktor,
                point_object.id AS id_ini,
                point_object.geom AS geom
            FROM point_object
            JOIN classification AS class ON (point_object.id = class.id_ini)
            WHERE class.geometri_typ = 'punkt';""")

        cur.execute("""INSERT OR IGNORE INTO views_geometry_columns
            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
            VALUES ('point_class', 'geom', 'id', 'point_object', 'geom', 1);""")

        con.commit()
        cur.close()
        con.close()

        root = QgsProject.instance().layerTreeRoot()
        mygroup = root.findGroup('Object_classified')
        if not mygroup:
            mygroup = root.insertGroup(0, 'Object_classified')

        # Set layers to invisible
        lyr = ['point_object', 'line_object', 'polygon_object']
        for l in lyr:
            layer = QgsProject.instance().mapLayersByName(l)[0]
            exists = len(layer) > 0
            if exists:
                root.findLayer(layer.id()).setItemVisibilityChecked(False)
        #iface.mapCanvas().refresh()

        views = ['point_class', 'line_class', 'polygon_class']
        for view in views:
            lyr = QgsProject.instance().mapLayersByName(view)
            if not lyr:
                pathLayer = path + r"\qgyf.sqlite|layername=" + view
                vlayer = QgsVectorLayer(pathLayer, view, 'ogr')
                vlayer.setProviderEncoding("utf-8")
                QgsProject.instance().addMapLayer(vlayer, False)
                mygroup.addLayer(vlayer)

        self.style = Style()
        self.style.oneColor()