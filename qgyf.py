# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGYF
								 A QGIS plugin
 Green Space Factor
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
							  -------------------
		begin                : 2019-03-01
		git sha              : $Format:%H$
		copyright            : (C) 2019 by C/O City
		email                : info@cocity.se
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt, QVariant
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsCoordinateReferenceSystem, QgsFields, QgsField, NULL, QgsWkbTypes
from qgis.gui import QgsFileWidget
from .resources import *

from .ui.qgyf_dockwidget import QGYFDockWidget
from .ui.welcome import WelcomeDialog
from .ui.settings import SettingsDialog
from .ui.layer_selector import LayerSelectorDialog
from .ui.export import ExportDialog
from .ui.radius_height import GeometryDialog
from .lib.db import Db
from .lib.switch_gyf import SwitchGYFs
from .lib.gyf_tables import QualityTable
from .lib.db_view import DbView
from .lib.ground_areas import GroundAreas
from .lib.file_loader import FileLoader
from .lib.styles import Style
from .lib.gyf_calculator import GyfCalculator
from .lib.gyf_diagram import Diagram
from .lib.map_export import ExportCreator

import os
import os.path
import numpy as np
import inspect
import uuid
from shutil import copyfile

class QGYF:

	def __init__(self, iface):
		self.iface = iface
		self.plugin_dir = os.path.dirname(os.path.abspath(__file__))

		locale = QSettings().value('locale/userLocale')[0:2]
		locale_path = os.path.join(
			self.plugin_dir,
			'i18n',
			'QGYF_{}.qm'.format(locale))

		if os.path.exists(locale_path):
			self.translator = QTranslator()
			self.translator.load(locale_path)
			if qVersion() > '4.3.3':
				QCoreApplication.installTranslator(self.translator)

		if not QSettings().value('dataPath'):
			QSettings().setValue('dataPath', os.getenv('APPDATA') + '\QGYF')
			if not os.path.exists(QSettings().value('dataPath')):
				os.makedirs(QSettings().value('dataPath'))

		if not QSettings().value('activeDataBase'):
			QSettings().setValue('activeDataBase', 'qgyf.sqlite')

		if not QSettings().value('CRS'):
			crs = QgsCoordinateReferenceSystem("EPSG:3006")
			QSettings().setValue('CRS', crs.authid())

		if not QSettings().value('model'):
			QSettings().setValue('model', 'KvartersGYF, Sthm Stad')

		QSettings().setValue('objectCount', 0)
		QSettings().setValue('groundArea', 0)
		QSettings().setValue('pointsCoord', 0)

		self.actions = []
		self.menu = self.translate(u'&QGYF')
		self.toolbar = self.iface.addToolBar(u'QGYF')
		self.toolbar.setObjectName(u'QGYF')
		self.pluginIsActive = False
		self.dockwidget = QGYFDockWidget()
		self.area_id = None
		self.diagram = Diagram()
		self.switch = SwitchGYFs(self.dockwidget, self.plugin_dir)
		self.gyfModel = self.switch.defineGYF()

		self.layerSelectorDialog = LayerSelectorDialog()
		self.fileLoader = FileLoader(self.iface.mainWindow(), self.layerSelectorDialog, self.dockwidget, QSettings().value('dataPath'))
		self.calculator = GyfCalculator(QSettings().value('dataPath'))
		self.showWelcome()

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/qgyf/assets/load_db.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Ladda databas'),
			callback=self.load,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/folder.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Ladda lager'),
			callback=self.loadFile,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/tree.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Beräkna grönytefaktor'),
			callback=self.openCalculationDialog,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/save.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Spara databas'),
			callback=self.save,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/settings.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Inställningar'),
			callback=self.openSettingsDialog,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/doc.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Öppna användarmanual'),
			callback=self.openDoc,
			parent=self.iface.mainWindow())

		# icon_path = ':/plugins/qgyf/assets/edit_point.png'
		# self.addAction(
		# 	icon_path,
		# 	text=self.translate(u'Editera punktobjekt'),
		# 	callback=self.info,
		# 	parent=self.iface.mainWindow())

		# icon_path = ':/plugins/qgyf/assets/edit_polyline.png'
		# self.addAction(
		# 	icon_path,
		# 	text=self.translate(u'Editera linjeobjekt'),
		# 	callback=self.info,
		# 	parent=self.iface.mainWindow())

		# icon_path = ':/plugins/qgyf/assets/edit_polygon.png'
		# self.addAction(
		# 	icon_path,
		# 	text=self.translate(u'Editera ytobjekt'),
		# 	callback=self.info,
		# 	parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/info.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Vissa upp informationsfönstret'),
			callback=self.info,
			parent=self.iface.mainWindow())

	def openDoc(self):
		docPath = self.plugin_dir + r'\\qgyf_user_guide.pdf'
		try:
			os.startfile(docPath)
		except:
			QMessageBox.warning(ExportDialog(), 'Ingen PDF läsare', 'Det ser ut att ingen PDF läsare finns installerat på datorn.')

	def load(self):
		self.initDatabase(QSettings().value('dataPath'))
		self.addLayers(QSettings().value('dataPath'), [
			"research_area",
			"point_object",
			"line_object",
			"polygon_object",
		])
		if self.dockwidget.isVisible():
			self.dockwidget.showClass()

	def translate(self, message):
		"""Get the translation for a string using Qt translation API.

		We implement this ourselves since we do not inherit QObject.

		:param message: String for translation.
		:type message: str, QString

		:returns: Translated version of message.
		:rtype: QString
		"""
		# noinspection PyTypeChecker,PyArgumentList,PyCallByClass
		return QCoreApplication.translate('QGYF', message)

	def addAction(
		self,
		icon_path,
		text,
		callback,
		enabled_flag=True,
		add_to_menu=True,
		add_to_toolbar=True,
		status_tip=None,
		whats_this=None,
		parent=None):

		icon = QIcon(icon_path)
		action = QAction(icon, text, parent)
		action.triggered.connect(callback)
		action.setEnabled(enabled_flag)

		if status_tip is not None:
			action.setStatusTip(status_tip)

		if whats_this is not None:
			action.setWhatsThis(whats_this)

		if add_to_toolbar:
			self.toolbar.addAction(action)

		if add_to_menu:
			self.iface.addPluginToMenu(
				self.menu,
				action)

		self.actions.append(action)

		return action

	def saveCheckBoxStatus(self):
		QSettings().setValue('checkBoxStatus', not self.welcome.checkBox.isChecked())
		QSettings().sync()

	def showWelcome(self):
		"""Show welcome message."""
		check_state = QSettings().value('checkBoxStatus', True, type=bool)
		if check_state is True:
			self.welcome = WelcomeDialog()
			self.welcome.show()
			self.welcome.okButton.clicked.connect(self.welcome.close)
			self.welcome.checkBox.clicked.connect(self.saveCheckBoxStatus)

	def loadFile(self):
		db = Db()
		initialized = db.check(QSettings().value('dataPath'))
		if not initialized:
			self.load()

		self.layerSelectorDialog.loadClassifications(QSettings().value('dataPath'))
		self.fileLoader.loadFile()
		root = QgsProject.instance().layerTreeRoot()
		content = [l.name() for l in root.children()]
		if 'Kvaliteter' in content:
			self.dockwidget.disableGroup()
		if self.dockwidget.isVisible():
			self.dockwidget.showClass()

	def info(self):
		self.welcome = WelcomeDialog()
		self.welcome.show()
		self.welcome.okButton.clicked.connect(self.welcome.close)

	def addLayers(self, path, layers):
		self.style = Style()
		root = QgsProject.instance().layerTreeRoot()
		classificationGroup = root.findGroup('Klassificering')
		visualizationGroup = root.findGroup('Kvaliteter')

		for layer in root.findLayers():
			if layer.name() == "Beräkningsområde":
				root.removeChildNode(layer)
			elif layer.name() == "Grundytor":
				root.removeChildNode(layer)
		if classificationGroup:
			root.removeChildNode(classificationGroup)
		if visualizationGroup:
			root.removeChildNode(visualizationGroup)

		classificationGroup = root.insertGroup(0, "Klassificering")
		layerNames =	{
		  "point_object": "Punktobjekt",
		  "line_object": "Linjeobjekt",
		  "polygon_object": "Ytobjekt",
		  "research_area": "Beräkningsområde"
		}

		for layer in layers:
			pathLayer = '{}\{}|layername={}'.format(path, QSettings().value("activeDataBase"), layer)
			vlayer = QgsVectorLayer(pathLayer, layerNames[layer], "ogr")

			if layer == "research_area":
				self.style.styleResearchArea(vlayer)
				QgsProject.instance().addMapLayer(vlayer)
			else:
				self.style.iniStyle(vlayer)
				QgsProject.instance().addMapLayer(vlayer, False)
				classificationGroup.addLayer(vlayer)
				vlayer.featureAdded.connect(lambda fid, vlayer=vlayer : self.featureAdded(fid, vlayer))
				vlayer.geometryChanged.connect(lambda fid, geom ,vlayer=vlayer : self.geometryModified(fid, geom, vlayer))
				vlayer.committedGeometriesChanges.connect(self.dockwidget.showClass)
				vlayer.committedFeaturesRemoved.connect(lambda : self.dockwidget.removeQ(QSettings().value('dataPath')))
				vlayer.committedFeaturesRemoved.connect(self.dockwidget.showClass)

	def geometryModified(self, fid, geom, layer):
		feature = layer.getFeature(fid)
		geom_type = QgsWkbTypes.geometryDisplayString(geom.type())
		if len(feature["gid"]) == 36:
			if geom_type == "Polygon":
				feature["yta"] = feature.geometry().area()
			elif geom_type == "Line":
				feature["yta"] = feature.geometry().length()
			layer.updateFeature(feature)
			self.dockwidget.updateClassArea(QSettings().value('dataPath'), feature["gid"], feature["yta"])

	def featureAdded(self, fid, layer):
		feature = layer.getFeature(fid)
		geom_type = QgsWkbTypes.geometryDisplayString(feature.geometry().type())
		if feature["gid"] == NULL or len(feature["gid"]) != 36:
			feature["gid"] = str(uuid.uuid4())
			if geom_type == "Polygon":
				feature["yta"] = feature.geometry().area()
			elif geom_type == "Point":
				print(type(feature["yta"]))
				if type(feature["yta"]) != float:
					feature["yta"] = 25.0
			else:
				feature["yta"] = feature.geometry().length()
			layer.updateFeature(feature)

	def initDatabase(self, path):
		self.db = Db()
		self.db.create(path)
		self.quality = QualityTable()
		self.quality.init(path, self.gyfModel)

	def onClosePlugin(self):
		self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

	def unload(self):
		for action in self.actions:
			self.iface.removePluginMenu(
				self.translate(u'&QGYF'),
				action)
			self.iface.removeToolBarIcon(action)
		del self.toolbar

	def createDataView(self):
		if self.dockwidget.tabWidget.currentIndex() != 0:
			self.dbView = DbView()
			self.dbView.init(QSettings().value('dataPath'))
			self.createGA = GroundAreas()
			self.createGA.init(QSettings().value('dataPath'))
			self.createGA.showGA(QSettings().value('dataPath'))

	def updateGA(self):
		self.createGA = GroundAreas()
		self.createGA.init(QSettings().value('dataPath'))

	def calculate(self):
		self.createDataView()

		gyf, factor_areas, groups, feature_ids, area_id, ground_area, eco_area = self.calculator.calculate()
		self.dockwidget.gyfValue.setText("{0:.2f}".format(gyf))

		try:
			if factor_areas.size != 0:
				# Plot
				self.dockwidget.plot.canvas.ax.cla()
				self.dockwidget.plot.canvas.ax.set_title('Fördelning av kvalitetspoäng')
				sizes, legend, colors, outline = self.diagram.init(factor_areas, groups)
				patches, text = self.dockwidget.plot.canvas.ax.pie(sizes, colors=colors, startangle=90, wedgeprops=outline)
				#self.dockwidget.plot.canvas.fig.tight_layout()
				# Legend
				patches, legend, dummy =  zip(*sorted(zip(patches, legend, sizes), key=lambda x: x[2], reverse=True))
				self.dockwidget.plot.canvas.ax2.legend(patches, legend, loc = 'center', shadow = None, frameon = False)
				self.dockwidget.plot.canvas.draw()
		except:
			pass

		self.area_id = area_id
		self.groups = groups
		self.feature_ids = feature_ids
		self.eco_area = eco_area
		self.ground_area = ground_area

	def showExportDialog(self):
		if self.area_id == None:
			QMessageBox.warning(ExportDialog(), 'Ingen GYF', 'Beräkna GYF först för att exportera resultat!')
		else:
			self.exportDialog = ExportDialog()
			self.exportDialog.show()
			self.exportDialog.okButton.clicked.connect(self.export)
			self.exportDialog.okButton.clicked.connect(self.exportDialog.close)

	def export(self):
		chart_path = QSettings().value('dataPath') + '\PieChart.png'
		self.dockwidget.plot.canvas.fig.savefig(chart_path)
		gyf = self.dockwidget.gyfValue.text()
		try:
			self.diagram.ecoAreaPlot(self.ground_area, self.eco_area/float(gyf))
		except:
			pass
		groups = []
		checkboxnames = ['checkBio', 'checkBuller', 'checkVatten', 'checkKlimat', 'checkPoll', 'checkHalsa']
		checkbox_list = [getattr(self.dockwidget, n) for n in checkboxnames]
		for checkbox in checkbox_list:
			if checkbox.isEnabled() and checkbox.isChecked():
				groups.append(checkbox.text())
		groups = [g for g in groups if g in self.groups]
		self.pdfCreator = ExportCreator()
		self.pdfCreator.exportPDF(chart_path, gyf, self.exportDialog, self.area_id, groups, self.feature_ids, self.eco_area)

	def openCalculationDialog(self):
		
		db = Db()
		initialized = db.check(QSettings().value('dataPath'))
		if not initialized:
			self.load()

		self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
		if not self.pluginIsActive:
			self.pluginIsActive = True
			self.initCalculationDialog()
			self.dockwidget.show()
			self.dockwidget.showClass()

		print(self.gyfModel)

	def initCalculationDialog(self):

		# connect to provide cleanup on closing of dockwidget
		self.dockwidget.closingPlugin.connect(self.onClosePlugin)

		# Show GYF version
		self.switch.adjustDockwidget(self.gyfModel)

		# Classification
		self.dockwidget.switchLayerGroups()

		# Highlight rows in classification table
		self.iface.mapCanvas().selectionChanged.connect(self.dockwidget.highlightRows)

		# Qualities
		self.dockwidget.label_G.setText(self.gyfModel['label_G'])
		self.dockwidget.label_Q.setText(self.gyfModel['label_Q'])
		self.dockwidget.chooseQ('gyf_qgroup', self.dockwidget.selectQGroup, self.dockwidget.selectQ, self.dockwidget.textQ)
		self.dockwidget.chooseQ('gyf_areas', self.dockwidget.selectYGroup, self.dockwidget.selectY, self.dockwidget.textY)

		self.dockwidget.selectQGroup.currentIndexChanged.connect(self.dockwidget.getQ)
		self.dockwidget.selectQ.currentIndexChanged.connect(self.dockwidget.getF)

		self.dockwidget.approveButton.clicked.connect(self.dockwidget.setQ)
		self.dockwidget.removeButton.clicked.connect(self.dockwidget.removeQ)

		self.dockwidget.classtable.itemSelectionChanged.connect(self.dockwidget.highlightFeatures)
		self.dockwidget.geometryButton.clicked.connect(self.openGeometryDialog)

		# Objects
		self.dockwidget.setLayers()
		self.dockwidget.selectLayer.currentIndexChanged.connect(self.dockwidget.selectStart)

		# Visualisation
		self.dockwidget.tabWidget.currentChanged.connect(self.createDataView)
		self.dockwidget.tabWidget.currentChanged.connect(self.dockwidget.disableGroup)
		self.dockwidget.tabWidget.currentChanged.connect(self.dockwidget.switchLayerGroups)
		self.dockwidget.groupList()

		# Estimation of GYF
		# Research area
		self.dockwidget.calculate.setStyleSheet("color: #006600")
		self.dockwidget.selectRA.clicked.connect(self.dockwidget.selectArea)
		self.dockwidget.createRA.clicked.connect(self.dockwidget.createArea)
		# GYF
		self.dockwidget.calculate.clicked.connect(self.calculate)

		# Export
		self.dockwidget.report.clicked.connect(self.showExportDialog)

	def openGeometryDialog(self):
		layers = [layer for layer in QgsProject.instance().mapLayers().values()]
		names = []
		for l in layers:
			if l.isEditable():
				names.append(l.name())
		if names:
			QMessageBox.warning(ExportDialog(), 'Stäng redigeringsläge', 'Spara ändringar och gå ur redigeringsläget för att sätta punktyta/linjehöjd')
		else:
			self.geometry = GeometryDialog(self.dockwidget, QSettings().value('dataPath'))

	def openSettingsDialog(self):
		self.settings = SettingsDialog(self.dockwidget, self.gyfModel, self.plugin_dir, None, self)
		self.settings.show()
		self.settings.okButton.clicked.connect(self.settings.close)

	def save(self):
		path = QFileDialog.getSaveFileName(self.iface.mainWindow(), 'Spara som', QSettings().value('dataPath'), '*.sqlite')
		new_path = path[0]
		database = QSettings().value('activeDataBase')
		path = "{}/{}".format(QSettings().value('dataPath'), database)
		if path and new_path:
			copyfile(path, new_path)

