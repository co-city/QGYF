# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------
CategoryTable.py
Created on: 2019-03-18 13:30:53
---------------------------------------------------------------------------
"""
import os
import sys
from qgis.utils import spatialite_connect
from PyQt5.QtCore import QSettings

class QualityTable:

    def init(self, path):
        """ Populate the table "gyf_quality" with values of C/O City's GYF """
        inputfile_group = 'gyf_AP_groups.txt'
        inputfile_quality = 'gyf_AP_qualities.txt'
        
        group = self.readInputGYF(inputfile_group)
        q_f   = self.readInputGYF(inputfile_quality)

        con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))
        cur = con.cursor()
        cur.execute("SELECT id FROM gyf_qgroup")
        if not cur.fetchall():
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