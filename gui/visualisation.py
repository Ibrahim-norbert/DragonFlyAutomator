import matplotlib
from time import sleep

import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QLabel, QApplication, QVBoxLayout, QWidget
import logging
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from devices.wellplate import WellPlate

matplotlib.use("QtAgg")

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class Visualiser(QWidget):
    def __init__(self, canvas):
        super().__init__()

        self.canvas = canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.figure, self.axes = plt.subplots()
        super(MplCanvas, self).__init__(self.figure)
        self.x = [0]
        self.y = [0]

    def CoordinateFrameVisualisation(self, corner_coords, r_n, c_n, vector):

        ####Use instead of linspace the actuall coordinates
        try:
            self.axes.cla()  # Clear the canvas.
            self.axes.set_xlim(corner_coords[0][0], corner_coords[1][0])
            self.axes.set_ylim(corner_coords[0][1], corner_coords[2][1])

            x_values = list(range(1, 25))
            y_values = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:r_n]]

            # Set y-axis ticks from P to A
            self.axes.set_yticks(np.linspace(corner_coords[0][1], corner_coords[2][1], len(y_values)))
            self.axes.set_yticklabels(reversed(y_values))

            self.axes.set_title('Real-Time {} well plate positioning'.format(c_n * r_n))
            self.x += [vector[0]]
            self.y += [vector[1]]
            self.axes.scatter(self.x, self.y, c="r")
            self.draw()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here ", exc_info=True)

    def update_canvas(self):

        # Get the first checked button's well_state_dict, or None if no buttons are checked

        # TODO the vectors do not appear to correspond to the coordinate space

        outs = next(iter(self.checked_buttons))
        self.state_dict, self.coords = outs
        # This executes the xzystage movement
        self.well_plate.execute_template_coords(self.state_dict)
        self.visualiser.canvas.CoordinateFrameVisualisation(self.well_plate.corners_coords,
                                                            self.well_plate.r_n, self.well_plate.c_n,
                                                            self.well_plate.state_dict_2_vector(self.state_dict))
        QTimer.singleShot(1000, self.update_canvas)
        self.checked_buttons.remove(outs)  # Remove the processed entry
        logger.log(level=10, msg="Wells that have been selected: {} adn their coordinates {}".format(self.coords,
                                                                                                     self.state_dict))


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
