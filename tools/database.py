'''
---------------------------------------------------------------------------
Database.py
Created on: 2019-03-13 11:37:53.00000
---------------------------------------------------------------------------
'''

def createDB(path):
    '''
    This function checks if there is a sqlite database for QGYF estimation and
    creates one in case it doesn't
    '''
    import os
    import sys
    sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis\python')
    from qgis.utils import spatialite_connect

    # Check path to database
    if not os.path.isdir(path):
        os.mkdir(path)

    # create a db or connect to existing one
    con = spatialite_connect(path + r'\qgyf_db.sqlite')
    cur = con.cursor()

    # clear layers/tables in db or fill db if it is empty
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    if cur.fetchall():
        tables = ['punkt_objekt', 'linje_objekt', 'areal_objekt', 'begransningsomrade', 'qgyf_kvaliteter', 'klassning']
        for t in tables:
            cur.execute("DELETE FROM " + t)
        con.isolation_level = None
        cur.execute("VACUUM")
        con.isolation_level = ''
    else:
        cur.execute("SELECT InitSpatialMetaData()")
        # create a point layer
        cur.execute("""CREATE TABLE punkt_objekt (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        filnamn TEXT,
        kvalitetgrupp TEXT NOT NULL,
        kvalitet TEXT NOT NULL,
        beskrivning TEXT);""")
        cur.execute("""SELECT AddGeometryColumn('punkt_objekt', 'the_geom',
        3006, 'POINT', 'XY');""")

        # create a line layer
        cur.execute("""CREATE TABLE linje_objekt (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        filnamn TEXT,
        kvalitetgrupp TEXT NOT NULL,
        kvalitet TEXT NOT NULL,
        beskrivning TEXT);""")
        cur.execute("""SELECT AddGeometryColumn('linje_objekt', 'the_geom',
        3006, 'LINESTRING', 'XY');""")

        # create a polygon layer
        cur.execute("""CREATE TABLE areal_objekt (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        filnamn TEXT,
        kvalitetgrupp TEXT NOT NULL,
        kvalitet TEXT NOT NULL,
        beskrivning TEXT);""")
        cur.execute("""SELECT AddGeometryColumn('areal_objekt', 'the_geom',
        3006, 'POLYGON', 'XY');""")

        # create a layer for research area
        cur.execute("""CREATE TABLE begransningsomrade (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        namn TEXT,
        yta DOUBLE NOT NULL,
        beskrivning TEXT);""")
        cur.execute("""SELECT AddGeometryColumn('begransningsomrade',
        'the_geom', 3006, 'POLYGON', 'XY');""")

        # create a QGYF table för qualities and factors
        cur.execute("""CREATE TABLE qgyf_kvaliteter (
        kvalitet TEXT NOT NULL,
        faktor DOUBLE NOT NULL,
        exempel TEXT);""")

        # create a table for classification
        cur.execute("""CREATE TABLE klassning (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        geometri_typ TEXT NOT NULL,
        id_ini INTEGER NOT NULL,
        kvalitet TEXT NOT NULL,
        faktor DOUBLE NOT NULL);""")

    cur.close()
    con.close()

if __name__ == '__main__':
    createDB(path)
