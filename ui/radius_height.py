'''
---------------------------------------------------------------------------
radius_height.py
Created on: 2019-05-07 08:41:28
Dialog window to set radius for points and height for lines
---------------------------------------------------------------------------
'''
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMessageBox, QDialog
from qgis.utils import spatialite_connect
from qgis.core import QgsProject

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'radius_height.ui'))


class GeometryDialog(QDialog, FORM_CLASS):
    def __init__(self, dockwidget, parent=None, parentWidget=None):
        super(GeometryDialog, self).__init__(parent)
        self.setupUi(self)
        self.proj = QgsProject.instance()
        if dockwidget.tabWidget.currentIndex() == 1:
            geometry = self.switchPointLine(dockwidget)
            self.saveButton.clicked.connect(lambda : self.setValue(dockwidget, geometry))
        else:
            self.radiusButton.setEnabled(False)
            self.heightButton.setChecked(True)
            selected_items = dockwidget.areasTable.selectedItems()
            if selected_items:
                self.show()
                self.saveButton.clicked.connect(lambda : self.setValueArea(dockwidget, selected_items))
            else:
                QMessageBox.warning(self, 'Inget valt objekt', 'Välj grundyta i tabellen för att sätta höjden på.')
            
        
    def switchPointLine(self, dockwidget):
        geometry = None 
        selected_items = dockwidget.classtable.selectedItems()
        if selected_items:
            selected_rows = list(set([i.row() for i in selected_items]))
            geom = [dockwidget.classtable.item(i, 0).text() for i in selected_rows]
            geom = list(set(geom))
            if len(geom) == 1:
                geometry = geom[0]
                if geometry == 'punkt':
                    self.radiusButton.setChecked(True)
                    self.heightButton.setChecked(False)
                    self.heightButton.setEnabled(False)
                    self.show()
                elif geometry == 'linje':
                    self.heightButton.setChecked(True)
                    self.radiusButton.setChecked(False)
                    self.radiusButton.setEnabled(False)
                    self.show()
                else:
                     QMessageBox.warning(self, 'Valt ytobjekt', 'Det går inte att uppdatera geometri för ytobjekt. Välj punkt- eller linjeobjekt för att sätta en ny yta/höjd.')
            else:
                QMessageBox.warning(self, 'Olika geometrier', 'De valda objekten har olika geometrier. Välj antingen punkter eller linjer i klassificeringstabell.')
        else:
            QMessageBox.warning(self, 'Inget valt objekt', 'Välj punkt- eller linjeobjekt i klassificeringstabell för att sätta geometri på.')
        
        return geometry


    def setValue(self, dockwidget, geometry):
        selected_items = dockwidget.classtable.selectedItems()
        selected_rows = list(set([i.row() for i in selected_items]))
        gids = [dockwidget.classtable.item(i, 7).text() for i in selected_rows]
        value = self.valueLine.text()
        try:
            value = round(float(value),1)
            if value == 0:
                value = 1.0
            items = []
            con = spatialite_connect("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], self.proj.readEntry("QGYF", 'activeDataBase')[0]))
            cur = con.cursor()
            
            if geometry == 'linje':
                for i in gids:
                    cur.execute('SELECT faktor, kvalitet, gid FROM classification WHERE gid = (?);', [i])
                    y = [[j[0], j[1], j[2]] for j in cur.fetchall()]
                    cur.execute('SELECT GLENGTH(geom) FROM line_object WHERE gid = (?);', [i])
                    l = [j[0] for j in cur.fetchall()]
                    items += [l + y[0]]
                values = [[y[0]*value, y[0]*value*y[1], y[2], y[3]] for y in items]
            else:
                for i in gids:
                    cur.execute('SELECT faktor, kvalitet, gid FROM classification WHERE gid = (?);', [i])
                    y = [[j[0], j[1], j[2]] for j in cur.fetchall()]
                    items += y
                values = [[value, value*j[0], j[1], j[2]] for j in items]

            cur.executemany('UPDATE classification SET yta = (?), poang = (?) WHERE kvalitet = (?) AND gid = (?);', values)
            values = [[v[0], v[-1]] for v in values]
            cur.executemany('UPDATE point_object SET yta = (?) WHERE gid = (?);', values)
            cur.executemany('UPDATE line_object SET yta = (?) WHERE gid = (?);', values)

            cur.close()
            con.commit()
            con.close()
            dockwidget.showClass()
            self.close()
        except:
            QMessageBox.warning(self, 'Fel värde', 'Ange ett numeriskt värde för yta eller höjd.')

    def setValueArea(self, dockwidget, selected_items):
        selected_rows = list(set([i.row() for i in selected_items]))
        ids = [dockwidget.areasTable.item(i, 5).text() for i in selected_rows]
        value = self.valueLine.text()
        try:
            value = round(float(value),1)
            if value == 0:
                value = 1.0
            items = []
            con = spatialite_connect("{}\{}".format(self.proj.readEntry("QGYF", "dataPath")[0], self.proj.readEntry("QGYF", 'activeDataBase')[0]))
            cur = con.cursor()
            
            for i in ids:
                cur.execute('SELECT faktor, ytklass, yta, id FROM ground_areas WHERE id = (?);', [i])
                y = [[j[0], j[1], j[2], j[3]] for j in cur.fetchall()]
                items += y
            values = [[y[2]*value, y[2]*value*y[0], y[1], y[3]] for y in items]

            cur.executemany('UPDATE ground_areas SET yta = (?), poang = (?) WHERE ytklass = (?) AND id = (?);', values)

            cur.close()
            con.commit()
            con.close()
            dockwidget.showAreas()
            self.close()
        except:
            QMessageBox.warning(self, 'Fel värde', 'Ange ett numeriskt värde för höjd.')


