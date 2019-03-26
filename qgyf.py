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
from PyQt5.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from qgis.core import QgsProject, QgsVectorLayer
from qgis.gui import QgsFileWidget
from .resources import *

from .ui.qgyf_dockwidget import QGYFDockWidget
from .ui.welcome import WelcomeDialog
from .ui.layer_selector import LayerSelectorDialog
from .lib.db import Db
from .lib.qualityTable import QualityTab
from .lib.db_view import DbView
from .lib.fileLoader import loadFile

import os.path
import inspect

class QGYF:

	def __init__(self, iface):


		self.iface = iface
		self.plugin_dir = os.path.dirname(__file__)

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

		self.actions = []
		self.menu = self.translate(u'&QGYF')
		self.toolbar = self.iface.addToolBar(u'QGYF')
		self.toolbar.setObjectName(u'QGYF')
		self.pluginIsActive = False
		self.dockwidget = None

		self.path = os.path.expanduser('~') + r'\Documents\QGYF'
		self.initDatabase(self.path)
		self.addLayers(self.path, [
			"point_object",
			"line_object",
			"polygon_object",
			"research_area"
		])
		self.showWelcome()
		self.layerSelectorDialog = LayerSelectorDialog()
		self.layerSelectorDialog.loadClassifications(self.path)

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

	def load(self):
		loadFile(self.iface.mainWindow(), self.layerSelectorDialog)

	def info(self):
		self.welcome = WelcomeDialog()
		self.welcome.show()
		self.welcome.okButton.clicked.connect(self.welcome.close)

	def initGui(self):
		"""Create the menu entries and toolbar icons inside the QGIS GUI."""

		icon_path = ':/plugins/qgyf/assets/folder.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Ladda lager'),
			callback=self.load,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/tree.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Beräkna grönytefaktor'),
			callback=self.openCalculationDialog,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/edit_point.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Editera punktobjekt'),
			callback=self.info,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/edit_polyline.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Editera linjeobjekt'),
			callback=self.info,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/edit_polygon.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Editera ytobjekt'),
			callback=self.info,
			parent=self.iface.mainWindow())

		icon_path = ':/plugins/qgyf/assets/info.png'
		self.addAction(
			icon_path,
			text=self.translate(u'Vissa upp informationsfönstret'),
			callback=self.info,
			parent=self.iface.mainWindow())

	def addLayers(self, path, layers):
		for layer in layers:
			pathLayer = path + r"\qgyf.sqlite|layername=" + layer
			mapLayers = QgsProject.instance().mapLayersByName(layer)
			exists = len(mapLayers) > 0
			if not exists:
				vlayer = QgsVectorLayer(pathLayer, layer, "ogr")
				QgsProject.instance().addMapLayer(vlayer)
				root = QgsProject.instance().layerTreeRoot()

	def initDatabase(self, path):
		self.db = Db()
		self.db.create(path)
		self.quality = QualityTab()
		self.quality.init(path)

	def onClosePlugin(self):
		self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)
		# Remove this statement if dockwidget is to remain
		# for reuse if plugin is reopened
		self.pluginIsActive = False

	def unload(self):
		for action in self.actions:
			self.iface.removePluginMenu(
				self.translate(u'&QGYF'),
				action)
			self.iface.removeToolBarIcon(action)
		del self.toolbar

	def openCalculationDialog(self):
		"""Run method that loads and starts the plugin"""
		if not self.pluginIsActive:
			self.pluginIsActive = True

			# dockwidget may not exist if:
			#    first run of plugin
			#    removed on close (see self.onClosePlugin method)
			if self.dockwidget == None:

				# Create the dockwidget (after translation) and keep reference
				self.dockwidget = QGYFDockWidget()

				# connect to provide cleanup on closing of dockwidget
				self.dockwidget.closingPlugin.connect(self.onClosePlugin)

		self.dockwidget = QGYFDockWidget()
		# show the dockwidget
		self.iface.addDockWidget(Qt.RightDockWidgetArea, self.dockwidget)
		self.dockwidget.show()

		# Classification
		showClass = lambda : self.dockwidget.showClass(self.path)
		showClass()
		# Qualities
		self.dockwidget.selectQGroup.clear()
		self.dockwidget.chooseQ(self.path)
		getQ = lambda : self.dockwidget.getQ(self.path)
		self.dockwidget.selectQGroup.currentIndexChanged.connect(getQ)
		getF = lambda : self.dockwidget.getF(self.path)
		self.dockwidget.selectQ.currentIndexChanged.connect(getF)
		setQ = lambda : self.dockwidget.setQ(self.path)
		self.dockwidget.approveButton.clicked.connect(setQ)
		self.dockwidget.approveButton.clicked.connect(showClass)
		# Objects
		self.dockwidget.setLayers()
		self.dockwidget.selectObj.clicked.connect(self.dockwidget.selectStart)

		# Visualisation
		self.dbView = DbView()
		self.dbView.init(self.path)

		# Estimation of GYF
		# Research area
		self.dockwidget.selectRA.clicked.connect(self.dockwidget.selectArea)
		createArea = lambda : self.dockwidget.createArea(self.path)
		self.dockwidget.createRA.clicked.connect(createArea)