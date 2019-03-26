"""
---------------------------------------------------------------------------
db_view.py
Created on: 2019-03-25 16:20:53
---------------------------------------------------------------------------
"""
import os
import sys
sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis\python')
from qgis.utils import spatialite_connect

class DbView:
    
    def init(self, path):
        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()

        cur.execute('DROP VIEW IF EXISTS klassificerade_ytor')
        
        cur.execute("CREATE VIEW klassificerade_ytor AS \
            SELECT class.id AS id, \
                class.id_ini AS id_new, \
                class.geometri_typ, \
                class.grupp AS grupp, \
                class.kvalitet AS kvalitet, \
                polygon_object.id AS id_ini, \
                polygon_object.geom AS geometry \
            FROM polygon_object \
            JOIN classification AS class ON (polygon_object.id = class.id_ini) \
            WHERE class.geometri_typ = 'yta';")

        cur.execute("INSERT INTO views_geometry_columns  \
            (view_name, view_geometry, view_rowid, f_table_name, f_geometry_column, read_only) \
            VALUES ('klassificerade_ytor', 'geometry', 'id', 'classification', 'geom', 1);")
            
        cur.execute("SELECT * FROM klassificerade_ytor;")
        
            
        cur.close()
        con.close()

        
