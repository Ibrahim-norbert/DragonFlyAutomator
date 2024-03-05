import matplotlib
from time import sleep

matplotlib.use("QtAgg")
import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QApplication, QVBoxLayout, QWidget
import logging
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from devices.wellplate import WellPlate

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class MplCanvas(FigureCanvas):
    def __init__(self):
        super().__init__()
        self.coords = None
        self.state_dict = None
        self.figure, self.axes = plt.subplots()
        self.x = [0]
        self.y = [0]


class CoordinatePlot(MplCanvas):
    def __init__(self, well_plate, checked_buttons):
        super().__init__()

        self.well_plate = well_plate
        self.checked_buttons = checked_buttons

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
        if self.checked_buttons:
            outs = next(iter(self.checked_buttons))
            self.state_dict, self.coords = outs
            vector = self.well_plate.state_dict_2_vector(self.state_dict)
            self.drawcoordinate(vector)
            self.checked_buttons.remove(outs)  # Remove the processed entry
            return True
        else:
            return False


class Visualiser(QWidget):
    def __init__(self, canvas, stacked_widget=None, next_widget=None):
        super().__init__()

        self.canvas = canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.stacked_widget = stacked_widget
        self.stacked_widget.addWidget(self)
        self.stacked_widget.setCurrentWidget(self)

        self.next_widget = next_widget
        self.stacked_widget.addWidget(self.next_widget)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.Update())
        self.timer.start(10)

    def Update(self):
        out = self.canvas.update_canvas()
        if out is False:
            self.stopUpdates()
    def stopUpdates(self):
        # Stop the timer and update the label
        self.timer.stop()
        logger.log(level=10, msg="Switch to new widget")
        self.stacked_widget.setCurrentWidget(self.next_widget)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Visualiser(MplCanvas())
    # Update the canvas with new data
    wellplate2 = WellPlate()
    wellplate2.load_attributes(name="384_falcon_wellplate.json")


    def update_canvas():
        if wellplate2.all_well_dicts:
            key, value = next(iter(wellplate2.all_well_dicts.items()))
            window.canvas.CoordinateFrameVisualisation(wellplate2.corners_coords,
                                                       wellplate2.r_n, wellplate2.c_n,
                                                       wellplate2.state_dict_2_vector(value))
            wellplate2.all_well_dicts.pop(key)  # Remove the processed entry
            QTimer.singleShot(5000, update_canvas)


    update_canvas()
    window.show()
    sys.exit(app.exec())
