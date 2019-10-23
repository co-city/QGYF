try:
    from PyQt5 import QtWidgets
    from PyQt5.QtCore import QSettings
    from matplotlib.gridspec import GridSpec
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('QT5Agg')
    import numpy as np

    from ..ui.mplwidget import MplWidget
except:
    pass

class Diagram:

    def init(self, factor_areas, groups):
        labels = list(set(groups))
        total = sum(factor_areas)
        sizes = []
        for group in labels:
            ii = [index for (index, g) in enumerate(groups) if g == group]
            size = factor_areas[ii].sum()
            sizes.append(size*100/total)

        items = ['Biologisk mångfald',
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

    def ecoAreaPlot(self, eco_area, total_area):
        labels = ['Grön yta', 'Grå yta']
        colors = [
                [0, 0.6, 0, 0.8], # green
                [0.6, 0.6, 0.6, 0.8], # grey
            ]
        sizes = [eco_area*100/total_area, abs(total_area - eco_area)*100/total_area]
        items = [[sizes[i], labels[i]] for i,x in enumerate(sizes)]

        outline = {"edgecolor":"white", 'linewidth': 0.8, 'antialiased': True}
        legend = ['{:.1f} % - {}'.format(float(i[0]), i[1]) for i in items]

        # Plot
        gs = GridSpec(4,1)
        ax = plt.subplot(gs[0:3,0])
        ax.axis('off')
        ax.axis('equal')
        ax2 = plt.subplot(gs[3,0])
        ax2.axis('off')
        matplotlib.rcParams['font.size'] = 8.0
        ax.set_title('Andel grön- och hårdgjord yta')

        patches, text = ax.pie(sizes, colors=colors, startangle=90, wedgeprops=outline)
        patches, legend, dummy =  zip(*sorted(zip(patches, legend, sizes), key=lambda x: x[2], reverse=True))
        ax2.legend(patches, legend, loc = 'center', shadow = None, frameon = False)
        chart_path = QSettings().value('dataPath') + '\PieChart2.png'
        plt.savefig(chart_path)

