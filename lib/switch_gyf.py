# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------
switch_gyf.py
Created on: 2019-11-09 22:05:53
---------------------------------------------------------------------------
"""
import os
import os.path
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QMessageBox

from ..ui.export import ExportDialog
from .gyf_tables import QualityTable


class SwitchGYFs:
    def __init__(self, dockwidget, plugin_dir):
        self.dockwidget = dockwidget
        self.plugin_dir = plugin_dir
        

    def defineGYF(self):
        gyf_var = [
            'Name', 
            'Doc', 
            'Input_groups', 
            'Input_categories',
            'Input_ground_areas',
            'Ground_areas_enabled',
            'Tabs_labels',
            'Klass_items']

        gyf_ap = [
            r'GYF för allmän platsmark, C/O City', 
            'gyf_ap.pdf', 
            'gyf_AP_groups.txt', 
            'gyf_AP_qualities.txt',
            'gyf_AP_groundareas.txt',
            0,
            ['Grundytor','Klassificera', 'Visualisera', 'Beräkna'],
            ['yteklass', 'kvalitet']]

        gyf_kvarters = [
            r'GYF för kvartersmark, Stockholm Stad', 
            'kvartersgyf_sthm.pdf', 
            'kvartersgyf_grupp_tillaggsfaktorer.txt', 
            'kvartersgyf_tillaggsfaktorer.txt',
            'kvartersgyf_delfaktorer.txt',
            1,
            ['Delfaktorer','Tilläggsfaktorer', 'Visualisera', 'Beräkna'],
            ['delfaktor', 'tilläggsfaktor']]

        if QSettings().value('model') == r"GYF AP, C/O City":
            gyf_model = dict(zip(gyf_var, gyf_ap))
        else:
            gyf_model = dict(zip(gyf_var, gyf_kvarters))
        
        return gyf_model

    def adjustDockwidget(self, model):
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
        QualityTable().init(QSettings().value('dataPath'), model)
        self.dockwidget.chooseQ('gyf_qgroup', self.dockwidget.selectQGroup, self.dockwidget.selectQ, self.dockwidget.textQ)
        
        ### Labels
        for n, t in enumerate(model['Tabs_labels']):
            self.dockwidget.tabWidget.setTabText(n,t)
        
        # Tab1
        self.dockwidget.label_YQ.setText('Välj ' + model['Klass_items'][0])
        self.dockwidget.approveButton_2.setText('Lägg till ' + model['Klass_items'][0])
        self.dockwidget.removeButton_2.setText('Ta bort ' + model['Klass_items'][0])
        # Tab2
        self.dockwidget.label_G.setText('Välj grupp för ' + model['Klass_items'][1])
        self.dockwidget.label_Q.setText('Välj ' + model['Klass_items'][1])
        self.dockwidget.approveButton.setText('Lägg till ' + model['Klass_items'][1])
        self.dockwidget.removeButton.setText('Ta bort ' + model['Klass_items'][1])
        
    def showGYFname(self, model):
        gyf_name = '<h3 style="color:#238973">' + model['Name'] + '</h3>'
        self.dockwidget.gyfVersion.setText(gyf_name)
        self.dockwidget.gyfVersion_2.setText(gyf_name)

    def pdfGYF(self, model):
        docPath = self.plugin_dir + '/gyf_models/' + model['Doc']
        try:
            os.startfile(docPath)
        except:
            QMessageBox.warning(ExportDialog(), 'Ingen PDF läsare', 'Det ser ut att ingen PDF läsare finns installerat på datorn.')