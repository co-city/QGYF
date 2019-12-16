# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------
QualityTable.py
Created on: 2019-03-18 13:30:53
---------------------------------------------------------------------------
"""
import os
import sys
from qgis.utils import spatialite_connect
from qgis.core import QgsProject

class QualityTable:

    def init(self, model):
        """ Populate the table "gyf_quality" with GYF values """
        
        areas = self.readInputGYF(model['Input_ground_areas'])
        group = self.readInputGYF(model['Input_groups'])
        q_f   = self.readInputGYF(model['Input_categories'])
        proj = QgsProject.instance()

        con = spatialite_connect("{}\{}".format(proj.readEntry("QGYF", "dataPath")[0], proj.readEntry("QGYF", "activeDataBase")[0]))
        cur = con.cursor()
        cur.execute("SELECT id FROM gyf_qgroup")
        if cur.fetchall():
            cur.execute('''SELECT grupp FROM gyf_qgroup''')
            items = [i[0] for i in cur.fetchall()]
            c_items = [i[1] for i in group]
            # Load another GYF
            if not set(items) == set(c_items):
                cur.execute("DELETE FROM gyf_areas")
                cur.execute("DELETE FROM gyf_qgroup")
                cur.execute("DELETE FROM gyf_quality")
                cur.executemany('INSERT OR IGNORE INTO gyf_areas VALUES (?,?,?,?,?,?,?)', areas)
                cur.executemany('INSERT OR IGNORE INTO gyf_qgroup VALUES (?,?,?)', group)
                cur.executemany('INSERT OR IGNORE INTO gyf_quality VALUES (?,?,?,?,?,?)', q_f)
        else:
            cur.executemany('INSERT OR IGNORE INTO gyf_areas VALUES (?,?,?,?,?,?,?)', areas)
            cur.executemany('INSERT OR IGNORE INTO gyf_qgroup VALUES (?,?,?)', group)
            cur.executemany('INSERT OR IGNORE INTO gyf_quality VALUES (?,?,?,?,?,?)', q_f)
        con.commit()

        cur.close()
        con.close()

    def readInputGYF(self, inputfile):
        output = []
        filepath = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", 'gyf_models', inputfile))
        with open(filepath, 'r', encoding="windows-1252") as inputdata:
            lines = inputdata.read().splitlines()
            lines = [l for l in lines if '#' not in l]
            for l in lines:
                item = [splits for splits in l.split("\t") if splits is not ""]
                output.append(item)
        return output

