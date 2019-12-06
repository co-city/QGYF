'''
---------------------------------------------------------------------------
settings.py
Created on: 2019-04-09 12:04:28
QGYF settings dialog
---------------------------------------------------------------------------
'''
import os, fnmatch
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from qgis.utils import iface, spatialite_connect
from ..lib.db import Db
from ..lib.gyf_tables import QualityTable
from ..lib.switch_gyf import SwitchGYFs
from qgis.gui import QgsProjectionSelectionDialog
from qgis.core import QgsCoordinateReferenceSystem

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings.ui'))

class SettingsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, dockwidget, model, plugin_dir, parent=None, parentWidget=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        modelGyf = model
        self.switch = SwitchGYFs(dockwidget, plugin_dir)
        self.populate()
        self.populateGYF()
        self.dataPath.setText(QSettings().value('dataPath'))
        crs = QgsCoordinateReferenceSystem(QSettings().value('CRS'))
        self.crs.setText(crs.description())
        self.selectPathButton.clicked.connect(self.openFileDialog)
        self.clearDatabaseButton.clicked.connect(self.clearDataBase)
        self.activeDatabase.currentIndexChanged.connect(self.setDatabase)
        self.parent = parentWidget
        self.selectCRSButton.clicked.connect(self.setCRS)
        updateDockwidget = lambda : self.updateDockwidget(dockwidget)
        self.db = Db()
        self.quality = QualityTable()
        if self.db.checkClass(QSettings().value('dataPath')):
            self.currentGyf.setEnabled(True)
            self.currentGyf.currentIndexChanged.connect(self.setGYF)
            if dockwidget.isVisible():
                self.currentGyf.currentIndexChanged.connect(updateDockwidget)
        else:
            self.currentGyf.setEnabled(False)

    def populateGYF(self):
        models = [r'KvartersGYF, Sthm Stad', r'GYF AP, C/O City']
        activeIndex = 0
        index = 0
        for m in models:
            self.currentGyf.addItem(m)
            if m == QSettings().value('model'):
                activeIndex = index
            index += 1

        self.setGYF(activeIndex)


    def setGYF(self, index):
        self.currentGyf.setCurrentIndex(index)
        if self.currentGyf.currentText():
            QSettings().setValue('model', self.currentGyf.currentText())
            global modelGyf
            modelGyf = self.switch.defineGYF()
        

    def updateDockwidget(self, dockwidget):
        self.switch.adjustDockwidget(modelGyf)
        dockwidget.showClass()
        

    def clearDataBase(self):
        self.db.clear("{}\{}".format(QSettings().value('dataPath'), QSettings().value('activeDataBase')))
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setWindowTitle("Information")
        self.msg.setText("Databasen rensades")
        self.msg.show()
        iface.mapCanvas().refreshAllLayers()
        
    def openFileDialog(self):
        path = QFileDialog.getExistingDirectory(self, 'Öppna fil', '', QFileDialog.ShowDirsOnly)
        if path:
            QSettings().setValue('dataPath', path)
            self.dataPath.setText(QSettings().value('dataPath'))
            self.activeDatabase.clear()
            self.populate()

    def setDatabase(self, index):
        self.activeDatabase.setCurrentIndex(index)
        if self.activeDatabase.currentText():
            QSettings().setValue('activeDataBase', self.activeDatabase.currentText())
            crs_id = self.getCRS(QSettings().value('activeDataBase'))
            QSettings().setValue('CRS', crs_id)
            crs = QgsCoordinateReferenceSystem(crs_id)
            self.crs.setText(crs.description())
        else:
            QSettings().setValue('activeDataBase', 'qgyf.sqlite')

    def populate(self):
        if not os.path.exists(QSettings().value('dataPath')):
            QSettings().setValue('dataPath', os.getenv('APPDATA') + '\QGYF')
        listOfFiles = os.listdir(QSettings().value('dataPath'))
        pattern = "*.sqlite"
        self.activeDatabase.clear()
        activeIndex = 0
        index = 0
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern):
                self.activeDatabase.addItem(entry)
                if entry == QSettings().value('activeDataBase'):
                    activeIndex = index
                index += 1

        self.setDatabase(activeIndex)

    def defineCRS(self):
        projSelector = QgsProjectionSelectionDialog()
        projSelector.exec()
        crs_id = projSelector.crs().authid()
        if crs_id:
            QSettings().setValue('CRS', crs_id)
        self.crs.setText(projSelector.crs().description())

    def setCRS(self):
        if os.path.exists(QSettings().value("dataPath") + r'\\' + QSettings().value("activeDataBase")):
            if not self.db.checkObjects(QSettings().value('dataPath')):
                QMessageBox.warning(self, 'Koordinatsystem kan inte ändras', '''Den aktiva databasen ''' \
                        '''innehåller data. Töm databasen för att sätta ett nytt koordinatsystem.''')
            else:
                try:
                    self.defineCRS()
                    os.remove(QSettings().value("dataPath") + r'\\' + QSettings().value("activeDataBase"))
                    self.db.create(QSettings().value('dataPath'))               
                    self.quality.init(path, modelGyf)
                except:
                    QMessageBox.information(self, 'Koordinatsystem kan inte ändras', '''Det går inte att ändra på koordinatsystem ''' \
                        '''för att databasen används i nuvarande QGIS projekt. Ta bort alla lager som tillhör till QGYF databas ''' \
                        '''från projektet och prova på nytt.''')
        else:
            self.defineCRS()

    def getCRS(self, db):
        if os.path.exists(QSettings().value("dataPath") + r'\\' + QSettings().value("activeDataBase")):
            con = spatialite_connect("{}\{}".format(QSettings().value('dataPath'), db))
            cur = con.cursor()

            cur.execute('SELECT srid FROM geometry_columns;')
            c = cur.fetchone()[0]

            cur.close()
            con.close()
            return c


        
