"""
---------------------------------------------------------------------------
db_view.py
Created on: 2019-03-25 16:20:53
---------------------------------------------------------------------------
"""
import os
import sys
from qgis.utils import spatialite_connect, iface
from qgis.core import QgsProject, QgsVectorLayer, QgsDataSourceUri
from .styles import Style

class DbView:

    def init(self):
        proj = QgsProject.instance()
        path = proj.readEntry("QGYF", "dataPath")[0]
        db = proj.readEntry("QGYF", 'activeDataBase')[0]

        con = spatialite_connect("{}\{}".format(path, db))
        cur = con.cursor()

        cur.execute('DROP VIEW IF EXISTS polygon_class')
        cur.execute('DROP VIEW IF EXISTS line_class')
        cur.execute('DROP VIEW IF EXISTS point_class')

        cur.execute("""CREATE VIEW polygon_class AS
            SELECT  polygon_object.id AS id,
                class.gid AS gid,
                class.geometri_typ,
                class.grupp AS grupp,
                class.kvalitet AS kvalitet,
                class.faktor AS faktor,
                polygon_object.yta AS yta,
                polygon_object.geom AS geom
            FROM polygon_object
            JOIN classification AS class ON (polygon_object.gid = class.gid)
            WHERE class.geometri_typ = 'yta';""")

        cur.execute("""INSERT OR IGNORE INTO views_geometry_columns
            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
            VALUES ('polygon_class', 'geom', 'id', 'polygon_object', 'geom', 1);""")

        cur.execute("""CREATE VIEW line_class AS
            SELECT line_object.id AS id,
                class.gid AS gid,
                class.geometri_typ,
                class.grupp AS grupp,
                class.kvalitet AS kvalitet,
                class.faktor AS faktor,
                line_object.yta AS yta,
                line_object.geom AS geom
            FROM line_object
            JOIN classification AS class ON (line_object.gid = class.gid)
            WHERE class.geometri_typ = 'linje';""")

        cur.execute("""INSERT OR IGNORE INTO views_geometry_columns
            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
            VALUES ('line_class', 'geom', 'id', 'line_object', 'geom', 1);""")

        cur.execute("""CREATE VIEW point_class AS
            SELECT point_object.id AS id,
                class.gid AS gid,
                class.geometri_typ,
                class.grupp AS grupp,
                class.kvalitet AS kvalitet,
                class.faktor AS faktor,
                point_object.yta AS yta,
                point_object.geom AS geom
            FROM point_object
            JOIN classification AS class ON (point_object.gid = class.gid)
            WHERE class.geometri_typ = 'punkt';""")

        cur.execute("""INSERT OR IGNORE INTO views_geometry_columns
            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only)
            VALUES ('point_class', 'geom', 'id', 'point_object', 'geom', 1);""")

        con.commit()
        cur.close()
        con.close()

        root = proj.layerTreeRoot()
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
            lyr = proj.mapLayersByName(view_names[view])
            if not lyr:
                pathLayer = '{}\{}|layername={}'.format(path, db, view)
                vlayer = QgsVectorLayer(pathLayer, view_names[view], 'ogr')
                vlayer.setProviderEncoding("utf-8")
                self.style.oneColor(vlayer)
                proj.addMapLayer(vlayer, False)
                mygroup.addLayer(vlayer)
            else:
                lyr[0].triggerRepaint()