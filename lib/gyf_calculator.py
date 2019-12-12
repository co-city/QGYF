from qgis.core import QgsProject, QgsVectorLayer, QgsApplication, QgsWkbTypes, NULL
from qgis.utils import iface
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QSettings
from ..ui.welcome import WelcomeDialog
import numpy as np

class GyfCalculator:
  def __init__(self, path):
    self.path = path

  def getFeatures(self):
    """
    Get features from given layers.
    @return {list} features
    """
    polygon_layer = QgsProject.instance().mapLayersByName("Ytkvalitet")[0]
    line_layer = QgsProject.instance().mapLayersByName("Linjekvalitet")[0]
    point_layer = QgsProject.instance().mapLayersByName("Punktkvalitet")[0]
    # Clear visualisation filters if they were set
    polygon_layer.setSubsetString('')
    line_layer.setSubsetString('')
    point_layer.setSubsetString('')

    return [
      *list(polygon_layer.getFeatures()),
      *list(line_layer.getFeatures()),
      *list(point_layer.getFeatures())
    ]

  def calculateIntersectionArea(self, feature, intersector):
    """
    Calculate the instersection of two features, and optionally scale with given factor.
    @param {QgsFeature} feature
    @param {QgsFeature} intersector
    @param {bool} with_factor
    @return {list} features
    """
    geometry_type = QgsWkbTypes.geometryDisplayString(feature.geometry().type())
    new_geom = None
    if geometry_type == "Point":
      radius = round((feature["yta"]/3.14159)**0.5, 2)
      new_geom = feature.geometry().buffer(radius, 20)
    if geometry_type == "Line":
      new_geom = feature.geometry().buffer(0.5, 20)
      height = round(feature["yta"]/feature.geometry().length(), 1)

    if new_geom:
      intersection = new_geom.intersection(intersector.geometry())
    else:
      intersection = feature.geometry().intersection(intersector.geometry())

    factor = feature["faktor"]
    group = feature["grupp"]
    feature_id = feature["gid"]
    ground_area_add = []
    b_value_feature = feature["kvalitet"]

    if geometry_type == "Line":
      intersection_area = intersection.area() * height
      ground_area_add.append([intersection.area(), intersection_area])
    else:
      intersection_area = intersection.area()

    #print([feature["gid"], intersection_area, factor, intersection_area * factor])
    return intersection_area * factor, group, feature_id, b_value_feature, ground_area_add

  def calculateGroundAreaIntersection(self, intersector, ground_area_lines):
    "Calculate the intersection of ground areas and the research area"
    ground_layer = QgsProject.instance().mapLayersByName("Grundytor")
    if ground_layer:
      ground_layer = ground_layer[0]
    else:
      pathLayer = '{}\{}|layername={}'.format(QSettings().value("dataPath"), QSettings().value("activeDataBase"), 'ground_areas')
      ground_layer = QgsVectorLayer(pathLayer, 'Grundytor', "ogr")
    areas = list(ground_layer.getFeatures())
    area_value = 0
    b_value = []
    for area in areas:
      intersection = area.geometry().intersection(intersector.geometry())
      area_value += intersection.area()
      if intersection.area() > 0:
        b_value.append(area['ytklass'])
    if ground_area_lines:
      minus_area = sum([i[0] for i in ground_area_lines])
      plus_area = sum([i[1] for i in ground_area_lines])
      area_value = area_value - minus_area + plus_area
    
    return area_value, b_value

  def calculate(self):
    """
    Calculate gyf factor.
    @return {number} gyf
    """
    
    # Default values
    gyf = 0
    areas = []
    factor_areas = []
    groups = []
    feature_ids = []
    eco_area = 0
    feature_area_sum = 0
    selected_feature = None
    ground_area_lines = []
    b_value_features = []
    b_value = []

    research_area_layer = QgsProject.instance().mapLayersByName("Beräkningsområde")
    if research_area_layer:
      research_area_layer = research_area_layer[0]
      if research_area_layer.isEditable():
        iface.vectorLayerTools().stopEditing(research_area_layer)
      selected_features = list(research_area_layer.selectedFeatures())

      if list(selected_features):
        selected_feature = selected_features[0]
        features = self.getFeatures()

        calculation_area = selected_feature.geometry().area()
        feature_area_sum = 0
        feature_area_factor_sum = 0

        intersecting_features = [feature for feature in features if not feature.geometry().intersection(selected_feature.geometry()).isEmpty()]

        for feature in intersecting_features:
          factor_area, group, feature_id, b_value_feature, ground_area_add = self.calculateIntersectionArea(feature, selected_feature)
          feature_area_factor_sum += factor_area
          factor_areas.append(factor_area)
          groups.append(group)
          feature_ids.append(feature_id)
          b_value_features.append(b_value_feature)
          if ground_area_add:
            ground_area_lines += ground_area_add

        feature_area_sum, b_value_areas = self.calculateGroundAreaIntersection(selected_feature, ground_area_lines)
        print('Ground Area:' + str(feature_area_sum))
        print('Faktor Area:' + str(feature_area_factor_sum))
        
        eco_area = feature_area_sum + feature_area_factor_sum
        gyf = eco_area / calculation_area
        b_value = self.balancering(b_value_areas, b_value_features)
      else:
        QMessageBox.warning(WelcomeDialog(), 'Inget beräkningsområde', 'Välj beräkningsområde för att beräkna GYF!')

    else:
      QMessageBox.warning(WelcomeDialog(), 'Inget beräkningsområde', 'Lägg till lager med beräkningsområde för att beräkna GYF!')

    return gyf, factor_areas, groups, feature_ids, selected_feature, feature_area_sum, eco_area, b_value

  def balancering(self, list1, list2):
    values = list(set(list1 + list2))
    values = [v for v in values if v != NULL]
    print(values)
    B = len([i for i in values if 'B' in i])
    S = len([i for i in values if 'S' in i])
    K = len([i for i in values if 'K' in i])
    L = len([i for i in values if 'L' in i])
    balancering = [B, S, K, L]
    return balancering



