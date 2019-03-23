# -*- coding: utf-8 -*-
"""
/***************************************************************************
 QGYFDockWidget
                                 A QGIS plugin
 Green Space Factor
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2019-03-01
        git sha              : $Format:%H$
        copyright            : (C) 2019 by C/O City
        email                : info@cocity.se
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtCore import pyqtSignal
from qgis.core import QgsProject, QgsVectorLayer
from qgis.utils import iface
from qgis.utils import spatialite_connect

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'qgyf_dockwidget_base.ui'))


class QGYFDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(QGYFDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()

        """ Functions to classify input data"""    
    
    def chooseQ(self, path):
        self.selectQGroup.clear()
        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()

        self.textQ.clear()
        self.selectQ.clear()
        cur.execute('''SELECT grupp FROM gyf_qgroup''')
        items = [i[0] for i in cur.fetchall()]
        self.selectQGroup.addItems(items)
        
        cur.close()
        con.close()

    def getQ(self, path):
        self.selectQ.clear()
        self.textQ.clear()

        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()
        
        i = str(self.selectQGroup.currentIndex() + 1)
        cur.execute('SELECT kvalitet FROM gyf_quality WHERE grupp_id = ' + i)
        quality = [j[0] for j in cur.fetchall()]
        quality = quality + ['Vet inte']
        self.selectQ.addItems(quality)

        cur.close()
        con.close()
        
    def getF(self, path):
        self.textQ.clear()
        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()

        if self.selectQ.count() > 0:
            if self.selectQ.currentText() != 'Vet inte':
                q = [self.selectQ.currentText()]
                cur.execute('SELECT faktor,namn FROM gyf_quality WHERE kvalitet = ?', q)
                text = cur.fetchone()
                t = text[1] + ', faktor = ' + str(text[0])
                self.textQ.append(t)
            else:
                i = [self.selectQGroup.currentIndex() + 1]
                cur.execute('SELECT faktor FROM gyf_qgroup WHERE id = ?', i)
                text = '<b>Ungerfärligt beräkningsläge för GYF:en!</b><br>' + \
                    self.selectQGroup.currentText() + ', grov faktor = ' + str(cur.fetchone()[0])
                self.textQ.append(text)

        cur.close()
        con.close()

    def setLayers(self):
        self.selectLayer.clear()
        items = ['', 'punkt', 'linje', 'yta']
        self.selectLayer.addItems(items)
            
    def selectStart(self):
        # Start selection for QGYF
        for a in iface.attributesToolBar().actions(): 
            if a.objectName() == 'mActionDeselectAll':
                a.trigger()
                break

        iface.actionSelect().trigger()

        def lyr(x):
            return {'punkt': 'point_object',
                    'linje': 'line_object'}.get(x, 'polygon_object')
                    
        l = QgsProject.instance().mapLayersByName(lyr(self.selectLayer.currentText()))[0]
        iface.setActiveLayer(l)

    def setQ(self, path):
        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()

        layer = iface.activeLayer()
        selected = layer.selectedFeatures()
        attributes = []
        if selected:
            for f in selected:
                attributes.append(f.attributes())
        
        g = self.selectQGroup.currentText()
        geom = self.selectLayer.currentText()

        if self.selectQ.currentText() != 'Vet inte':
            q = self.selectQ.currentText()
            cur.execute('SELECT faktor FROM gyf_quality WHERE kvalitet = ?', [q])
        else:
            q = ''
            i = [self.selectQGroup.currentIndex() + 1]
            cur.execute('SELECT faktor FROM gyf_qgroup WHERE id = ?', i)
        f = cur.fetchone()[0]
        
        data = []
        for obj in attributes:
            data.append([geom, obj[1], obj[0], g, q, f])
        
        cur.executemany('INSERT INTO classification VALUES (?,?,?,?,?,?)', data)
        cur.close()
        con.commit()
        con.close()

    def showClass(self, path):
        self.classtable.clear()
        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()

        cur.execute('SELECT * FROM classification')
        data = cur.fetchall()
        
        if data:
            self.classtable.setRowCount(len(data))
            self.classtable.setColumnCount(len(data[0]))
            self.classtable.setHorizontalHeaderLabels(["geom", "fil namn", 'id', 'Grupp', 'K', 'F'])
            for i, item in enumerate(data):
                for j, field in enumerate(item):
                    self.classtable.setItem(i, j, QtWidgets.QTableWidgetItem(str(field)))
                    self.classtable.horizontalHeader().setSectionResizeMode(j, QtWidgets.QHeaderView.ResizeToContents)

        cur.close()
        con.close()
