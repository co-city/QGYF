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
from PyQt5.QtWidgets import QFileDialog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'settings.ui'))

class SettingsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(SettingsDialog, self).__init__(parent)
        self.setupUi(self)
        self.dataPath.setText(QSettings().value('dataPath'))
        self.populate()
        self.selectPathButton.clicked.connect(self.openFileDialog)
        self.activeDatabase.currentIndexChanged.connect(self.setDatabase)

    def openFileDialog(self):
        path = QFileDialog.getExistingDirectory(self, 'Öppna fil', '', QFileDialog.ShowDirsOnly)
        if path:
            QSettings().setValue('dataPath', path)
            self.dataPath.setText(QSettings().value('dataPath'))
            self.activeDatabase.clear()
            self.populate()

    def setDatabase(self, index):
        self.activeDatabase.setCurrentIndex(index)
        QSettings().setValue('activeDataBase', self.activeDatabase.currentText())

    def populate(self):
        listOfFiles = os.listdir(QSettings().value('dataPath'))
        pattern = "*.sqlite"
        self.activeDatabase.clear()
        activeIndex = 0
        for index, entry in enumerate(listOfFiles):
            if fnmatch.fnmatch(entry, pattern):
                self.activeDatabase.addItem(entry)
                if entry == QSettings().value('activeDataBase'):
                    activeIndex = index

        self.setDatabase(activeIndex)