'''
---------------------------------------------------------------------------
export.py
Created on: 2019-04-10 12:04:28
QGYF export dialog
---------------------------------------------------------------------------
'''
import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import QSettings

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'export.ui'))

class ExportDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ExportDialog, self).__init__(parent)
        self.setupUi(self)
        self.selectPathButton.clicked.connect(self.openFileDialog)
        self.pdfPath.setText(QSettings().value('exportPath'))
        self.author.setText(QSettings().value('author'))
        self.author.textChanged.connect(self.saveAuthor)
        self.projectName.textChanged.connect(self.setName)
            
        if self.pdfName.text()[-3:] != 'pdf':
            self.pdfName.setText(self.pdfName.text() + '.pdf')

    def openFileDialog(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Öppna fil', '', QtWidgets.QFileDialog.ShowDirsOnly)
        if path:
            QSettings().setValue('exportPath', path)
            self.pdfPath.setText(QSettings().value('exportPath'))

    def saveAuthor(self):
        QSettings().setValue('author', self.author.text())
        QSettings().sync()

    def setName(self):
        if self.projectName.text() != '':
            self.pdfName.setText(self.projectName.text() + '.pdf')



    