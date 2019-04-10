from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from ..ui.mplwidget import MplWidget


matplotlib.use('QT5Agg')

class Diagram:

    def init(self, factor_areas, groups):
            labels = list(set(groups))
            total = sum(factor_areas)
            factor_areas = np.asarray(factor_areas)
            sizes = []
            for group in labels:
                ii = [index for (index, g) in enumerate(groups) if g == group]
                size = factor_areas[ii].sum()
                sizes.append(size*100/total)

            items = ['Biologisk mångdfald',
            'Bullerreducering',
            'Dagvatten- och skyfallshantering',
            'Mikroklimatreglering',
            'Pollination',
            'Rekreation och hälsa']
            cmap = [
                [0.36, 0.97, 0.41, 0.8], # green
                [0.98, 0.8, 0.3, 0.8], # orange
                [0.3, 0.84, 0.98, 0.8], # blue
                [0.98, 1, 0.4, 0.8], # yellow
                [0.83, 0.71, 1, 0.8], # violet
                [1, 0.64, 0.97, 0.8], # rose
            ]
            symbology = dict(zip(items, cmap))
            
            def setColor(x):
                return symbology.get(x)
            colors = [setColor(l) for l in labels]
            items = [[sizes[i], labels[i]] for i,x in enumerate(sizes)]

            outline = {"edgecolor":"white", 'linewidth': 0.8, 'antialiased': True}
            legend = ['{:.1f} % - {}'.format(float(i[0]), i[1]) for i in items]

            return sizes, legend, colors, outline
