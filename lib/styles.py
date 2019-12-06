"""
---------------------------------------------------------------------------
styles.py
Created on: 2019-03-27 16:20:53
---------------------------------------------------------------------------
"""
import os
import sys
from qgis.core import QgsProject, QgsVectorLayer, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer
from qgis.utils import spatialite_connect, iface
from PyQt5.QtCore import QSettings

class Style:
    
    def styleCategories(self, path):
        con = spatialite_connect("{}\{}".format(path, QSettings().value('activeDataBase')))        
        cur = con.cursor()
        cur.execute('''SELECT grupp FROM gyf_qgroup''')
        items = [i[0] for i in cur.fetchall()][:6]
        cur.close()
        con.close()

        colors = [
            ['76,153,0,50', '0,102,0,50'], # green
            ['255,128,0,50', '204,102,0,50'], # orange
            ['51,153,255,50', '0,102,204,50'], # blue
            ['255,255,51,50', '204,204,0,50'], # yellow
            ['178,102,255,50', '76,0,153,50'], # violet
            ['255,0,127,50', '153,0,76,50'], # rose
        ]

        symbology = dict(zip(items, colors))
        categories1 = []
        categories2 = []
        categories3 = []
        for groups, (c1, c2) in symbology.items():
            symbol_point = QgsMarkerSymbol.createSimple({
                'color':c1,
                'color_border':c2,
                'width_border':'0.5'})
            symbol_line = QgsLineSymbol.createSimple({
                'color':c1,
                'width':'1.5'})
            symbol_poly = QgsFillSymbol.createSimple({
                'color':c1,
                'color_border':c2,
                'width_border':'0.5'})
            category1 = QgsRendererCategory(groups, symbol_point, groups)
            category2 = QgsRendererCategory(groups, symbol_line, groups)
            category3 = QgsRendererCategory(groups, symbol_poly, groups)
            categories1.append(category1)
            categories2.append(category2)
            categories3.append(category3)

        views = ['Punktkvalitet', 'Linjekvalitet', 'Ytkvalitet']
        symbols = dict(zip(views, [categories1, categories2, categories3]))
        for v, c in symbols.items():
            l = QgsProject.instance().mapLayersByName(v)
            if l:
                l = l[0]
                renderer = QgsCategorizedSymbolRenderer('grupp', c)
                l.setRenderer(renderer)
                l.triggerRepaint()

    def oneColor(self, lyr):
        if lyr.geometryType() == 2:
            symbol = QgsFillSymbol.createSimple({
                'color':'0, 153, 51, 60',
                'color_border':'0, 102, 0, 60',
                'width_border':'0.5'})
        elif lyr.geometryType() == 0:
            symbol = QgsMarkerSymbol.createSimple({
                'color':'0, 153, 51, 60', #'153, 0, 0, 50'
                'color_border':'0, 102, 0, 60', #'128, 0, 0, 50'
                'width_border':'0.5'})
        else:
            symbol = QgsLineSymbol.createSimple({
                'color':'0, 153, 51, 60', #'51, 102, 0, 50'
                'width':'1.5'})
        lyr.renderer().setSymbol(symbol)
        lyr.triggerRepaint()


    def styleResearchArea(self, lyr):
        symbol = QgsFillSymbol.createSimple({
            'color':'255,255,255,20',
            'color_border':'204,0,0',
            'width_border':'0.6',
            'style_border':'dash'})
        lyr.renderer().setSymbol(symbol)
        lyr.triggerRepaint()

    def visibility(self, group_name, bool):
        # Set layer group to visible/invisible
        root = QgsProject.instance().layerTreeRoot()
        group = root.findGroup(group_name)
        if group:
            group.setItemVisibilityChecked(bool)

    def iniStyle(self, lyr):
        # Style for initial objects which loads from database
        if lyr.geometryType() == 2:
            symbol = QgsFillSymbol.createSimple({
                'color':'88, 192, 40',
                'color_border':'77, 73, 73',
                'width_border':'0.1'})
        elif lyr.geometryType() == 0:
            symbol = QgsMarkerSymbol.createSimple({
                'color':'150, 72, 3', #'153, 0, 0, 50'
                'color_border':'81, 38, 1', #'128, 0, 0, 50'
                'width_border':'0.1'})
        else:
            symbol = QgsLineSymbol.createSimple({
                'color':'25, 84, 124', #'51, 102, 0, 50'
                'width':'1.5'})
        lyr.renderer().setSymbol(symbol)
        lyr.triggerRepaint()

    def styleGroundAreas(self, lyr):
        groups = ['Gr?nska', 'Vatten'] # '11,84,37,100'
        colors = [('f_diagonal', '0,102,0,150', '0,102,0,255'), ('b_diagonal', '0,43,128,150', '0,43,128,255')]
        symbology = dict(zip(groups, colors))
        categories = []
        for groups, (g, c1, c2) in symbology.items():
            symbol = QgsFillSymbol.createSimple({
                'style': g,
                'color': c1,
                'color_border': c2,
                'width_border':'0.1',
                'style_border': 'dot',
                })
            category = QgsRendererCategory(groups, symbol, groups)
            categories.append(category)
        
        renderer = QgsCategorizedSymbolRenderer('ytgrupp', categories)
        lyr.setRenderer(renderer)
        lyr.triggerRepaint()



