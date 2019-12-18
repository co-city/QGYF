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
		self.proj = QgsProject.instance()

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

		if not self.proj.readEntry("QGYF", "dataPath")[0]:
			self.proj.writeEntry("QGYF", "dataPath", os.getenv('APPDATA') + '\QGYF')
			if not os.path.exists(self.proj.readEntry("QGYF", "dataPath")[0]):
				os.makedirs(self.proj.readEntry("QGYF", "dataPath")[0])

		if not self.proj.readEntry("QGYF", "model")[0]:
			self.proj.writeEntry("QGYF", "model", 'KvartersGYF, Sthm Stad')

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
		self.db = Db()
		self.createGA = GroundAreas()
		self.switch = SwitchGYFs(self.dockwidget, self.plugin_dir)
		self.gyfModel = self.switch.defineGYF()
		self.layerSelectorDialog = LayerSelectorDialog(self.gyfModel)
		self.fileLoader = FileLoader(self.iface.mainWindow(), self.layerSelectorDialog, self.dockwidget)
		
		self.showWelcome()

		#self.proj.projectSaved.connect(self.projectSettings)
		self.proj.readProject.connect(self.loadProject)

	def loadProject(self):
		if self.proj.fileName() and os.path.exists(self.proj.readEntry("QGYF", "dataPath")[0]+ r'\\' + self.proj.readEntry("QGYF", 'activeDataBase')[0]):
			self.addLayers(self.proj.readEntry("QGYF", "dataPath")[0], [
				"research_area",
				"ground_areas",
				"point_object",
				"line_object",
				"polygon_object"])

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
			text=self.translate(u'Importera data'),
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
		if self.proj.readEntry("QGYF", "CRS")[0]:
			self.initDatabase()
			self.addLayers(self.proj.readEntry("QGYF", "dataPath")[0], [
				"research_area",
				"ground_areas",
				"point_object",
				"line_object",
				"polygon_object",
			])
			if self.dockwidget.isVisible():
				self.dockwidget.showClass()
				self.dockwidget.showAreas()
		else:
			QMessageBox.warning(ExportDialog(), 'Inget definierat koordinatsystem', 
			'Sätt koordinatsystem i inställningar för att kunna skapa och ladda databas.')

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
		initialized = self.db.check()
		if not initialized:
			self.load()

		self.layerSelectorDialog.loadClassifications()
		self.fileLoader.loadFile()
		root = self.proj.layerTreeRoot()
		content = [l.name() for l in root.children()]
		if 'Kvaliteter' in content:
			self.dockwidget.disableGroup()
		if self.dockwidget.isVisible():
			self.dockwidget.showClass()
			self.dockwidget.showAreas()

	def info(self):
		self.welcome = WelcomeDialog()
		self.welcome.show()
		self.welcome.okButton.clicked.connect(self.welcome.close)

	def addLayers(self, path, layers):
		self.style = Style()
		root = self.proj.layerTreeRoot()
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
		  "research_area": "Beräkningsområde",
		  "ground_areas": "Grundytor"
		}

		path = self.proj.readEntry("QGYF", "dataPath")[0]
		for layer in layers:
			pathLayer = '{}\{}|layername={}'.format(path, self.proj.readEntry("QGYF", 'activeDataBase')[0], layer)
			vlayer = QgsVectorLayer(pathLayer, layerNames[layer], "ogr")

			if layer == "research_area":
				self.style.styleResearchArea(vlayer)
				self.proj.addMapLayer(vlayer)
				vlayer.geometryChanged.connect(lambda fid, geom, vlayer=vlayer: self.dockwidget.areaAdded(fid, vlayer))
				vlayer.featureAdded.connect(lambda fid, vlayer=vlayer: self.dockwidget.areaAdded(fid, vlayer))
			elif layer == "ground_areas":
				self.style.oneStyleGroundAreas(vlayer)
				self.proj.addMapLayer(vlayer)
				vlayer.setReadOnly(True)
			else:
				self.style.iniStyle(vlayer)
				self.proj.addMapLayer(vlayer, False)
				classificationGroup.addLayer(vlayer)
				vlayer.featureAdded.connect(lambda fid, vlayer=vlayer : self.featureAdded(fid, vlayer))
				vlayer.geometryChanged.connect(lambda fid, geom ,vlayer=vlayer : self.geometryModified(fid, geom, vlayer))
				vlayer.committedGeometriesChanges.connect(self.dockwidget.showClass)
				vlayer.committedFeaturesRemoved.connect(self.dockwidget.removeQ)
				vlayer.committedFeaturesRemoved.connect(self.dockwidget.showClass)

	def geometryModified(self, fid, geom, layer):
		feature = layer.getFeature(fid)
		geom_type = QgsWkbTypes.geometryDisplayString(geom.type())
		if len(feature["gid"]) == 36:
			if geom_type == "MultiPolygon":
				feature["yta"] = feature.geometry().area()
			elif geom_type == "Line":
				feature["yta"] = feature.geometry().length()
			layer.updateFeature(feature)
			self.dockwidget.updateClassArea(feature["gid"], feature["yta"])

	def featureAdded(self, fid, layer):
		feature = layer.getFeature(fid)
		geom_type = QgsWkbTypes.geometryDisplayString(feature.geometry().type())
		if feature["gid"] == NULL or len(feature["gid"]) != 36:
			feature["gid"] = str(uuid.uuid4())
			if geom_type == "MultiPolygon":
				feature["yta"] = feature.geometry().area()
			elif geom_type == "Point":
				if type(feature["yta"]) != float:
					feature["yta"] = 25.0
			else:
				feature["yta"] = feature.geometry().length()
			layer.updateFeature(feature)

	def initDatabase(self):
		self.db.create()
		self.quality = QualityTable()
		self.quality.init(self.gyfModel)

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
		if self.dockwidget.tabWidget.currentIndex() > 1:
			self.dbView = DbView()
			self.dbView.init()
			if not self.gyfModel['Ground_areas_enabled']:
				self.createGA.initAP()
				self.createGA.showGA()

	def updateGA(self):
		self.createGA.initAP(self.proj.readEntry("QGYF", "dataPath")[0])

	def calculate(self):
		calculator = GyfCalculator()
		self.createDataView()
		#if not hasattr(self.dockwidget.plot.canvas, 'ax'):
		#	self.diagram.initCanvas(self.dockwidget)
		self.dockwidget.plot.canvas.ax.cla()

		gyf, factor_areas, groups, feature_ids, area_id, ground_area, eco_area, balancering = calculator.calculate()
		self.dockwidget.gyfValue.setText("{0:.2f}".format(gyf))
		# Plot
		#try:
		if factor_areas and self.gyfModel['Version']=='GYF AP 2.0':
			self.diagram.piePlot(self.dockwidget, factor_areas, groups)
		if balancering and self.gyfModel['Version']=='GYF Kvartersmark':
			self.diagram.balancePlot(self.dockwidget, balancering)
		#except:
		#	pass

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
		chart_path = self.proj.readEntry("QGYF", 'dataPath')[0] + '\PieChart.png'
		self.dockwidget.plot.canvas.fig.savefig(chart_path)
		gyf = self.dockwidget.gyfValue.text()
		try:
			self.diagram.ecoAreaPlot(self.ground_area, self.eco_area/float(gyf))
		except:
			pass
		groups = []
		checkbox_list = []
		for i in range(self.dockwidget.checkBoxLayout.count()):
			checkbox_list.append(self.dockwidget.checkBoxLayout.itemAt(i).widget())
		for checkbox in checkbox_list:
			if checkbox.isEnabled() and checkbox.isChecked():
				groups.append(checkbox.text())
		groups = [g for g in groups if g in self.groups]
		self.pdfCreator = ExportCreator()
		self.pdfCreator.exportPDF(self.gyfModel, chart_path, gyf, self.exportDialog, self.area_id, groups, self.feature_ids, self.eco_area)

	def openCalculationDialog(self):
		initialized = self.db.check()
		if not initialized:
			QMessageBox.information(ExportDialog(), 'Ingen aktiv databas', 'Sätt sina inställningar och skapa en databas först för att börja QGYFs beräkningsprocess.')
			#self.load()
			return

		self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
		if not self.pluginIsActive:
			print(self.pluginIsActive)
			self.pluginIsActive = True
			self.initCalculationDialog()
			self.dockwidget.show()
			self.dockwidget.showClass()
			self.dockwidget.showAreas()

	def initCalculationDialog(self):

		# connect to provide cleanup on closing of dockwidget
		self.dockwidget.closingPlugin.connect(self.onClosePlugin)

		# Show GYF version
		self.switch.adjustDockwidget(self.gyfModel, self.layerSelectorDialog)

		# Classification
		self.dockwidget.switchLayerGroups()

		# Highlight rows in classification table
		self.iface.mapCanvas().selectionChanged.connect(self.dockwidget.highlightRows)
		self.iface.mapCanvas().selectionChanged.connect(self.dockwidget.highlightRowsAreas)

		# Qualities
		group_list = self.dockwidget.chooseQ('gyf_qgroup', self.dockwidget.selectQGroup, self.dockwidget.selectQ, self.dockwidget.textQ)
		group_areaslist = self.dockwidget.chooseQ('gyf_areas', self.dockwidget.selectYGroup, self.dockwidget.selectY, self.dockwidget.textY)

		get_qualities = lambda : self.dockwidget.getQ('gyf_quality', self.dockwidget.selectQGroup, self.dockwidget.selectQ, self.dockwidget.textQ)
		self.dockwidget.selectQGroup.currentIndexChanged.connect(get_qualities)
		self.dockwidget.selectQ.currentIndexChanged.connect(self.dockwidget.getF)
		get_delfactors = lambda : self.dockwidget.getQ('gyf_areas', self.dockwidget.selectYGroup, self.dockwidget.selectY, self.dockwidget.textY)
		self.dockwidget.selectYGroup.currentIndexChanged.connect(get_delfactors)
		self.dockwidget.selectY.currentIndexChanged.connect(self.dockwidget.getFY)

		self.dockwidget.approveButton.clicked.connect(self.dockwidget.setQ)
		self.dockwidget.removeButton.clicked.connect(self.dockwidget.removeQ)
		self.dockwidget.approveButton_2.clicked.connect(self.dockwidget.setY)
		self.dockwidget.removeButton_2.clicked.connect(self.dockwidget.removeY)

		self.dockwidget.setTableLabels(self.gyfModel)
		self.dockwidget.classtable.itemSelectionChanged.connect(self.dockwidget.highlightFeatures)
		self.dockwidget.areasTable.itemSelectionChanged.connect(self.dockwidget.highlightAreas)
		self.dockwidget.geometryButton.clicked.connect(self.openGeometryDialog)
		self.dockwidget.geometryButton_2.clicked.connect(self.openGeometryDialog)

		# Objects
		self.dockwidget.setLayers(self.dockwidget.selectLayer)
		self.dockwidget.setLayers(self.dockwidget.selectLayer_2)
		self.dockwidget.selectLayer.currentIndexChanged.connect(lambda : self.dockwidget.selectStart(self.dockwidget.selectLayer))
		self.dockwidget.selectLayer_2.currentIndexChanged.connect(lambda : self.dockwidget.selectStart(self.dockwidget.selectLayer_2))

		# Visualisation
		#self.dockwidget.createCheckBoxes(group_list)
		self.dockwidget.tabWidget.currentChanged.connect(self.createDataView)
		#self.dockwidget.tabWidget.currentChanged.connect(self.dockwidget.disableGroup)
		self.dockwidget.tabWidget.currentChanged.connect(self.dockwidget.switchLayerGroups)
		#self.dockwidget.groupList()

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
		layers = [layer for layer in self.proj.mapLayers().values()]
		names = []
		for l in layers:
			if l.isEditable():
				names.append(l.name())
		if names:
			QMessageBox.warning(ExportDialog(), 'Stäng redigeringsläge', 'Spara ändringar och gå ur redigeringsläget för att sätta punktyta/linjehöjd')
		else:
			self.geometry = GeometryDialog(self.dockwidget)

	def openSettingsDialog(self):
		self.settings = SettingsDialog(self.dockwidget, self.gyfModel, self.plugin_dir, self.layerSelectorDialog, None, self)
		self.settings.show()
		self.settings.okButton.clicked.connect(self.returnModel)
		print(self.gyfModel)
		self.settings.okButton.clicked.connect(self.settings.close)

	def returnModel(self):
		self.gyfModel = self.switch.defineGYF()

	def save(self):
		path = QFileDialog.getSaveFileName(self.iface.mainWindow(), 'Spara som', QSettings().value('dataPath'), '*.sqlite')
		new_path = path[0]
		database = self.proj.readEntry("QGYF", 'activeDataBase')[0]
		path = "{}/{}".format(self.proj.readEntry("QGYF", 'dataPath')[0], database)
		if path and new_path and os.path.exists(path):
			copyfile(path, new_path)



