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
            'label_G',
            'label_Q']

        gyf_ap = [
            r'GYF för allmän platsmark, C/O City', 
            'gyf_ap.pdf', 
            'gyf_AP_groups.txt', 
            'gyf_AP_qualities.txt',
            'Välj kvalitetsgrupp',
            'Välj kvalitet']

        gyf_kvarters = [
            r'GYF för kvartersmark, Stockholm Stad', 
            'kvartersgyf_sthm.pdf', 
            'kvartersgyf_groups.txt', 
            'kvartersgyf_qualities.txt',
            'Välj faktorsgrupp',
            'Välj faktor']

        if QSettings().value('model') == r"GYF AP, C/O City":
            gyf_model = dict(zip(gyf_var, gyf_ap))
        else:
            gyf_model = dict(zip(gyf_var, gyf_kvarters))
        
        return gyf_model

    def adjustDockwidget(self, model):
        self.showGYFname(model)
        pdfGYF = lambda: self.pdfGYF(model)
        self.dockwidget.info.disconnect()
        self.dockwidget.info.clicked.connect(pdfGYF)
        QualityTable().init(QSettings().value('dataPath'), model)
        self.dockwidget.chooseQ(QSettings().value('dataPath'))
        self.dockwidget.label_G.setText(model['label_G'])
        self.dockwidget.label_Q.setText(model['label_Q'])

        

    def showGYFname(self, model):
        gyf_name = '<h3 style="color:#238973">' + model['Name'] + '</h3>'
        self.dockwidget.gyfVersion.setText(gyf_name)

    def pdfGYF(self, model):
        docPath = self.plugin_dir + '/gyf_models/' + model['Doc']
        try:
            os.startfile(docPath)
        except:
            QMessageBox.warning(ExportDialog(), 'Ingen PDF läsare', 'Det ser ut att ingen PDF läsare finns installerat på datorn.')