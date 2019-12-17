'''
---------------------------------------------------------------------------
file_loader.py
Created on: 2019-03-28 08:23:28
FileLoader class
---------------------------------------------------------------------------
'''
import os
import sys
import re
import uuid
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QVariant
from qgis.core import QgsProject, QgsVectorLayer, QgsWkbTypes, QgsFields, QgsField, QgsGeometry, QgsPointXY, QgsRectangle
from qgis.utils import spatialite_connect, iface
from .ground_areas import GroundAreas

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'attribute_selector.ui'))

class AttributeSelectorDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
      super(AttributeSelectorDialog, self).__init__(parent)
      self.setupUi(self)

    def load(self, attributes):
      self.attributes.addItems(attributes)

class FileLoader():

  def __init__(self, interface, layerSelectorDialog, dockwidget):
    self.interface = interface
    self.layerSelectorDialog = layerSelectorDialog
    self.proj = QgsProject.instance()
    
    self.layerSelectorDialog.okButton.clicked.connect(self.importToMap)
    self.layerSelectorDialog.okButton.clicked.connect(lambda : self.updateDockwidget(dockwidget))

  def updateDockwidget(self, dockwidget):
    if dockwidget:
      dockwidget.showClass()
      dockwidget.showAreas()

  def loadFile(self):
    """
    Load file and add features to input layers of matching type (Point, Line, Polygon).
    @param {QtWidget} interface
    """
    file = QFileDialog.getOpenFileName(self.interface, 'Öppna fil', self.proj.readEntry("QGYF", "dataPath")[0], '*.shp; *.dxf')
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

  def importToMap(self):

    filters = []
    areas = []
    classifications = []

    if not self.ignore_mappings:
      for mapping in self.layerSelectorDialog.addedMappings:
        values = re.split(' > | : ', mapping)
        layerName = values[0].strip()
        if (len(values) == 3):
          if values[1].strip() == self.layerSelectorDialog.tabWidget.tabText(0):
            areas.append((values[0].strip(), values[2].strip()))
          else:
            classifications.append((values[0].strip(), values[2].strip()))
        filters.append(str(layerName))
      filters = list(set(filters))
      print('Filters: ' + str(filters))
      print('Classifications: ' + str(classifications))
      print('Areas: ' + str(areas))
      self.loadFeatures(filters, classifications)
      if areas:
        self.loadAreas(areas)
    else:
      self.loadFeatures(None, None)

    self.layerSelectorDialog.close()
    
  def loadAreas(self, areas):
    #try:
    geometry_list = []
    area_list = []
    attr = []

    for feature in self.layer.getFeatures():
      #try:
      ftype = self.prepareFeature(feature)
      if ftype == "Point":
        area = 25.0
        radius = round((area/3.14159)**0.5, 2)
        geom = feature.geometry().buffer(radius, 20)
        feature.setGeometry(geom)
      if ftype == "Line":
        area = feature.geometry().length()
        geom = feature.geometry().buffer(0.5, 20)
        feature.setGeometry(geom)
      if ftype == "Polygon":
        area = feature.geometry().area()
      
      a_list = self.layerSelectorDialog.areas_list
      index = feature.fields().indexFromName(self.filter_attribute)
      layer_name = feature.attributes()[index]

      if any(str(layer_name) in filtr for filtr in areas):
        geometry_list.append(feature.geometry().asWkt())
        area_list.append(area)
        f = 0.0
        group_name = None
        k = [i[1] for i in areas if i[0] == str(layer_name)][0]
        k, group_name, f = self.findQuality(a_list, k)
        attr.append([group_name, k, f])
      #except:
      #  QMessageBox.information(self.layerSelectorDialog, 'Importfel', '''Filen innehåller vissa objekt som inte går att importera.''')
    data = []
    for i,obj in enumerate(attr):
      data.append(obj + [round(area_list[i], 1), round(area_list[i]*obj[-1], 1), geometry_list[i]])

    crs = self.proj.readEntry("QGYF", "CRS")[0]

    con = spatialite_connect("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], self.proj.readEntry("QGYF", "activeDataBase")[0]))
    cur = con.cursor()
    cur.executemany('''INSERT INTO ga_template VALUES 
      (NULL,?,?,?,?,?, CastToMultiPolygon(GeomFromText(?, ''' + crs + ''')))''', data)

    print('I come in into function')

    GroundAreas().mergeGA(cur)
    con.commit()
    cur.close()
    con.close()

    #except:
    #  QMessageBox.information(self.layerSelectorDialog, 'Importfel', '''Nödvändiga kartlager saknas. Ladda in databasen på nytt.''')

  def loadFeatures(self, filters, classifications):
    try:
      data = []
      pointLayer = self.proj.mapLayersByName("Punktobjekt")[0]
      lineLayer = self.proj.mapLayersByName("Linjeobjekt")[0]
      polygonLayer = self.proj.mapLayersByName("Ytobjekt")[0]
      pointLayer.startEditing()
      lineLayer.startEditing()
      polygonLayer.startEditing()

      for feature in self.layer.getFeatures():
        try:
          type = self.prepareFeature(feature)
          if type == "Point":
            area = 25.0
            data_feature = self.addFeature(feature, type, pointLayer, filters, classifications, area)
          if type == "Line":
            area = feature.geometry().length()
            data_feature = self.addFeature(feature, type, lineLayer, filters, classifications, area)
          if type == "Polygon":
            area = feature.geometry().area()
            data_feature = self.addFeature(feature, type, polygonLayer, filters, classifications, area)
          data.append(data_feature)
        except:
          QMessageBox.information(self.layerSelectorDialog, 'Importfel', '''Filen innehåller vissa objekt som inte går att importera.''')

      pointLayer.commitChanges()
      lineLayer.commitChanges()
      polygonLayer.commitChanges()
      iface.vectorLayerTools().stopEditing(pointLayer)
      iface.vectorLayerTools().stopEditing(lineLayer)
      iface.vectorLayerTools().stopEditing(polygonLayer)

      # Fill classification table
      data = [d for d in data if d is not None]
      data = [item for sublist in data for item in sublist]
      data = [d for d in data if d is not None]
      
      if data:
        con = spatialite_connect("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], self.proj.readEntry("QGYF", "activeDataBase")[0]))
        cur = con.cursor()
        cur.executemany('INSERT INTO classification VALUES (?, ?, ?, ?, ?, ?, ?, ?)', data)
        cur.close()
        con.commit()
        con.close()

      # Zoom to features
      extent = QgsRectangle()
      extent.setMinimal()
      root = self.proj.layerTreeRoot()
      group = root.findGroup("Klassificering")
      for child in group.children():
        extent.combineExtentWith(child.layer().extent())
      iface.mapCanvas().setExtent(extent)
      iface.mapCanvas().refresh()

    except:
      QMessageBox.information(self.layerSelectorDialog, 'Importfel', '''Nödvändiga kartlager saknas. Ladda in databasen på nytt.''')

  def addFeature(self, feature, type, layer, filters, classifications, area):
    """
    Convert attributes and add features to input layer.
    @param {QgsFeature} feature
    @param {string} type
    @param {QgsVectorLayer} layer
    @param {list} filters
    @param {list} classifications
    """
    index = feature.fields().indexFromName(self.filter_attribute)
    layer_name = feature.attributes()[index]
    data_feature = None

    try:
      layer_name = layer_name.encode("windows-1252").decode("utf-8")
    except:
      layer_name = layer_name

    if not filters or any(str(layer_name) in filtr for filtr in filters):
      fields = QgsFields()
      fields.append(QgsField("id", QVariant.Int, "serial"))
      fields.append(QgsField("gid", QVariant.String, "text"))
      fields.append(QgsField("filnamn", QVariant.String, "text"))
      fields.append(QgsField("beskrivning", QVariant.String, "text"))
      fields.append(QgsField("yta", QVariant.Double, "double"))
      gid = str(uuid.uuid4())

      feature.setFields(fields, True)
      feature.setAttributes([None, gid, self.fileName, layer_name, area])
      layer.addFeature(feature)

      if classifications:
        classification = list(filter(lambda classification: classification[0] == str(layer_name), classifications))
        if classification:
          data_feature = []
          for cl in classification:
            data_feature.append(self.insertQuality(cl, feature, gid, area))

    return data_feature

  def prepareFeature(self, feature):

    geom = feature.geometry()
    geom.convertToSingleType()
    feature.setGeometry(geom)

    type = QgsWkbTypes.geometryDisplayString(geom.type())

    if type == "Polygon":
      geom = feature.geometry().fromPolygonXY(feature.geometry().asPolygon())
      feature.setGeometry(geom)
      feature.geometry().makeValid()

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
        feature.geometry().makeValid()

      if type == "Line":
        geom = feature.geometry().fromPolylineXY(feature.geometry().asPolyline())
        feature.setGeometry(geom)

    return type

  def insertQuality(self, classification, feature, gid, yta):
    data = None
    geometry_type = QgsWkbTypes.geometryDisplayString(feature.geometry().type())
    if (geometry_type == "Point"):
      geometry_type = "punkt"
    if (geometry_type == "Line"):
      geometry_type = "linje"
    if (geometry_type == "Polygon"):
      geometry_type = "yta"

      quality_name = classification[1]

      q_list = self.layerSelectorDialog.qualities_list
      factor = -1
      group_name = None

      quality_name, group_name, factor = self.findQuality(q_list, quality_name)

      if factor != -1:
        data = [gid, geometry_type, self.fileName, group_name, quality_name, factor, round(yta, 1), round(factor*yta, 1)]
        # gid, geometri_typ, filnamn, grupp, kvalitet, faktor, yta, poäng

    return data

  def findQuality(self, q_list, quality_name):
    # try to find mathing quality
    r = list(filter(lambda q: q[1][1] == quality_name, q_list))
    if len(r) == 0:
      # try to find mathing group
      r = list(filter(lambda q: q[1][0] == quality_name, q_list))
      if len(r) > 0:
        factor = r[0][1][4]
        group_name = r[0][1][0]
        quality_name = ''
    else:
      factor = r[0][1][3]
      group_name = r[0][1][0]
      quality_name = quality_name
    return quality_name, group_name, factor

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
