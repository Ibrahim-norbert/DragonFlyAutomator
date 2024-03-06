import matplotlib
from time import sleep

matplotlib.use("QtAgg")
import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QApplication, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
import logging
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from devices.wellplate import WellPlate

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))

class VisualiserWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout

        self.nextbutton = QPushButton("Next")
        self.nextbutton.clicked.connect(self.nextbutton)

    #def nextbutton(self):

class MplCanvas(FigureCanvas):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.coords = None
        self.state_dict = None
        self.figure, self.axes = plt.subplots()
        self.x = [0]
        self.y = [0]


class CoordinatePlot(MplCanvas):
    def __init__(self, stacked_widget, parent=None,):
        super().__init__(parent, stacked_widget)

        self.well_plate = WellPlate()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_figure)
        self.timer.start(100)  # update every second

    def drawcoordinate(self, vector):
        try:
            self.axes.cla()  # Clear the canvas.
            self.axes.set_xlim(self.well_plate.corners_coords[0][0], self.well_plate.corners_coords[1][0])
            self.axes.set_ylim(self.well_plate.corners_coords[0][1], self.well_plate.corners_coords[2][1])

            x_values = list(range(1, 25))
            y_values = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:self.well_plate.r_n]]

            # Set y-axis ticks from P to A
            self.axes.set_yticks(
                np.linspace(self.well_plate.corners_coords[0][1], self.well_plate.corners_coords[2][1],
                            len(y_values)))
            self.axes.set_yticklabels(reversed(y_values))

            self.axes.set_title(
                'Real-Time {} well plate positioning'.format(self.well_plate.c_n * self.well_plate.r_n))
            self.x += [vector[0]]
            self.y += [vector[1]]
            self.axes.scatter(self.x, self.y, c="r")
            self.draw()

            logger.log(level=10,
                       msg="Wells that have been selected: {} adn their coordinates {}".format(self.coords,

                                                                                               self.state_dict))
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here ", exc_info=True)

    def update_canvas(self):
        # TODO quit Qtimer from repeating itself when the checkedbuttons is empty
        # See if you can find the coordinate mapping problem

        #Check if CoordinatePlot is current widget and then proceed with plotting
        #Im doing this as I do not want Qtimer after init to switch to the exit window after startup because wellplate has no checkedbuttons attribute
        if self.well_plate.checked_buttons:
            outs = next(iter(self.well_plate.checked_buttons))
            self.state_dict, self.coords = outs
            vector = self.well_plate.state_dict_2_vector(self.state_dict)
            self.drawcoordinate(vector)
            self.well_plate.checked_buttons.remove(outs)  # Remove the processed entry
        else:
            self.hide()
            self.another_widget = AnotherWidget(self.parent())
            self.parent().layout().addWidget(self.another_widget)
            logger.log(level=10, msg="Switch to new widget")





if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Update the canvas with new data
    wellplate2 = WellPlate()
    wellplate2.load_attributes(name="384_falcon_wellplate.json")
    window = CoordinatePlot(wellplate2)


    def update_canvas():
        if wellplate2.all_well_dicts:
            key, value = next(iter(wellplate2.all_well_dicts.items()))
            window.CoordinateFrameVisualisation(wellplate2.corners_coords,
                                                       wellplate2.r_n, wellplate2.c_n,
                                                       wellplate2.state_dict_2_vector(value))
            wellplate2.all_well_dicts.pop(key)  # Remove the processed entry
            QTimer.singleShot(5000, update_canvas)


    update_canvas()
    window.show()
    sys.exit(app.exec())
