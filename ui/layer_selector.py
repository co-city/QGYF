'''
---------------------------------------------------------------------------
layer_selector.py
Created on: 2019-03-26 08:23:28
Dialog LayerSelectorDialog
---------------------------------------------------------------------------
'''
import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtGui import QStandardItem
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox
from qgis.utils import spatialite_connect

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer_selector.ui'))

class LayerSelectorDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, model_gyf, parent=None):
        super(LayerSelectorDialog, self).__init__(parent)
        self.setupUi(self)

        for n, t in enumerate(model_gyf['Klass_items']):
            self.tabWidget.setTabText(n,t)

        self.addButton.clicked.connect(lambda : self.addToImport(self.classifications_2, 0))
        self.tabWidget.currentChanged.connect(self.switchImport)
        self.removeButton.clicked.connect(self.removeFromImport)
        self.layerAbort.clicked.connect(self.abortLayerSelection)
        self.qualityAbort.clicked.connect(self.abortQualitySelection)

        self.importsModel = QStandardItemModel()
        self.importItems.setModel(self.importsModel)
        self.addedMappings = []
        self.addedLayers = []

    def switchImport(self):
        self.abortQualitySelection()
        if self.tabWidget.currentIndex() == 0:
            self.addButton.disconnect()
            self.addButton.clicked.connect(lambda : self.addToImport(self.classifications_2, 0))
        else:
            self.addButton.disconnect()
            self.addButton.clicked.connect(lambda : self.addToImport(self.classifications, 1))

    def closeEvent(self, event):
        self.reset()

    def reset(self):
        self.layers.setModel(None)
        self.importsModel.clear()
        self.addedMappings = []
        self.addedLayers = []

    def abortLayerSelection(self):
        self.layers.selectionModel().clear()

    def abortQualitySelection(self):
        self.classifications.selectionModel().clear()
        self.classifications_2.selectionModel().clear()

    def removeFromImport(self):
        import_indexes = self.importItems.selectedIndexes()
        if len(import_indexes) > 0:
            data = import_indexes[0].data()
            row = import_indexes[0].row()

            self.importsModel.removeRows(row, 1)
            self.addedLayers.remove(data)
            self.addedMappings.remove(data)

    def addToImport(self, items_list, n):
        layers_list = self.layers

        classification_indexes = items_list.selectedIndexes()
        classification = None
        for index in classification_indexes:
            classification = index.data().split(",")[0]

        layers_indexes = layers_list.selectedIndexes()
        layer = None
        for index in layers_indexes:
            layer = index.data()

        if layer:
            if classification:
                item = layer + " > " + self.tabWidget.tabText(n) + ' : ' + classification
                digit_check = list(filter(str.isdigit, classification))
            else:
                item = layer
                digit_check = 1
            if digit_check or (self.classifications.selectedIndexes() and QSettings().value('model') == r"GYF AP, C/O City"):

                if self.classifications_2.selectedIndexes():
                    check = layer + " > " + self.tabWidget.tabText(0)
                    if not any(check in addedLayer for addedLayer in self.addedLayers):
                        self.addedLayers.append(item)
                        self.addedMappings.append(item)
                        self.importsModel.appendRow(QStandardItem(item))
                else:
                    if not any(item == addedLayer for addedLayer in self.addedLayers):
                        self.addedLayers.append(item)
                        self.addedMappings.append(item)
                        self.importsModel.appendRow(QStandardItem(item))
                

    def loadClassifications(self, path):
        classifications_list = self.classifications
        areas_list = self.classifications_2
        con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))

        cur = con.cursor()
        cur.execute("""
            SELECT DISTINCT grupp, kvalitet, namn, gyf_quality.faktor AS k_faktor, gyf_qgroup.faktor AS g_faktor
            FROM gyf_quality
            LEFT JOIN gyf_qgroup
            ON gyf_qgroup.id = grupp_id""")

        qualities = cur.fetchall()
        self.qualities_list = list(enumerate(qualities, 0))
        model = QStandardItemModel(classifications_list)

        for i, fields in self.qualities_list:
            if i == 0:
                item = QStandardItem(self.qualities_list[i][1][0])
                model.appendRow(item)

            item = QStandardItem(fields[1] + ", " + fields[2])
            model.appendRow(item)

            if (i < len(self.qualities_list) - 1):
                if self.qualities_list[i][1][0] != self.qualities_list[i + 1][1][0]:
                    item = QStandardItem("")
                    model.appendRow(item)
                    item = QStandardItem(self.qualities_list[i + 1][1][0])
                    model.appendRow(item)

        classifications_list.setModel(model)

        cur.execute("""SELECT DISTINCT grupp, kvalitet, namn, faktor FROM gyf_areas""")

        areas = cur.fetchall()
        self.areas_list = list(enumerate(areas, 0))
        model2 = QStandardItemModel(areas_list)

        for i, fields in self.areas_list:
            if i == 0:
                item = QStandardItem(self.areas_list[i][1][0])
                model2.appendRow(item)

            item = QStandardItem(fields[1] + ", " + fields[2])
            model2.appendRow(item)

            if (i < len(self.areas_list) - 1):
                if self.areas_list[i][1][0] != self.areas_list[i + 1][1][0]:
                    item = QStandardItem("")
                    model2.appendRow(item)
                    item = QStandardItem(self.areas_list[i + 1][1][0])
                    model2.appendRow(item)

        areas_list.setModel(model2)

        cur.close()
        con.close()

    def load(self, layers):
        layers_list = self.layers
        model = QStandardItemModel(layers_list)
        for layer in layers:
            item = QStandardItem(str(layer))
            model.appendRow(item)

        layers_list.setModel(model)