from qgis.core import QgsProject, QgsVectorLayer, QgsApplication, QgsWkbTypes
import processing

class GyfCalculator:
  def __init__(self, path):
    print("Gyf calcuclator")
    self.path = path

  def getFeatures(self):

    polygon_layer = QgsProject.instance().mapLayersByName("polygon_class")[0]
    line_layer = QgsProject.instance().mapLayersByName("line_class")[0]
    point_layer = QgsProject.instance().mapLayersByName("point_class")[0]

    return [
      *list(polygon_layer.getFeatures()),
      *list(line_layer.getFeatures()),
      *list(point_layer.getFeatures())
    ]

  def calculate(self):
    research_area_layer = QgsProject.instance().mapLayersByName("research_area")[0]
    selected_features = list(research_area_layer.selectedFeatures())
    if list(selected_features):
      selected_feature = selected_features[0]
      features = self.getFeatures()

      feature_area_sum = 0

      unique_features = []
      for feature in features:
        #if not any(feature.attributes()[1] == feature.attributes()[1] in unique_features):
        if not feature.attributes()[1] in unique_features:
          unique_features.append(feature)

      print("Unique", unique_features)

      for feature in features:
        geometry_type = QgsWkbTypes.geometryDisplayString(feature.geometry().type())
        new_geom = None
        if geometry_type == "Point":
            new_geom = feature.geometry().buffer(3, 20)
        if geometry_type == "Line":
            new_geom = feature.geometry().buffer(0.5, 20)

        if (new_geom):
          intersection = new_geom.intersection(selected_feature.geometry())
        else:
          intersection = feature.geometry().intersection(selected_feature.geometry())

        feature_area_sum += intersection.area()

        index = feature.fields().indexFromName("faktor")
        factor = feature.attributes()[index]

        # summa(feature.area) + summa(feature.area * faktor) / selected_feature.area
        print("Feature intersection area", intersection.area())


      print("Calculate!", features, selected_feature)