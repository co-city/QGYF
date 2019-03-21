import os
import sys
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QVariant
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, QgsFields, QgsField

def loadFile(interface):
  file = QFileDialog.getOpenFileName(interface, 'Öppna fil', '', '*.shp')
  filePath = file[0]
  fileName = os.path.basename(filePath)
  extension = os.path.splitext(fileName)[1]

  layer = QgsVectorLayer(filePath, fileName, "ogr")
  features = layer.getFeatures()

  for feature in features:
    geom = feature.geometry()
    print("Load", feature.geometry().type())
    geom.convertToSingleType()
    type = QgsWkbTypes.geometryDisplayString(geom.type())
    addFeature(feature, type, fileName)

def addFeature(feature, type, fileName):
  pointLayer = QgsProject.instance().mapLayersByName("point_object")[0]
  lineLayer = QgsProject.instance().mapLayersByName("line_object")[0]
  polygonLayer = QgsProject.instance().mapLayersByName("polygon_object")[0]

  fields = feature.fields()
  attributes = feature.attributes()
  print("Attributes", attributes)

  fields = QgsFields()
  fields.append(QgsField("id", QVariant.Int, "serial"))
  fields.append(QgsField("filnamn", QVariant.String, "text"))
  fields.append(QgsField("beskrivning", QVariant.String, "text"))

  feature.setFields(fields, True)
  feature.setAttributes([attributes[0], fileName, "beskrivning"])

  if type == "Point":
    pointLayer.addFeature(feature)
  if type == "Line":
    lineLayer.addFeature(feature)
  if type == "Polygon":
    print("Add", feature.geometry().type())
    polygonLayer.addFeature(feature)
