import json
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QWidget


class RealTimePlot(QWidget):
    def __init__(self):
        super().__init__()

        # Create a figure and axis
        self.figure, self.ax = plt.subplots(dpi=300)
        self.canvas = FigureCanvas(self.figure)

    def define_coordinate_frame_visualisation(self, corner_coords, c_n, r_n):
        return CoordinateFrameVisualisation(corner_coords, c_n, r_n)


class CoordinateFrameVisualisation(RealTimePlot):
    def __init__(self, corner_coords, c_n, r_n):
        super().__init__()

        self.ax.clear()

        tl, tr, bl, br = corner_coords
        # center = self.state_dict_2_vector(all_state_dicts[((self.c_n/2)-1)+((self.r_n/2)-1)])

        # Set the x-axis and y-axis limits for the first subplot
        self.ax.set_xlim(tl[0], tr[0])
        self.ax.set_ylim(tl[1], bl[1])

        x_values = list(range(1, 25))
        y_values = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:r_n]]

        # Set y-axis ticks from P to A
        self.ax.set_yticks(range(len(y_values)))
        self.ax.set_yticklabels(reversed(y_values))

        self.ax.set_title('Real-Time {} well plate positioning'.format(c_n * r_n))

    def drawcoordinate(self, vector):
        self.ax.plot(vector[0], vector[1])
        self.canvas.draw()


