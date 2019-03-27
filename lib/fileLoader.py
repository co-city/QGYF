import os
import sys
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QVariant
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, QgsFields, QgsField, QgsGeometry, QgsPointXY

def loadFile(interface, layerSelectorDialog):
  """
  Load file and add features to input layers of matching type (Point, Line, Polygon).
  @param {QtWidget} interface
  """
  file = QFileDialog.getOpenFileName(interface, 'Öppna fil', '', '*.shp; *.dxf')
  filePath = file[0]
  fileName = os.path.basename(filePath)
  extension = os.path.splitext(fileName)[1]

  layer = QgsVectorLayer(filePath, fileName, "ogr")

  if extension == ".dxf":
    layers = []
    lookupLayers(layer.getFeatures(), layers)
    layerSelectorDialog.load(layers)
    layerSelectorDialog.show()

  pointLayer = QgsProject.instance().mapLayersByName("point_object")[0]
  lineLayer = QgsProject.instance().mapLayersByName("line_object")[0]
  polygonLayer = QgsProject.instance().mapLayersByName("polygon_object")[0]

  pointLayer.startEditing()
  lineLayer.startEditing()
  polygonLayer.startEditing()

  for feature in layer.getFeatures():
    try:
      type = prepareFeature(feature, extension)
      if type == "Point":
        addFeature(feature, type, fileName, pointLayer, extension)
      if type == "Line":
        addFeature(feature, type, fileName, lineLayer, extension)
      if type == "Polygon":
        addFeature(feature, type, fileName, polygonLayer, extension)
    except:
      print("Load error", feature)

  pointLayer.commitChanges()
  lineLayer.commitChanges()
  polygonLayer.commitChanges()

def addFeature(feature, type, fileName, layer, extension):
  """
  Convert attributes and add features to input layer.
  @param {QgsFeature} feature
  @param {string} type
  @param {string} fileName
  @param {QgsVectorLayer} layer
  """
  fields = QgsFields()
  fields.append(QgsField("id", QVariant.Int, "serial"))
  fields.append(QgsField("filnamn", QVariant.String, "text"))
  fields.append(QgsField("beskrivning", QVariant.String, "text"))

  feature.setFields(fields, True)
  feature.setAttributes([None, fileName, ""])
  layer.addFeature(feature)

def prepareFeature(feature, extension):

  geom = feature.geometry()
  geom.convertToSingleType()
  feature.setGeometry(geom)

  type = QgsWkbTypes.geometryDisplayString(geom.type())

  if type == "Polygon":
    geom = feature.geometry().fromPolygonXY(feature.geometry().asPolygon())
    feature.setGeometry(geom);

  if type == "Point":
    geom = feature.geometry().fromPointXY(feature.geometry().asPoint())
    feature.setGeometry(geom);

  if type == "Line":
    if extension == ".dxf":
      vertices = []
      for v in geom.vertices():
        vertices.append(QgsPointXY(v.x(), v.y()))

      if vertices[0] == vertices[len(vertices) - 1]:
        geom = QgsGeometry.fromPolygonXY([vertices])

    type = QgsWkbTypes.geometryDisplayString(geom.type())

    if type == "Polygon":
      feature.setGeometry(geom);

    if type == "Line":
      geom = feature.geometry().fromPolylineXY(feature.geometry().asPolyline())
      feature.setGeometry(geom);

  return type

def mapShapeAttributes(feature):
  return True

def lookupLayers(features, layers):
  """
  Lookup features layername and append to the layer list if it´s a new one.
  @param {QgsFeature} feature
  @param {list<str>} layers
  """
  for feature in features:
    index = feature.fields().indexFromName("Layer")
    layer = feature.attributes()[index]
    layer = layer.encode("windows-1252").decode("utf-8")
    if layer not in layers:
      layers.append(layer)