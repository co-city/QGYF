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
        self.selectQ.addItems(quality)

        cur.close()
        con.close()
        
    def getF(self, path):
        self.textQ.clear()

        if self.selectQ.count() > 0:
            con = spatialite_connect(path + r'\qgyf.sqlite')
            cur = con.cursor()
            
            q = [self.selectQ.currentText()]
            cur.execute('SELECT faktor,namn FROM gyf_quality WHERE kvalitet = ?', q)
            text = cur.fetchone()
            t = text[1] + ', faktor = ' + str(text[0])
            self.textQ.append(t)
            
            cur.close()
            con.close()
            
    def selectStart(self):
        # Start selection for QGYF
        iface.actionSelect().trigger()
        def select():
            layer = iface.activeLayer()
            selected = layer.selectedFeatures()
            print(selected)
            if selected:
                for f in selected:
                    print(f.attributes())
        iface.mapCanvas().selectionChanged.connect(select)

    def setQ(self, path):
        con = spatialite_connect(path + r'\qgyf.sqlite')
        cur = con.cursor()

        cur.close()
        con.close()