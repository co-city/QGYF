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

		# The InitSpatialMetaData() function must be called immediately after creating a new database,
		# and before attempting to call any other Spatial SQL function.
		# The PRAGMA operations speeds up the process.
		cur.execute("PRAGMA synchronous = OFF;")
		cur.execute("PRAGMA journal_mode = MEMORY;")
		cur.execute("SELECT InitSpatialMetaData(0)")
		cur.execute("PRAGMA synchronous = FULL;")
		cur.execute("PRAGMA journal_mode = DELETE;")

		cur.execute("""CREATE TABLE point_object (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		filnamn TEXT,
		beskrivning TEXT);""")

		cur.execute("""SELECT AddGeometryColumn('point_object', 'geom',
		3006, 'POINT', 'XY');""")

		cur.execute("""
		CREATE TABLE line_object (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		filnamn TEXT,
		beskrivning TEXT);""")

		cur.execute("""SELECT AddGeometryColumn('line_object', 'geom',
		3006, 'LINESTRING', 'XY');""")

		cur.execute("""
		CREATE TABLE polygon_object (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		filnamn TEXT,
		beskrivning TEXT);""")

		cur.execute("""SELECT AddGeometryColumn('polygon_object', 'geom',
		3006, 'POLYGON', 'XY');""")

		cur.execute("""
		CREATE TABLE research_area (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		namn TEXT,
		yta DOUBLE);""")

		cur.execute("""SELECT AddGeometryColumn('research_area',
		'geom', 3006, 'POLYGON', 'XY');""")

		cur.execute("""
		CREATE TABLE gyf_quality (
		grupp_id INTEGER NOT NULL,
		kvalitet TEXT NOT NULL,
		faktor DOUBLE NOT NULL,
		namn TEXT,
		kort_namn TEXT);
		""")

		cur.execute("""
		CREATE TABLE gyf_qgroup (
		id INTEGER NOT NULL,
		grupp TEXT NOT NULL,
		faktor DOUBLE NOT NULL);
		""")

		cur.execute("""
		CREATE TABLE classification (
		id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
		geometri_typ TEXT,
		filnamn TEXT,
		id_ini INTEGER NOT NULL,
		grupp TEXT,
		kvalitet TEXT,
		faktor DOUBLE NOT NULL);""")

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
			'classification'
		]

		for table in tables:
			cur.execute("DELETE FROM " + table)

		con.isolation_level = None
		cur.execute("VACUUM")
		con.isolation_level = ""
		cur.close()
		con.close()

	def create(self, path):
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