import os
import sys
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QVariant
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, QgsFields, QgsField

def loadFile(interface):
  """
  
  Load file and add features to input layers of matching type (Point, Line, Polygon)

  @param {QtWidget} interce
  """
  file = QFileDialog.getOpenFileName(interface, 'Öppna fil', '', '*.shp')
  filePath = file[0]
  fileName = os.path.basename(filePath)
  extension = os.path.splitext(fileName)[1]

  layer = QgsVectorLayer(filePath, fileName, "ogr")
  features = layer.getFeatures()

  pointLayer = QgsProject.instance().mapLayersByName("point_object")[0]
  lineLayer = QgsProject.instance().mapLayersByName("line_object")[0]
  polygonLayer = QgsProject.instance().mapLayersByName("polygon_object")[0]
  
  pointLayer.startEditing()
  lineLayer.startEditing()
  polygonLayer.startEditing()

  for feature in features:
    geom = feature.geometry()
    geom.convertToSingleType()
    feature.setGeometry(geom);
    type = QgsWkbTypes.geometryDisplayString(geom.type())
    if type == "Point":  
      addFeature(feature, type, fileName, pointLayer)  
    if type == "Line":    
      addFeature(feature, type, fileName, lineLayer)
    if type == "Polygon":    
      addFeature(feature, type, fileName, polygonLayer)

  pointLayer.commitChanges()
  lineLayer.commitChanges()
  polygonLayer.commitChanges()

def addFeature(feature, type, fileName, layer):
  """
  
  Convert attributes and add features to input layer.

  @param {QgsFeature} feature
  @param {string} type
  @param {string} fileName
  @param {QgsVectorLayer} layer
  """
  fields = feature.fields()
  attributes = feature.attributes()

  fields = QgsFields()
  fields.append(QgsField("id", QVariant.Int, "serial"))
  fields.append(QgsField("filnamn", QVariant.String, "text"))
  fields.append(QgsField("beskrivning", QVariant.String, "text"))

  feature.setFields(fields, True)
  feature.setAttributes([None, fileName, ""])

  layer.addFeature(feature)