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
from PyQt5.QtCore import QSettings

class Db:

	def init(self, cur, con):
		"""
		Check for existing sqlite database for QGYF estimations, create one if needed.
		Initialize tables to store geo-objects (point, line, polygon) and calculations.
		"""

		if QSettings().value('CRS'):
			crs = QSettings().value('CRS')
			crs = ''.join(c for c in crs if c.isdigit())
			print(crs)
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
            ytklass TEXT,
            yta DOUBLE);""")

		cur.execute("""SELECT AddGeometryColumn('ground_areas', 'geom', """ + crs + """, 'MULTIPOLYGON', 'XY');""")

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

	def check(self, path):
		"""
		Check if the database is initialized
		"""
		# Check path to database.
		if not os.path.isdir(path):
			os.mkdir(path)

		con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))
		cur = con.cursor()
		cur.execute("SELECT name FROM sqlite_master WHERE type='table';")

		result = cur.fetchall()

		cur.close()
		con.close()

		return result

	def checkClass(self, path):
		"""
		Check if the classification table is filled
		"""
		if not os.path.exists("{}\{}".format(path, QSettings().value('activeDataBase'))):
			return True
		else:
			con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))
			cur = con.cursor()
			cur.execute("SELECT count(*) FROM classification;")

			result = cur.fetchone()
			cur.close()
			con.close()
			
			print(result[0])
			if result[0] == 0:
				return True
			else:
				return False

	def clear(self, path):
		"""
		Empty existing tables.
		"""
		con = spatialite_connect(path)
		cur = con.cursor()

		tables = [
			'point_object',
			'line_object',
			'polygon_object',
			'research_area',
			'classification',
			'ground_areas'
		]

		for table in tables:
			cur.execute("DELETE FROM " + table)

		con.isolation_level = None
		cur.execute("VACUUM")
		con.isolation_level = ""
		cur.close()
		con.close()

	def create(self, path):
		"""
		Initialize database.
		"""
		# Check path to database.
		if not os.path.isdir(path):
			os.mkdir(path)

		# Create a database or connect to existing one.
		con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))
		cur = con.cursor()

		cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
		# Fill database if it is empty.
		if not cur.fetchall():
			self.init(cur, con)

		cur.close()
		con.close()