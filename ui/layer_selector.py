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
from qgis.utils import spatialite_connect

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'layer_selector.ui'))


class LayerSelectorDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(LayerSelectorDialog, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.addToImport)
        self.okButton.clicked.connect(self.importToMap)

        self.importsModel = QStandardItemModel()
        self.importItems.setModel(self.importsModel)
        self.addedMappings = []
        self.addedLayers = []

    def importToMap(self):
        print("Import selected items to map")
        return self.addedMappings

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

        if classification and layer:
            item = layer + " > " + classification
            if not any(layer in addedLayer for addedLayer in self.addedLayers):
                self.addedLayers.append(layer)
                self.addedMappings.append(item)
                self.importsModel.appendRow(QStandardItem(item))

    def loadClassifications(self, path):
        classifications_list = self.classifications
        con = spatialite_connect(path + r'\qgyf.sqlite')

        cur = con.cursor()
        cur.execute("""
            SELECT DISTINCT grupp, kvalitet, namn
            FROM gyf_quality
            LEFT JOIN gyf_qgroup
            ON gyf_qgroup.id = grupp_id""")

        qualities = cur.fetchall()
        qualities_list = list(enumerate(qualities, 0))
        model = QStandardItemModel(classifications_list)

        for i, fields in qualities_list:
            if i == 0:
                item = QStandardItem(qualities_list[i][1][0])
                model.appendRow(item)

            item = QStandardItem(fields[1] + ", " + fields[2])
            model.appendRow(item)

            if (i < len(qualities_list) - 1):
                if qualities_list[i][1][0] != qualities_list[i + 1][1][0]:
                    item = QStandardItem("")
                    model.appendRow(item)
                    item = QStandardItem(qualities_list[i + 1][1][0])
                    model.appendRow(item)

        classifications_list.setModel(model)

        cur.close()
        con.close()

    def load(self, layers):
        layers_list = self.layers
        model = QStandardItemModel(layers_list)
        for layer in layers:
            item = QStandardItem(layer)
            model.appendRow(item)

        layers_list.setModel(model)