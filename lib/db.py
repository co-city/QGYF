"""
---------------------------------------------------------------------------
db.py
Created on: 2019-03-14 16:20:53
---------------------------------------------------------------------------
"""
import os
import sys
sys.path.append(r'C:\Program Files\QGIS 3.4\apps\qgis\python')
from qgis.utils import spatialite_connect
from qgis.core import QgsProject

class Db:

	def init(self, cur, con):
		"""
		Check for existing sqlite database for QGYF estimations, create one if needed.
		Initialize tables to store geo-objects (point, line, polygon) and calculations.
		"""
		if QgsProject.instance().readEntry("QGYF", "CRS")[0]:
			crs = QgsProject.instance().readEntry("QGYF", "CRS")[0]
		else:
			crs = '3006' # SWEREF99 TM is default

		# The InitSpatialMetaData() function must be called immediately after creating a new database,
		# and before attempting to call any other Spatial SQL function.
		# The PRAGMA operations speeds up the process.
		try:
			con.isolation_level = None # Is necessary for QGIS 3.2.2 (the bug that was fixed in later versions), but results in lower performance
			cur.execute("BEGIN;")
			cur.execute("COMMIT;")
			cur.execute("PRAGMA synchronous = OFF;")
			cur.execute("PRAGMA journal_mode = MEMORY;")
			cur.execute("BEGIN;")
			cur.execute("SELECT InitSpatialMetaData(0)")
			cur.execute("COMMIT;")
			cur.execute("BEGIN;")
			cur.execute("COMMIT;")
			cur.execute("PRAGMA synchronous = FULL;")
			cur.execute("PRAGMA journal_mode = DELETE;")
		except:
			con.isolation_level = None  
			cur.execute("BEGIN;")
			cur.execute("SELECT InitSpatialMetaData(0)")
			cur.execute("COMMIT;")

		cur.execute("""
		CREATE TABLE point_object (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		gid TEXT,
		filnamn TEXT,
		beskrivning TEXT,
		yta DOUBLE);""")

		cur.execute("SELECT AddGeometryColumn('point_object', 'geom', " + crs + ", 'POINT', 'XY');")

		cur.execute("""
		CREATE TABLE line_object (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		gid TEXT,
		filnamn TEXT,
		beskrivning TEXT,
		yta DOUBLE);""")

		cur.execute("""SELECT AddGeometryColumn('line_object', 'geom', """ + crs + """, 'LINESTRING', 'XY');""")

		cur.execute("""
		CREATE TABLE polygon_object (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		gid TEXT,
		filnamn TEXT,
		beskrivning TEXT,
		yta DOUBLE);""")

		cur.execute("""SELECT AddGeometryColumn('polygon_object', 'geom', """ + crs + """, 'POLYGON', 'XY');""")

		cur.execute("""
		CREATE TABLE research_area (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		namn TEXT,
		yta DOUBLE);""")

		cur.execute("""SELECT AddGeometryColumn('research_area', 'geom', """ + crs + """, 'POLYGON', 'XY');""")

		cur.execute("""CREATE TABLE ground_areas (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		ytgrupp TEXT,
		ytklass TEXT,
		faktor DOUBLE,
		yta DOUBLE,
		poang DOUBLE);""")

		cur.execute("""SELECT AddGeometryColumn('ground_areas', 'geom', """ + crs + """, 'MULTIPOLYGON', 'XY');""")

		cur.execute("""CREATE TABLE ga_template (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		ytgrupp TEXT,
		ytklass TEXT,
		faktor DOUBLE,
		yta DOUBLE,
		poang DOUBLE);""")

		cur.execute("""SELECT AddGeometryColumn('ga_template', 'geom', """ + crs + """, 'MULTIPOLYGON', 'XY');""")

		cur.execute("""
		CREATE TABLE gyf_quality (
		grupp_id INTEGER NOT NULL,
		kvalitet TEXT NOT NULL,
		faktor DOUBLE NOT NULL,
		namn TEXT,
		kort_namn TEXT,
		beskrivning TEXT);
		""")

		cur.execute("""
		CREATE TABLE gyf_qgroup (
		id INTEGER NOT NULL,
		grupp TEXT NOT NULL,
		faktor DOUBLE NOT NULL);
		""")

		cur.execute("""
		CREATE TABLE gyf_areas (
		grupp_id INTEGER NOT NULL,
		grupp TEXT NOT NULL,
		kvalitet TEXT NOT NULL,
		faktor DOUBLE NOT NULL,
		namn TEXT,
		kort_namn TEXT,
		beskrivning TEXT);
		""")

		# id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		cur.execute("""
		CREATE TABLE classification (
		gid TEXT,
		geometri_typ TEXT,
		filnamn TEXT,
		grupp TEXT,
		kvalitet TEXT,
		faktor DOUBLE NOT NULL,
		yta DOUBLE,
		poang DOUBLE);""")

		cur.execute("""SELECT InitSpatialMetaData();""")

	def check(self):
		"""
		Check if the database is initialized
		"""
		# Check path to database.
		path = QgsProject.instance().readEntry("QGYF", "dataPath")[0]
		db = QgsProject.instance().readEntry("QGYF", "activeDataBase")[0]

		if not os.path.isdir(path):
			os.mkdir(path)

		if db and os.path.exists("{}\{}".format(path, db)):
			con = spatialite_connect("{}\{}".format(path, db))
			cur = con.cursor()
			cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

			result = cur.fetchall()

			cur.close()
			con.close()

			return result
		else:
			return None

	def checkClass(self):
		"""
		Check if the classification table is filled
		"""
		db = QgsProject.instance().readEntry("QGYF", "activeDataBase")[0]
		path = QgsProject.instance().readEntry("QGYF", "dataPath")[0]
		if not os.path.exists("{}\{}".format(path, db)):
			return True
		else:
			con = spatialite_connect("{}\{}".format(path, db))
			cur = con.cursor()
			cur.execute("SELECT count(*) FROM classification;")

			result = cur.fetchone()
			cur.close()
			con.close()
			
			if result[0] == 0:
				return True
			else:
				return False

	def checkObjects(self):
		"""
		Check if the db contains data
		"""
		db = QgsProject.instance().readEntry("QGYF", "activeDataBase")[0]
		path = QgsProject.instance().readEntry("QGYF", "dataPath")[0]
		if not os.path.exists("{}\{}".format(path, db)):
			return True
		else:
			con = spatialite_connect("{}\{}".format(path, db))
			cur = con.cursor()
			tables = ['ground_areas', 'polygon_object', 'line_object', 'point_object']
			count = 0
			for t in tables:
				cur.execute("SELECT count(*) FROM " + t)
				result = cur.fetchone()[0]
				count += result
			cur.close()
			con.close()

			if count == 0:
				return True
			else:
				return False



	def clear(self):
		"""
		Empty existing tables.
		"""
		db = QgsProject.instance().readEntry("QGYF", "activeDataBase")[0]
		path = QgsProject.instance().readEntry("QGYF", "dataPath")[0]
		con = spatialite_connect("{}\{}".format(path, db))
		cur = con.cursor()

		tables = [
			'point_object',
			'line_object',
			'polygon_object',
			'research_area',
			'classification',
			'ground_areas',
			'ga_template'
		]

		for table in tables:
			cur.execute("DELETE FROM " + table)

		con.isolation_level = None
		cur.execute("VACUUM")
		con.isolation_level = ""
		cur.close()
		con.close()

	def create(self):
		"""
		Initialize database.
		"""
		# Check path to database.
		path = QgsProject.instance().readEntry("QGYF", "dataPath")[0]
		if not os.path.isdir(path):
			os.mkdir(path)

		# Create a database or connect to existing one.
		db = QgsProject.instance().readEntry("QGYF", "activeDataBase")[0]
		con = spatialite_connect("{}\{}".format(path, db))
		cur = con.cursor()

		cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		# Fill database if it is empty.
		if not cur.fetchall():
			self.init(cur, con)

		cur.close()
		con.close()