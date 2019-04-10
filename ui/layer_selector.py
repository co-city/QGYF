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
    def __init__(self, parent=None):
        super(LayerSelectorDialog, self).__init__(parent)
        self.setupUi(self)

        self.addButton.clicked.connect(self.addToImport)
        self.removeButton.clicked.connect(self.removeFromImport)
        self.layerAbort.clicked.connect(self.abortLayerSelection)
        self.qualityAbort.clicked.connect(self.abortQualitySelection)

        self.importsModel = QStandardItemModel()
        self.importItems.setModel(self.importsModel)
        self.addedMappings = []
        self.addedLayers = []

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

    def removeFromImport(self):
        import_indexes = self.importItems.selectedIndexes()
        if len(import_indexes) > 0:
            data = import_indexes[0].data()
            row = import_indexes[0].row()
            values = data.split(">")
            layer = values[0].strip()

            self.importsModel.removeRows(row, 1)
            self.addedLayers.remove(layer)
            self.addedMappings.remove(data)

    def addToImport(self):
        classifications_list = self.classifications
        layers_list = self.layers

        classification_indexes = classifications_list.selectedIndexes()
        classification = None
        for index in classification_indexes:
            classification = index.data().split(",")[0]

        layers_indexes = layers_list.selectedIndexes()
        layer = None
        for index in layers_indexes:
            layer = index.data()

        if layer:
            if classification:
                item = layer + " > " + classification
            else:
                item = layer
            if not any(layer in addedLayer for addedLayer in self.addedLayers):
                self.addedLayers.append(layer)
                self.addedMappings.append(item)
                self.importsModel.appendRow(QStandardItem(item))

    def loadClassifications(self, path):
        classifications_list = self.classifications
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

        cur.close()
        con.close()

    def load(self, layers):
        layers_list = self.layers
        model = QStandardItemModel(layers_list)
        for layer in layers:
            item = QStandardItem(str(layer))
            model.appendRow(item)

        layers_list.setModel(model)