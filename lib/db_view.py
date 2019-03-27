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

        cur.execute('DROP VIEW IF EXISTS ytor_klassade')
        
        cur.execute("CREATE VIEW ytor_klassade AS \
            SELECT class.id AS id, \
                class.id_ini AS id_new, \
                class.geometri_typ, \
                class.grupp AS grupp, \
                class.kvalitet AS kvalitet, \
                polygon_object.id AS id_ini, \
                polygon_object.geom AS geom \
            FROM polygon_object \
            JOIN classification AS class ON (polygon_object.id = class.id_ini) \
            WHERE class.geometri_typ = 'yta';")

        cur.execute("INSERT INTO views_geometry_columns  \
            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) \
            VALUES ('ytor_klassade', 'geom', 'id', 'polygon_object', 'geom', 1);")
        cur.execute("SELECT * FROM ytor_klassade;")
        ##cur.execute("SELECT RecoverGeometryColumn('ytor_klassade','geom',3006,'POLYGON',2);")
        cur.execute("SELECT RecoverSpatialIndex('ytor_klassade','geom');")
        cur.execute("SELECT UpdateLayerStatistics('ytor_klassade');")
        cur.execute("SELECT * FROM ytor_klassade;")
        
        cur.close()
        con.close()

        views = ['ytor_klassade'] #'polygon_object'
        uri = QgsDataSourceUri()
        uri.setDatabase(path + r'\qgyf.sqlite')
        schema = ''
        geom_column = '' #geom
        for view in views:
            uri.setDataSource(schema, view, geom_column)
            iface.addVectorLayer(uri.uri(), view, 'spatialite')
            self.style = Style()
        
        self.style.init()
            
        

