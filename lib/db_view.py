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
        
        cur.execute("CREATE VIEW klassificerade_ytor AS \
            SELECT class.id_ini AS id_ini WHERE class.geometri_typ = yta, \
                class.grupp AS grupp, \
                class.kvalitet AS kvalitet, \
                polygon_object.id AS id \
            FROM classification AS class \
            JOIN polygon_object ON (class.id_ini = polygon_object.id);")
            
            
            
        cur.close()
        con.close()

        
