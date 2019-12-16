"""
---------------------------------------------------------------------------
map_export.py
Created on: 2019-04-09 10:20:53
---------------------------------------------------------------------------
"""

from PyQt5.QtXml import QDomDocument
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject, QgsVectorLayer, QgsLayout, QgsReadWriteContext, QgsLayoutItemPicture, QgsLayoutTable, QgsLayoutMultiFrame, QgsLayoutFrame
from qgis.core import QgsLayoutItemLabel, QgsLayoutItemMap, QgsLayoutItemLegend, QgsLayoutExporter, QgsLayerTree, QgsDataSourceUri, QgsMapLayer
from qgis.utils import iface
from ..ui.export import ExportDialog
import os
import sip
import datetime

class ExportCreator:

    def exportPDF(self, model, chart_path, gyf, exportDialog, area_id, groups, feature_gids, total):

        # Text from export dialog
        map_title = exportDialog.projectName.text()
        area_name = exportDialog.areaName.text()
        output_path = exportDialog.pdfPath.text()
        output_name = exportDialog.pdfName.text()
        author = exportDialog.author.text()
        gyf_version = model['Version'] #AP 2.0
        date = datetime.datetime.today().strftime('%Y-%m-%d')

        # Get template
        path = os.path.dirname(os.path.realpath(__file__))
        a = path.rfind('\\')
        template_file = open(path[:a] + "/template/qgyf_template1.qpt", encoding="utf-8")
        template_content = template_file.read()
        template_file.close()

        document = QDomDocument()
        proj = QgsProject.instance()
        document.setContent(template_content)
        composition = QgsLayout(proj)
        composition.loadFromTemplate(document, QgsReadWriteContext())

        # Title
        title = sip.cast(composition.itemById("title"), QgsLayoutItemLabel)
        title.setText(map_title)
        title = sip.cast(composition.itemById("title1"), QgsLayoutItemLabel)
        title.setText(map_title)
        title = sip.cast(composition.itemById("title2"), QgsLayoutItemLabel)
        title.setText(map_title)

        # GYF value
        value = sip.cast(composition.itemById("gyf_value"), QgsLayoutItemLabel)
        value.setText('GYF  ' + gyf)
        value = sip.cast(composition.itemById("gyf_value1"), QgsLayoutItemLabel)
        value.setText('GYF  ' + gyf)
        value = sip.cast(composition.itemById("gyf_value2"), QgsLayoutItemLabel)
        value.setText('GYF  ' + gyf)

        # GYF groups
        groups = sorted(list(set(groups)))
        groupList = sip.cast(composition.itemById("groups"), QgsLayoutItemLabel)
        text = '''<font face="tahoma" color="#238973"><h3>GYF Kategorier:</h3></font>
        <p style="font-family:tahoma; font-size:13.5; font-color:#4d4949; line-height:21px">'''
        for g in groups:
            text += g + '<br>'
        text = text + '</p>'
        groupList.setText(text)

        # Research Area
        area_id = area_id.id()
        research_area_lyr = proj.mapLayersByName('Beräkningsområde')[0]
        query = "id = " + str(area_id)
        research_area_lyr.setSubsetString(query)
        for feature in research_area_lyr.getFeatures():
            s = feature['yta']
        area_info = sip.cast(composition.itemById("area_info"), QgsLayoutItemLabel)
        items = [['Beräkningsyta: ', str(int(float(s)))], ['Ekoeffektiv yta: ', str(int(float(total)))]]
        text2 = ""
        for i in items:
            text2 += '<font face="tahoma" color="#238973"><b>'+ i[0] + \
            '</b></font><p style="display:inline;font-family:tahoma; font-size:13.5; font-color:#4d4949; line-height:19px">''' + \
            i[1] + ' m<sup>2</sup></p><br>'
        area_info.setText(text2)
        extent = research_area_lyr.extent()

        # Map
        main_map = sip.cast(composition.itemById("map"), QgsLayoutItemMap)
        main_map.zoomToExtent(extent)
        composition.itemById("map").refresh()
        main_map.setKeepLayerSet(True)
        main_map.setKeepLayerStyles(True)

        # Legend
        legend = sip.cast(composition.itemById("legend"), QgsLayoutItemLegend)
        legend.setLegendFilterByMapEnabled(True)
        # Remove background map from legend - have to be checked out
        #root = QgsLayerTree()
        #for lyr in iface.mapCanvas().layers():
        #    if lyr.type() == QgsMapLayer.VectorLayer:
        #        root.addLayer(lyr)
        #    legend.model().setRootGroup(root)
        legend.setAutoUpdateModel(False)

        # Table Grundytor & Kvaliteter
        root = proj.layerTreeRoot()
        content = [l.name() for l in root.children()]
        
        db_path = '{}\{}'.format(proj.readEntry("QGYF", "dataPath")[0], proj.readEntry("QGYF", 'activeDataBase')[0])
        uri = QgsDataSourceUri()
        uri.setDatabase(db_path)
        #Table 2 - ground areas 
        uri.setDataSource('', 'ground_areas', None)
        table2 = QgsVectorLayer(uri.uri(), 'ground_areas', 'spatialite')
        if 'ground_areas' not in content:
            proj.addMapLayer(table2, False)
        tableLayout2 = sip.cast(composition.itemById("table2"), QgsLayoutFrame)
        tableLayout2.refreshItemPosition()
        tableLayout2 = tableLayout2.multiFrame()
        tableLayout2.setVectorLayer(table2)
        tableLayout2.setDisplayedFields(['ytgrupp', 'ytklass', 'faktor', 'yta', 'poang'])
        # label
        table_areas = sip.cast(composition.itemById("table_areas"), QgsLayoutItemLabel)
        table2_name = '<font face="tahoma" color="#238973"><b>'+ model['Klass_items'][0].title() + 'er</b></font>'
        table_areas.setText(table2_name)
        #h = tableLayout2.totalHeight()
        
        #Table 1 - qualities
        uri.setDataSource('', 'classification', None)
        table1 = QgsVectorLayer(uri.uri(), 'classification', 'spatialite')
        if 'classification' not in content:
            proj.addMapLayer(table1, False)

        tableLayout = sip.cast(composition.itemById("table"), QgsLayoutFrame)
        #position = tableLayout.positionAtReferencePoint(tableLayout.ReferencePoint())
        #position.setX(position.x() + h)
        #tableLayout.setReferencePoint(position)
        tableLayout.refreshItemPosition()
        tableLayout = tableLayout.multiFrame()
        tableLayout.setVectorLayer(table1)
        tableLayout.setDisplayedFields(['id', 'geometri_typ', 'fil_namn', 'grupp', 'kvalitet', 'faktor', 'yta', 'poang'])
        # Filter
        feature_gids = "', '".join(i for i in feature_gids)
        query = "gid in ('"+ feature_gids +"')"
        tableLayout.setFilterFeatures(True)
        tableLayout.setFeatureFilter(query)
        tableLayout.update()
         # label
        table_class = sip.cast(composition.itemById("table_class"), QgsLayoutItemLabel)
        table1_name = '<font face="tahoma" color="#238973"><b>'+ model['Klass_items'][1].title() + 'er</b></font>'
        table_class.setText(table1_name)


        # Diagram
        chart = sip.cast(composition.itemById("chart"), QgsLayoutItemPicture)
        chart.setPicturePath(chart_path)
        chart.refreshPicture()

        # Diagram
        chart2 = sip.cast(composition.itemById("chart2"), QgsLayoutItemPicture)
        if float(gyf) > 0.0:
            chart2.setPicturePath(proj.readEntry("QGYF", "dataPath")[0] + '\PieChart2.png')
            chart2.refreshPicture()

        # Metadata
        text = '<p style="font-family:tahoma; font-size:13.5; font-color:#4d4949; line-height:21px">Område: ' + \
        area_name + '<br>Utförd av: ' + author + '<br>GYF version: ' + gyf_version + '<br>Datum: ' + date + '</p>'
        info = sip.cast(composition.itemById("info"), QgsLayoutItemLabel)
        info.setText(text)
        info = sip.cast(composition.itemById("info1"), QgsLayoutItemLabel)
        info.setText(text)

        # EXPORT!
        QgsLayoutExporter(composition).exportToPdf(output_path + '/' + output_name, QgsLayoutExporter.PdfExportSettings())
        QMessageBox.information(ExportDialog(), 'Rapport', 'Din rapport har skapats! :)')

        # Reset map view
        research_area_lyr.setSubsetString('')
        proj.removeMapLayer(table1)
        proj.removeMapLayer(table2)