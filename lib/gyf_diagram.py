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
        
    def piePlot(self, dockwidget, factor_areas, groups):
        dockwidget.plot.canvas.ax.cla()
        dockwidget.plot.canvas.ax.set_title('Fördelning av kvalitetspoäng')
        sizes, legend, colors, outline = self.init(factor_areas, groups)
        patches, text = dockwidget.plot.canvas.ax.pie(sizes, colors=colors, startangle=90, wedgeprops=outline)
        # Legend
        patches, legend, dummy =  zip(*sorted(zip(patches, legend, sizes), key=lambda x: x[2], reverse=True))
        dockwidget.plot.canvas.ax2.legend(patches, legend, loc = 'center', shadow = None, frameon = False)
        dockwidget.plot.canvas.draw()

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

    def balancePlot(self):
        con = spatialite_connect("{}\{}".format(QSettings().value('dataPath'), QSettings().value('activeDataBase')))
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM classification WHERE kvalitet LIKE "%B%"')
        B = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM classification WHERE kvalitet LIKE "%S%"')
        S = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM classification WHERE kvalitet LIKE "%K%"')
        K = cur.fetchone()[0]
        cur.execute('SELECT COUNT(*) FROM classification WHERE kvalitet LIKE "%L%"')
        L = cur.fetchone()[0]
        cur.close()
        con.close()

        max_values = np.array((34, 29, 20, 5))
        cur_values = np.array((B, S, K, L))
        result = (cur_values/max_values)*100

        items = ['Biologisk mångfald', 'Sociala värden', 'Klimatanpassning', 'Ljudkvalitet']
        cmap = [
            [0.36, 0.97, 0.41, 0.8], # green
            [1, 0.8, 0, 0.8], # orange
            [0.6, 0.8, 1, 0.8], # blue
            [0.5, 0, 0, 0.8], # maroon
        ]
        y = np.arange(len(items))
        for i in y:
            plt.bar(y[i], result[i], align='center', alpha=0.5, color=cmap[i], label=items[i])
        plt.yticks(y, items)
        plt.title('Balancering av möjliga faktorer')
        plt.legend()
        plt.tight_layout()
        plt.show()

