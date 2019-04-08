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
            print(ii)
            size = factor_areas[ii].sum()
            sizes.append(size*100/total)

        items = ['Biologisk mångdfald',
        'Bullerreducering',
        'Dagvatten- och skyfallshantering',
        'Mikroklimatreglering',
        'Pollination',
        'Rekreation och hälsa']
        cmap = [
            [0.3, 0.6, 0, 0.5], # green
            [1, 0.5, 0, 0.5], # orange
            [0.2, 0.6, 1, 0.5], # blue
            [1, 1, 0.2, 0.5], # yellow
            [0.7, 0.4, 1, 0.5], # violet
            [0.98, 0.65, 1, 0.5], # rose
        ]
        symbology = dict(zip(items, cmap))
        
        def setColor(x):
            return symbology.get(x)
        colors = [setColor(l) for l in labels]

        outline = {"edgecolor":"white",'linewidth': 0.1, 'antialiased': True}

        return sizes, labels, colors, outline
