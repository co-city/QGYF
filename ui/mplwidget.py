# Imports
from PyQt5 import QtWidgets
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
import matplotlib

# Ensure using PyQt5 backend
matplotlib.use('QT5Agg')

# Matplotlib canvas class to create figure
class MplCanvas(Canvas):
    def __init__(self):
        self.fig = Figure()
        gs = GridSpec(4,1)
        self.ax = self.fig.add_subplot(gs[0:3,0])
        self.ax.axis('off')
        self.ax2 = self.fig.add_subplot(gs[3,0])
        self.ax2.axis('off')
        matplotlib.rcParams['font.size'] = 8.0
        Canvas.__init__(self, self.fig)
        Canvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

# Matplotlib widget
class MplWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)   # Inherit from QWidget
        self.canvas = MplCanvas()                  # Create canvas object
        self.vbl = QtWidgets.QVBoxLayout()         # Set box for plotting
        self.vbl.addWidget(self.canvas)
        self.setLayout(self.vbl)