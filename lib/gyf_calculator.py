from qgis.core import QgsProject, QgsVectorLayer, QgsApplication, QgsWkbTypes
from PyQt5.QtWidgets import QMessageBox
from ..ui.welcome import WelcomeDialog
import processing
import numpy as np

class GyfCalculator:
  def __init__(self, path):
    self.path = path

  def getFeatures(self):
    """
    Get features from given layers.
    @return {list} features
    """
    polygon_layer = QgsProject.instance().mapLayersByName("polygon_class")[0]
    line_layer = QgsProject.instance().mapLayersByName("line_class")[0]
    point_layer = QgsProject.instance().mapLayersByName("point_class")[0]
    # Clear visualisation filters if they were set
    polygon_layer.setSubsetString('')
    line_layer.setSubsetString('')
    point_layer.setSubsetString('')

    return [
      *list(polygon_layer.getFeatures()),
      *list(line_layer.getFeatures()),
      *list(point_layer.getFeatures())
    ]

  def calculateIntersectionArea(self, feature, intersector, with_factor):
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
        new_geom = feature.geometry().buffer(3, 20)
    if geometry_type == "Line":
        new_geom = feature.geometry().buffer(0.5, 20)

    if new_geom:
      intersection = new_geom.intersection(intersector.geometry())
    else:
      intersection = feature.geometry().intersection(intersector.geometry())

    index = feature.fields().indexFromName("faktor")
    factor = feature.attributes()[index]
    index2 = feature.fields().indexFromName("grupp")
    group = feature.attributes()[index2]
    index3 = feature.fields().indexFromName("id")
    feature_id = feature.attributes()[index3]

    if with_factor:
      return intersection.area() * factor, group, feature_id
    else:
      return intersection.area() #, group

  def calculate(self):
    """
    Calculate gyf factor.
    @return {number} gyf
    """
    research_area_layer = QgsProject.instance().mapLayersByName("Beräkningsområde")[0]
    selected_features = list(research_area_layer.selectedFeatures())
    gyf = 0
    factor_areas = []
    groups = []
    feature_ids = []
    selected_feature = None

    if list(selected_features):
      selected_feature = selected_features[0]
      features = self.getFeatures()

      calculation_area = selected_feature.geometry().area()
      feature_area_sum = 0
      feature_area_factor_sum = 0

      intersecting_features = []
      unique_features = []
      unique_id = []

      for feature in features:
        geom = feature.geometry()
        selected_geometry = selected_feature.geometry()
        # TODO: find a comparer to test intersection,
        # the intersection calculation is not necsessary if the feature is completely outside the calculation area.
        # if geom.overlaps(selected_geometry):
        intersecting_features.append(feature)

      for feature in intersecting_features:
        if not feature.attributes()[1] in unique_id:
          unique_id.append(feature.attributes()[1])
          unique_features.append(feature)

      for feature in unique_features:
        area = self.calculateIntersectionArea(feature, selected_feature, False)
        feature_area_sum += area
        '''if group_gb == 'Dagvatten- och skyfallshantering':
          feature_area_blue += area
        else:
          feature_area_green += area'''

      for feature in intersecting_features:
        factor_area, group, feature_id = self.calculateIntersectionArea(feature, selected_feature, True)
        feature_area_factor_sum += factor_area
        factor_areas.append(factor_area)
        groups.append(group)
        feature_ids.append(feature_id)

      # Get rid of features which don't actually intersect the currently selected feature
      factor_areas = np.asarray(factor_areas)
      groups = np.asarray(groups)
      feature_ids = np.asarray(feature_ids)
      nonzero_indexes = np.where(factor_areas != 0.0)
      factor_areas = factor_areas[nonzero_indexes]
      groups = groups[nonzero_indexes]
      feature_ids = feature_ids[nonzero_indexes]

      gyf = (feature_area_sum + feature_area_factor_sum) / calculation_area

    else:
      QMessageBox.warning(WelcomeDialog(), 'Inget beräkningsområde', 'Välj beräkningsområde för att beräkna GYF!')

    if type(factor_areas) == list:
      factor_areas = np.array([])

    return gyf, factor_areas, groups, feature_ids, selected_feature

