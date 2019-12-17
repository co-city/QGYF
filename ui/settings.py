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
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from qgis.utils import iface, spatialite_connect
from ..lib.db import Db
from ..lib.gyf_tables import QualityTable
from ..lib.switch_gyf import SwitchGYFs
from qgis.gui import QgsProjectionSelectionDialog
from qgis.core import QgsProject, QgsCoordinateReferenceSystem

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings.ui'))

class SettingsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, dockwidget, model, plugin_dir, layerSelectorDialog, parent=None, parentWidget=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.proj = QgsProject.instance()
        modelGyf = model
        self.switch = SwitchGYFs(dockwidget, plugin_dir)
        self.populate()
        self.populateGYF()
        self.dataPath.setText(self.proj.readEntry("QGYF", "dataPath")[0])
        if self.proj.readEntry("QGYF", "CRS")[0]:
            crs = QgsCoordinateReferenceSystem(int(self.proj.readEntry("QGYF", "CRS")[0]))
            self.crs.setText(crs.description())
        self.selectPathButton.clicked.connect(self.openFileDialog)
        self.clearDatabaseButton.clicked.connect(lambda : self.clearDataBase(dockwidget))
        self.activeDatabase.currentIndexChanged.connect(self.setDatabase)
        self.parent = parentWidget
        self.selectCRSButton.clicked.connect(self.setCRS)
        updateDockwidget = lambda : self.updateDockwidget(dockwidget, layerSelectorDialog)
        self.db = Db()
        self.quality = QualityTable()
        if self.db.checkClass():
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
            if m == self.proj.readEntry("QGYF", "model")[0]:
                activeIndex = index
            index += 1

        self.setGYF(activeIndex)


    def setGYF(self, index):
        self.currentGyf.setCurrentIndex(index)
        if self.currentGyf.currentText():
            self.proj.writeEntry("QGYF", "model",self.currentGyf.currentText())
            global modelGyf
            modelGyf = self.switch.defineGYF()
        
    def updateDockwidget(self, dockwidget, layerSelectorDialog):
        self.checkbox_list = self.switch.adjustDockwidget(modelGyf, layerSelectorDialog)
        dockwidget.showClass()
        

    def clearDataBase(self, dockwidget):
        self.db.clear()
        self.msg = QMessageBox()
        self.msg.setIcon(QMessageBox.Information)
        self.msg.setWindowTitle("Information")
        self.msg.setText("Databasen rensades")
        self.msg.show()
        iface.mapCanvas().refreshAllLayers()
        if dockwidget.isVisible():
            dockwidget.showClass()
            dockwidget.showAreas()
        
    def openFileDialog(self):
        path = QFileDialog.getExistingDirectory(self, 'Öppna fil', '', QFileDialog.ShowDirsOnly)
        if path:
            self.proj.writeEntry("QGYF", "dataPath", path)
            self.dataPath.setText(self.proj.readEntry("QGYF", "dataPath")[0])
            self.activeDatabase.clear()
            self.populate()

    def setDatabase(self, index):
        self.activeDatabase.setCurrentIndex(index)
        if self.activeDatabase.currentText():
            self.proj.writeEntry("QGYF", "activeDataBase", self.activeDatabase.currentText())
            crs_id = self.getCRS(self.proj.readEntry("QGYF", "activeDataBase")[0])
            self.proj.writeEntry("QGYF", "CRS", crs_id)
            crs = QgsCoordinateReferenceSystem(int(float(crs_id)))
            self.crs.setText(crs.description())
        else:
            self.proj.writeEntry("QGYF", "activeDataBase", 'qgyf.sqlite')

    def populate(self):
        if not os.path.exists(self.proj.readEntry("QGYF", "dataPath")[0]):
            self.proj.writeEntry("QGYF", "dataPath", os.getenv('APPDATA') + '\QGYF')
        listOfFiles = os.listdir(self.proj.readEntry("QGYF", "dataPath")[0])
        pattern = "*.sqlite"
        self.activeDatabase.clear()
        activeIndex = 0
        index = 0
        for entry in listOfFiles:
            if fnmatch.fnmatch(entry, pattern):
                self.activeDatabase.addItem(entry)
                if entry == self.proj.readEntry("QGYF", "activeDataBase")[0]:
                    activeIndex = index
                index += 1

        self.setDatabase(activeIndex)

    def defineCRS(self):
        projSelector = QgsProjectionSelectionDialog()
        projSelector.exec()
        crs_id = projSelector.crs().authid()
        if crs_id:
            crs_id = ''.join(c for c in crs_id if c.isdigit())
            self.proj.writeEntry("QGYF", "CRS", crs_id)
            print(self.proj.readEntry("QGYF", "CRS")[0])
        self.crs.setText(projSelector.crs().description())

    def setCRS(self):
        if os.path.exists("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], self.proj.readEntry("QGYF", "activeDataBase")[0])):
            if not self.db.checkObjects():
                QMessageBox.warning(self, 'Koordinatsystem kan inte ändras', '''Den aktiva databasen ''' \
                        '''innehåller data. Töm databasen för att sätta ett nytt koordinatsystem.''')
            else:
                try:
                    self.defineCRS()
                    os.remove("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], self.proj.readEntry("QGYF", "activeDataBase")[0]))
                    self.db.create()               
                    self.quality.init(modelGyf)
                except:
                    QMessageBox.information(self, 'Koordinatsystem kan inte ändras', '''Det går inte att ändra på koordinatsystem ''' \
                        '''för att databasen används i nuvarande QGIS projekt. Ta bort alla lager som tillhör till QGYF databas ''' \
                        '''från projektet och prova på nytt.''')
        else:
            self.defineCRS()

    def getCRS(self, db):
        if os.path.exists("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], db)):
            con = spatialite_connect("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], db))
            cur = con.cursor()

            cur.execute('SELECT srid FROM geometry_columns;')
            c = cur.fetchone()[0]

            cur.close()
            con.close()
            return c


        
