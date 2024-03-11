import matplotlib
import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QPushButton
import logging
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt

matplotlib.use("QtAgg")
logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


# TODO Test the script, include labels that inform on microscope status and maybe optimize the script

class VisualiserWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout

        self.nextbutton = QPushButton("Next")
        self.nextbutton.clicked.connect(self.nextbutton)

    # def nextbutton(self):


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.coords = None
        self.state_dict = None
        self.figure, self.axes = plt.subplots()
        self.x = [0]
        self.y = [0]


class CoordinatePlot(QWidget):
    def __init__(self, stacked_widget, well_plate, protocol, parent=None):
        super().__init__(parent)
        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.

        self.protocol = protocol
        self.data = None
        self.doneplotting = True
        self.canvas = MplCanvas()
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.canvas)
        self.setLayout(main_layout)

        self.stacked_widget = stacked_widget

        self.well_plate = well_plate

        self.DF_notengaged = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_canvas)
        # update every second

        self.exit = False

    def initviz(self):

        self.data = self.well_plate.selected_wells

        self.canvas.axes.set_xlim(self.well_plate.corners_coords[0][0],
                                  self.well_plate.corners_coords[1][0] + (self.well_plate.corners_coords[1][0] * 0.1))
        self.canvas.axes.set_ylim(self.well_plate.corners_coords[0][1],
                                  self.well_plate.corners_coords[2][1] + (self.well_plate.corners_coords[2][1] * 0.1))

        x_values = list(range(1, 25))
        y_values = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:self.well_plate.r_n]]

        self.canvas.axes.set_xticks(
            np.linspace(self.well_plate.corners_coords[0][0], self.well_plate.corners_coords[1][0],
                        len(x_values)))

        # Set y-axis ticks from P to A
        self.canvas.axes.set_yticks(
            np.linspace(self.well_plate.corners_coords[0][1], self.well_plate.corners_coords[2][1],
                        len(y_values)))
        self.canvas.axes.set_yticklabels(reversed(y_values))

        self.canvas.axes.set_title(
            'Real-Time {} well plate positioning'.format(self.well_plate.c_n * self.well_plate.r_n))

        self.canvas.axes.grid(which='both')

        self.timer.start(1000)

    def drawcoordinate(self, vector, coords):
        try:
            self.canvas.x += [vector[0]]
            self.canvas.y += [vector[1]]

            self.canvas.axes.scatter(self.canvas.x, self.canvas.y)
            self.canvas.draw()

            logger.log(level=20,
                       msg="Wells that have been selected: {} and their coordinates {}".format(coords,

                                                                                               vector))
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception(
                "What happened here. We have the following x {} and y {} values".format(self.canvas.x, self.canvas.y),
                exc_info=True)
            self.timer.timeout()

    def update_canvas(self):

        """Updates the scatterplot using the QTimer events."""

        # Only proceeds if data exists and DragonFly has completed a process
        if self.data and self.DF_notengaged is True:

            # Start DragonFly process
            self.DF_notengaged = False
            state_dict, coords = next(iter(self.data))

            # Draw graph only when xyz-stage has arrived at well
            if self.well_plate.move2coord(state_dict) is False:  # Delay

                # Get protocol from GUI PRotocol ?
                # Obtain images of well content
                self.protocol.image_acquisition(wellcoord=coords)  # Delay

                vector = self.well_plate.state_dict_2_vector(state_dict)

                self.drawcoordinate(vector, coords)

                # Once data has been processed, we remove it
                self.data.remove((state_dict, coords))

                # End DragonFly process
                self.DF_notengaged = True

            # Maybe add text object above coordinate point indicating the xyz stage cartesian coordinate
        elif not self.data:
            self.timer.stop()
            self.protocol.autofocus.save2DT_excel()
            self.stacked_widget.switch2WPsavewindow()
            logger.log(level=20, msg="Switch to save window")


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
