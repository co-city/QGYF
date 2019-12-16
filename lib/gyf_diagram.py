try:
    from PyQt5 import QtWidgets
    from qgis.core import QgsProject
    from matplotlib.gridspec import GridSpec
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
    import matplotlib
    import matplotlib.pyplot as plt
    matplotlib.use('QT5Agg')
    import numpy as np
    from qgis.utils import spatialite_connect

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
            size = sum([factor_areas[i] for i in ii])
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
        
        return sizes, items, colors, outline

    def initCanvas(self, dockwidget):
        gs = GridSpec(4,1)
        dockwidget.plot.canvas.ax = dockwidget.plot.canvas.fig.add_subplot(gs[0:3,0])
        dockwidget.plot.canvas.ax2 = dockwidget.plot.canvas.fig.add_subplot(gs[3,0])
        dockwidget.plot.canvas.ax2.axis('off')
        
    def piePlot(self, dockwidget, factor_areas, groups):
        dockwidget.plot.canvas.ax.cla()
        #dockwidget.plot.canvas.fig.clf()
        #if not hasattr(dockwidget.plot.canvas, 'ax'):
        #    self.initCanvas(dockwidget)
        dockwidget.plot.canvas.ax.axis('equal')
        dockwidget.plot.canvas.ax.axis('off')
        dockwidget.plot.canvas.ax.set_title('Fördelning av kvalitetspoäng')
        sizes, items, colors, outline = self.init(factor_areas, groups)
        patches, text = dockwidget.plot.canvas.ax.pie(sizes, colors=colors, startangle=90, wedgeprops=outline)
        # Legend
        self.setLegend(items, patches, sizes, dockwidget.plot.canvas.ax2)
        dockwidget.plot.canvas.draw()

    def ecoAreaPlot(self, eco_area, total_area):
        proj = QgsProject.instance()
        labels = ['Grön yta', 'Grå yta']
        colors = [
                [0, 0.6, 0, 0.8], # green
                [0.6, 0.6, 0.6, 0.8], # grey
            ]
        sizes = [eco_area*100/total_area, abs(total_area - eco_area)*100/total_area]
        items = [[sizes[i], labels[i]] for i,x in enumerate(sizes)]

        outline = {"edgecolor":"white", 'linewidth': 0.8, 'antialiased': True}

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
        self.setLegend(items, patches, sizes, ax2)
        chart_path = proj.readEntry("QGYF", "dataPath")[0] + '\PieChart2.png'
        plt.savefig(chart_path)

    def balancePlot(self, dockwidget, balancering):
        
        max_values = np.array((34, 29, 20, 5))
        cur_values = np.asarray(balancering)
        result = (cur_values/max_values)*100

        items = ['Biologisk mångfald', 'Sociala värden', 'Klimatanpassning', 'Ljudkvalitet']
        items = [[result[i], items[i]] for i,x in enumerate(result)]
        labels = ['B', 'S', 'K', 'L']
        cmap = [
            [0, 0.7, 0, 0.8], # green
            [1, 0.8, 0, 0.8], # orange
            [0.6, 0.8, 1, 0.8], # blue
            [0.5, 0, 0, 0.8], # maroon
        ]
        clabels = [
            [0, 0.5, 0, 0.8], # green
            [0.8, 0.6, 0, 0.8], # orange
            [0, 0.35, 0.7, 0.8], # blue
            [0.5, 0, 0, 0.8], # maroon
        ]
        x = np.arange(len(labels))

        dockwidget.plot.canvas.ax.cla()
        #dockwidget.plot.canvas.fig.clf()
        #if not hasattr(dockwidget.plot.canvas, 'ax'):
        #    self.initCanvas(dockwidget)
        dockwidget.plot.canvas.ax.axis('auto')
        dockwidget.plot.canvas.ax.axis('on')
        dockwidget.plot.canvas.fig.subplots_adjust(hspace=1.5)
        dockwidget.obsText.clear()
        patches = []
        for i in x:
            patch = dockwidget.plot.canvas.ax.bar(x[i], result[i], align='center', color=cmap[i])
            patches.append(patch)

        dockwidget.plot.canvas.ax.set_xticks(x)
        dockwidget.plot.canvas.ax.set_xticklabels(labels)
        for ticklabel, tickcolor in zip(dockwidget.plot.canvas.ax.get_xticklabels(), clabels):
            ticklabel.set_color(tickcolor)
            ticklabel.set_weight("bold")
        dockwidget.plot.canvas.ax.set_ybound((0,100))
        dockwidget.plot.canvas.ax.tick_params(axis='x', width=0)
        dockwidget.plot.canvas.ax.set_title('Balancering av möjliga faktorer')
        self.setLegend(items, patches, result, dockwidget.plot.canvas.ax2)
        dockwidget.plot.canvas.draw()
        if any(result < 60):
            dockwidget.obsText.setText('''<p style="color:#cc2900">OBS! Minst 60 % av möjliga faktorer inom biologisk mångfald, \
            sociala värden, klimatanpassning och ljudkvalitet ska uppnås för att balanseringen ska bli godkänd.</p>''')

    def setLegend(self, items, patches, sizes, canvas):
        legend = ['{:.1f} % - {}'.format(float(i[0]), i[1]) for i in items]
        patches, legend, dummy =  zip(*sorted(zip(patches, legend, sizes), key=lambda x: x[2], reverse=True))
        canvas.legend(patches, legend, loc = 'center', shadow = None, frameon = False)


