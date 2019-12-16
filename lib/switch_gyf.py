# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------
switch_gyf.py
Created on: 2019-11-09 22:05:53
---------------------------------------------------------------------------
"""
import os
import os.path
from PyQt5.QtWidgets import QMessageBox
from qgis.core import QgsProject

from ..ui.layer_selector import LayerSelectorDialog
from ..ui.mplwidget import MplWidget
from .gyf_tables import QualityTable
from .db import Db


class SwitchGYFs:
    def __init__(self, dockwidget, plugin_dir):
        self.dockwidget = dockwidget
        self.plugin_dir = plugin_dir
        self.proj = QgsProject.instance()
        

    def defineGYF(self):
        gyf_var = [
            'Name',
            'Version',
            'Doc', 
            'Input_groups', 
            'Input_categories',
            'Input_ground_areas',
            'Ground_areas_enabled',
            'Tabs_labels',
            'Klass_items']

        gyf_ap = [
            r'GYF för allmän platsmark, C/O City',
            'GYF AP 2.0',
            'gyf_ap.pdf',
            'gyf_AP_groups.txt', 
            'gyf_AP_qualities.txt',
            'gyf_AP_groundareas.txt',
            0,
            ['Grundytor','Klassificera', 'Visualisera', 'Beräkna'],
            ['yteklass', 'kvalitet']]

        gyf_kvarters = [
            r'GYF för kvartersmark, Stockholm Stad',
            'GYF Kvartersmark',
            'kvartersgyf_sthm.pdf', 
            'kvartersgyf_grupp_tillaggsfaktorer.txt', 
            'kvartersgyf_tillaggsfaktorer.txt',
            'kvartersgyf_delfaktorer.txt',
            1,
            ['Delfaktorer','Tilläggsfaktorer', 'Visualisera', 'Beräkna'],
            ['delfaktor', 'tilläggsfaktor']]

        if self.proj.readEntry("QGYF", "model")[0] == r"GYF AP, C/O City":
            gyf_model = dict(zip(gyf_var, gyf_ap))
        else:
            gyf_model = dict(zip(gyf_var, gyf_kvarters))

        db = self.proj.readEntry("QGYF", "activeDataBase")[0]
        if db and os.path.exists("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], db)):
            QualityTable().init(gyf_model)
        
        return gyf_model

    def adjustDockwidget(self, model, layerSelectorDialog):
        ### GYF Name
        self.showGYFname(model)
        pdfGYF = lambda: self.pdfGYF(model)
        ### GYF Documentation
        self.dockwidget.info.disconnect()
        self.dockwidget.info.clicked.connect(pdfGYF)
        self.dockwidget.info_2.disconnect()
        self.dockwidget.info_2.clicked.connect(pdfGYF)
        ### Gound areas - enabled/disabled
        self.dockwidget.tabWidget.setTabEnabled(0, model['Ground_areas_enabled'])
        ### Import GYF model
        group_list = self.dockwidget.chooseQ('gyf_qgroup', self.dockwidget.selectQGroup, self.dockwidget.selectQ, self.dockwidget.textQ)
        
        ### Labels
        for n, t in enumerate(model['Tabs_labels']):
            self.dockwidget.tabWidget.setTabText(n,t)
        for n, t in enumerate(model['Klass_items']):
            layerSelectorDialog.tabWidget.setTabText(n,t.title())
        self.dockwidget.setTableLabels(model)
        
        # Tab1
        self.dockwidget.label_YQ.setText('Välj ' + model['Klass_items'][0])
        self.dockwidget.approveButton_2.setText('Lägg till ' + model['Klass_items'][0])
        self.dockwidget.removeButton_2.setText('Ta bort ' + model['Klass_items'][0])
        # Tab2
        self.dockwidget.label_G.setText('Välj grupp för ' + model['Klass_items'][1])
        self.dockwidget.label_Q.setText('Välj ' + model['Klass_items'][1])
        self.dockwidget.approveButton.setText('Lägg till ' + model['Klass_items'][1])
        self.dockwidget.removeButton.setText('Ta bort ' + model['Klass_items'][1])
        # Tab3
        items = [i.title()+'er' for i in model['Klass_items']]
        self.dockwidget.label_Areas.setText(items[0])
        self.dockwidget.showAreasClass.setText(items[0])
        self.dockwidget.showAreasLabels.setText('Visa upp etiketter med ' + model['Klass_items'][0] + 'er')
        self.dockwidget.showAreasPopups.setText('Aktivera popups med ' + model['Klass_items'][0] + 's beskrivningar')
        self.dockwidget.label_Qualities.setText(items[1])
        self.dockwidget.showAll.setText('Visa grupper av ' + model['Klass_items'][0] + 'er')
        self.dockwidget.showGroup.setText('Visa ' + model['Klass_items'][0] + 'er per grupp')
        self.dockwidget.createCheckBoxes(group_list)
        self.dockwidget.selectGroup.addItems(group_list)
        # Tab4
        #self.dockwidget.plot.canvas.fig.clf()
        self.dockwidget.plot.canvas.ax.cla()
        self.dockwidget.plot.canvas.ax.axis('off')
        self.dockwidget.obsText.clear()

        
    def showGYFname(self, model):
        gyf_name = '<h3 style="color:#238973">' + model['Name'] + '</h3>'
        self.dockwidget.gyfVersion.setText(gyf_name)
        self.dockwidget.gyfVersion_2.setText(gyf_name)

    def pdfGYF(self, model):
        docPath = self.plugin_dir + '/gyf_models/' + model['Doc']
        try:
            os.startfile(docPath)
        except:
            QMessageBox.warning(LayerSelectorDialog(), 'Ingen PDF läsare', 'Det ser ut att ingen PDF läsare finns installerat på datorn.')