
from PyQt5.QtXml import QDomDocument
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsLayout, QgsReadWriteContext, QgsLayoutItemPicture, QgsLayoutItemAttributeTable
from qgis.core import QgsLayoutItemLabel, QgsLayoutItemMap, QgsLayoutItemLegend, QgsLayoutExporter, QgsLayerTree
from qgis.utils import iface
from ..ui.export import ExportDialog
import os
import sip
import datetime

class ExportCreator:
        
    def exportPDF(self, chart_path, gyf, exportDialog, area_id):
        
        map_title = exportDialog.projectName.text()
        print(map_title)
        area_name = exportDialog.areaName.text()
        output_folder = r'C:\Users\SEEM20099\Documents\QGYF' ## SET!
        author = exportDialog.author.text()
        gyf_version = 'GYF AP 2.0'
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        extent = iface.mapCanvas().extent() #zoom to research_area
        
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

        #Accessing the legend
        legend = sip.cast(composition.itemById("legend"), QgsLayoutItemLegend)
        legend.setLegendFilterByMapEnabled(True)
        '''root = QgsLayerTree()
        for lyr in iface.mapCanvas().layers():
            if lyr.name() != 'Unwanted layer':  
                root.addLayer(lyr)
            legend.model().setRootGroup(root)'''
            
        
        legend.setAutoUpdateModel(False)

        # Table
        #table = sip.cast(composition.itemById("table"), QgsLayoutItemTable)
        #table 

        #Accessing the diagram
        chart = sip.cast(composition.itemById("chart"), QgsLayoutItemPicture)
        chart.setPicturePath(chart_path)
        chart.refreshPicture()

        #Accessing the metadata
        info = sip.cast(composition.itemById("info"), QgsLayoutItemLabel)
        text = 'Område: ' + area_name + '\nUtförd av: ' + author + '\nGYF version: ' + gyf_version + '\nDatum: ' + date
        info.setText(text)

        QgsLayoutExporter(composition).exportToPdf(output_folder + "/qgyf_output.pdf", QgsLayoutExporter.PdfExportSettings())
        QMessageBox.information(ExportDialog(), 'Rapport', 'Din rapport har skapats! :)')