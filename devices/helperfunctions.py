import json
import logging

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget, QVBoxLayout

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class RealTimePlot(QWidget):
    def __init__(self):
        super().__init__()

        # Create a figure and axis
        self.figure, self.ax = plt.subplots(dpi=300)
        self.canvas = FigureCanvas(self.figure)
        # Set up the layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def define_coordinate_frame_visualisation(self, corner_coords, r_n, c_n):
        return CoordinateFrameVisualisation(corner_coords, r_n, c_n, self.canvas)



class CoordinateFrameVisualisation:
    def __init__(self, corner_coords, r_n, c_n, canvas):

        # self.ax.clear()
        self.canvas = canvas
        self._dynamic_ax = self.canvas.figure.subplots()

        tl, tr, bl, br = corner_coords
        # center = self.state_dict_2_vector(all_state_dicts[((self.c_n/2)-1)+((self.r_n/2)-1)])

        # Set the x-axis and y-axis limits for the first subplot
        self._dynamic_ax.set_xlim(tl[0], tr[0])
        self._dynamic_ax.set_ylim(tl[1], bl[1])

        x_values = list(range(1, 25))
        y_values = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:r_n]]

        # Set y-axis ticks from P to A
        self._dynamic_ax.set_yticks(range(len(y_values)))
        self._dynamic_ax.set_yticklabels(reversed(y_values))

        self._dynamic_ax.set_title('Real-Time {} well plate positioning'.format(c_n * r_n))




    def drawcoordinate(self, vector):
        try:
            #3self.ax.clear()
            self._dynamic_ax.plot(vector[0], vector[1])
            self._dynamic_ax.figure.canvas.draw()
            #self._line.figure.canvas.draw()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here ", exc_info=True)
