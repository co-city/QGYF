
from PyQt5.QtXml import QDomDocument
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsLayout, QgsReadWriteContext, QgsLayoutItemPicture
from qgis.core import QgsLayoutItemLabel, QgsLayoutItemMap, QgsLayoutItemLegend, QgsLayoutExporter
from qgis.utils import iface
from ..ui.welcome import WelcomeDialog
import os
import sip
import datetime

class Export:

    def exportPDF(self, chart_path, gyf):
        map_title = 'GYF beräkning: Detaljplan TEST'
        output_folder = r'C:\Users\SEEM20099\Documents\QGYF' ## SET!
        author = 'EM'
        gyf_version = 'GYF AP 2.0'
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        extent = iface.mapCanvas().extent()
        
        
        
        path = os.path.dirname(os.path.realpath(__file__))
        a = path.rfind('\\')
        template_file = open(path[:a] + "/template/qgyf_template1.qpt", encoding="utf-8")
        template_content = template_file.read()
        template_file.close()
        
        document = QDomDocument()
        document.setContent(template_content)
        composition = QgsLayout(QgsProject.instance())
        composition.loadFromTemplate(document, QgsReadWriteContext())

        #Accessing the Title
        title = sip.cast(composition.itemById("title"), QgsLayoutItemLabel)
        title.setText(map_title)

        #Accessing GYF value
        value = sip.cast(composition.itemById("gyf_value"), QgsLayoutItemLabel)
        value.setText('GYF  ' + gyf)
        
        #Accessing the main map by recasting it as a QgsLayoutItemMap and not QgsLayoutItem
        main_map = sip.cast(composition.itemById("map"), QgsLayoutItemMap)
        main_map.zoomToExtent(extent)
        composition.itemById("map").refresh()
        main_map.setKeepLayerSet(True)
        main_map.setKeepLayerStyles(True)

        #Accessing the main legend by recasting it as a legend item
        legend = sip.cast(composition.itemById("legend"), QgsLayoutItemLegend)
        legend.setLegendFilterByMapEnabled(True)
        legend.setAutoUpdateModel(False)

        #Accessing the diagram
        chart = sip.cast(composition.itemById("chart"), QgsLayoutItemPicture)
        chart.setPicturePath(chart_path)
        chart.refreshPicture()

        #Accessing the metadata
        info = sip.cast(composition.itemById("info"), QgsLayoutItemLabel)
        text = 'Område: X\nUtförd av: ' + author + '\nGYF version: ' + gyf_version + '\nDatum:' + date
        info.setText(text)

        QgsLayoutExporter(composition).exportToPdf(output_folder + "/qgyf_output.pdf", QgsLayoutExporter.PdfExportSettings())
        QMessageBox.information(WelcomeDialog(), 'Rapport', 'Din rapport har skapats! :)')