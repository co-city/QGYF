'''
---------------------------------------------------------------------------
file_loader.py
Created on: 2019-03-28 08:23:28
FileLoader class
---------------------------------------------------------------------------
'''
import os
import sys
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QVariant, QSettings
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, QgsFields, QgsField, QgsGeometry, QgsPointXY
from qgis.utils import spatialite_connect, iface

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'attribute_selector.ui'))

class AttributeSelectorDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
      super(AttributeSelectorDialog, self).__init__(parent)
      self.setupUi(self)

    def load(self, attributes):
      self.attributes.addItems(attributes)

class FileLoader():

  def __init__(self, interface, layerSelectorDialog, path):
    self.interface = interface
    self.layerSelectorDialog = layerSelectorDialog
    self.path = path

  def loadFile(self):
    """
    Load file and add features to input layers of matching type (Point, Line, Polygon).
    @param {QtWidget} interface
    """
    file = QFileDialog.getOpenFileName(self.interface, 'Öppna fil', '', '*.shp; *.dxf')
    filePath = file[0]

    self.ignore_mappings = False
    self.fileName = os.path.basename(filePath)
    self.extension = os.path.splitext(self.fileName)[1]
    self.layer = QgsVectorLayer(filePath, self.fileName, "ogr")

    if self.extension == ".dxf":
      self.filter_attribute = "Layer"
      layers = []
      self.lookupLayers(self.layer.getFeatures(), layers)
      self.layerSelectorDialog.load(layers)
      self.layerSelectorDialog.show()
      self.layerSelectorDialog.okButton.clicked.connect(self.importToMap)

    if self.extension == ".shp":
      self.filter_attribute = "typkod"
      self.attributeSelectorDialog = AttributeSelectorDialog()
      attributes = self.lookupAttributes(self.layer)
      self.attributeSelectorDialog.load(attributes)
      self.attributeSelectorDialog.show()

      self.attributeSelectorDialog.okButton.clicked.connect(self.shapeAttributeSelected)

  def shapeAttributeSelected(self):

    attribute_name = self.attributeSelectorDialog.attributes.currentText()
    self.filter_attribute = attribute_name
    self.attributeSelectorDialog.close()

    if self.filter_attribute == "klassificera manuellt":
      self.ignore_mappings = True
      self.importToMap()
    else:
      layers = []
      self.lookupLayers(self.layer.getFeatures(), layers)
      self.layerSelectorDialog.load(layers)
      self.layerSelectorDialog.show()
      self.layerSelectorDialog.okButton.clicked.connect(self.importToMap)

  def importToMap(self):

    filters = []
    classifications = []

    if not self.ignore_mappings:
      for mapping in self.layerSelectorDialog.addedMappings:
        values = mapping.split(">")
        layerName = values[0].strip()
        if (len(values) == 2):
          classifications.append((values[0].strip(), values[1].strip()))
        filters.append(layerName)
      self.loadFeatures(filters, classifications)
    else:
      self.loadFeatures(None, None)

    self.layerSelectorDialog.close()

  def loadFeatures(self, filters, classifications):
    try:
      pointLayer = QgsProject.instance().mapLayersByName("Punktobjekt")[0]
      lineLayer = QgsProject.instance().mapLayersByName("Linjeobjekt")[0]
      polygonLayer = QgsProject.instance().mapLayersByName("Ytobjekt")[0]

      pointLayer.startEditing()
      lineLayer.startEditing()
      polygonLayer.startEditing()

      for feature in self.layer.getFeatures():
        try:
          type = self.prepareFeature(feature)
          if type == "Point":
            self.addFeature(feature, type, pointLayer, filters, classifications)
          if type == "Line":
            self.addFeature(feature, type, lineLayer, filters, classifications)
          if type == "Polygon":
            self.addFeature(feature, type, polygonLayer, filters, classifications)
        except:
          self.msg = QMessageBox()
          self.msg.setIcon(QMessageBox.Information)
          self.msg.setWindowTitle("Importfel")
          self.msg.setText("Filen innehåller vissa objekt som inte går att importera.")
          self.msg.show()

      pointLayer.commitChanges()
      lineLayer.commitChanges()
      polygonLayer.commitChanges()

      iface.mapCanvas().zoomToFullExtent()
    except:
      self.msg = QMessageBox()
      self.msg.setIcon(QMessageBox.Information)
      self.msg.setWindowTitle("Importfel")
      self.msg.setText("Nödvändiga kartlager saknas. Ladda in databasen på nytt.")
      self.msg.show()

  def addFeature(self, feature, type, layer, filters, classifications):
    """
    Convert attributes and add features to input layer.
    @param {QgsFeature} feature
    @param {string} type
    @param {QgsVectorLayer} layer
    @param {list} filters
    @param {list} classifications
    """
    index = feature.fields().indexFromName(self.filter_attribute)
    layer_name = str(feature.attributes()[index])
    try:
      layer_name = layer_name.encode("windows-1252").decode("utf-8")
    except:
      layer_name = layer_name

    if not filters or any(layer_name in filtr for filtr in filters):
      fields = QgsFields()
      fields.append(QgsField("id", QVariant.Int, "serial"))
      fields.append(QgsField("filnamn", QVariant.String, "text"))
      fields.append(QgsField("beskrivning", QVariant.String, "text"))

      feature.setFields(fields, True)
      feature.setAttributes([None, self.fileName, layer_name])
      layer.addFeature(feature)

      if classifications:
        classification = list(filter(lambda classification: classification[0] == layer_name, classifications))
        features = sorted(list(layer.getFeatures()), key=lambda feature: feature.attributes()[feature.fields().indexFromName("id")])
        inserted_feature = features[len(features) - 1]
        if classification:
          self.insertQuality(classification, inserted_feature)

  def prepareFeature(self, feature):

    geom = feature.geometry()
    geom.convertToSingleType()
    feature.setGeometry(geom)

    type = QgsWkbTypes.geometryDisplayString(geom.type())

    if type == "Polygon":
      geom = feature.geometry().fromPolygonXY(feature.geometry().asPolygon())
      feature.setGeometry(geom)

    if type == "Point":
      geom = feature.geometry().fromPointXY(feature.geometry().asPoint())
      feature.setGeometry(geom)

    if type == "Line":
      if self.extension == ".dxf":
        vertices = []
        for v in geom.vertices():
          vertices.append(QgsPointXY(v.x(), v.y()))

        if vertices[0] == vertices[len(vertices) - 1]:
          geom = QgsGeometry.fromPolygonXY([vertices])

      type = QgsWkbTypes.geometryDisplayString(geom.type())

      if type == "Polygon":
        feature.setGeometry(geom)

      if type == "Line":
        geom = feature.geometry().fromPolylineXY(feature.geometry().asPolyline())
        feature.setGeometry(geom)

    return type

  def insertQuality(self, classification, feature):
    con = spatialite_connect("{}\{}".format(QSettings().value('dataPath'), QSettings().value('activeDataBase')))
    cur = con.cursor()

    geometry_type = QgsWkbTypes.geometryDisplayString(feature.geometry().type())
    if (geometry_type == "Point"):
      geometry_type = "punkt"
      yta = 25.0
    if (geometry_type == "Line"):
      geometry_type = "linje"
      yta = feature.geometry().length()
    if (geometry_type == "Polygon"):
      geometry_type = "yta"
      yta = feature.geometry().area()

    #index = feature.fields().indexFromName("id")
    feature_id = feature["id"]
    print(feature_id)
    quality_name = classification[0][1]

    q_list = self.layerSelectorDialog.qualities_list
    factor = -1
    group_name = None

    # try to find mathing quality
    r = list(filter(lambda q: q[1][1] == quality_name, q_list))
    if len(r) == 0:
      # try to find mathing group
      r = list(filter(lambda q: q[1][0] == quality_name, q_list))
      if len(r) > 0:
        factor = r[0][1][4]
        group_name = r[0][1][0]
    else:
      factor = r[0][1][3]
      group_name = r[0][1][0]

    if factor != 1:
      data = [None, geometry_type, self.fileName, feature_id, group_name, quality_name, factor, round(yta, 1), round(factor*yta, 1)]
      # id, geometri_typ, filnamn, id_ini, grupp, kvalitet, faktor, yta, poäng
      print(data)
      cur.execute('INSERT INTO classification VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data)

    cur.close()
    con.commit()
    con.close()

  def lookupAttributes(self, layer):
    features = list(layer.getFeatures())
    if len(features) > 0:
      attributes = list(map(lambda field: field.name(), features[0].fields()))
    attributes.insert(0, "klassificera manuellt")
    return attributes

  def lookupLayers(self, features, layers):
    """
    Lookup features layername and append to the layer list if it´s a new one.
    @param {QgsFeature} feature
    @param {list<str>} layers
    """
    for feature in features:
      index = feature.fields().indexFromName(self.filter_attribute)
      layer = feature.attributes()[index]
      if isinstance(layer, str):
        try:
          layer = layer.encode("windows-1252").decode("utf-8")
        except:
          layer = layer
      if layer not in layers:
        layers.append(layer)