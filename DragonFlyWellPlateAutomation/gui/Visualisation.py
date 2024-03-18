import matplotlib
import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QSizePolicy
import logging
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from DragonFlyWellPlateAutomation.gui.helperfunctions import create_colored_label

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

    def __init__(self, parent=None, n_plots=1,  width=None, height=None, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(int("11{}".format(n_plots)))
        self.sizepolicy = QSizePolicy()
        self.sizepolicy.setHeightForWidth(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.x = []
        self.y = []
        self.coords = None
        self.state_dict = None
        super(MplCanvas, self).__init__(fig)


class CoordinatePlotAndImgDisplay(QWidget):
    def __init__(self, stacked_widget, well_plate, protocol, parent=None):
        super().__init__(parent)
        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.

        # Plot
        self.canvas = MplCanvas(parent=self, n_plots=2, dpi=300)
        self._plot_ref = None




        self.image_array = None
        self.protocol = protocol
        self.data = None
        self.doneplotting = True


        layout1 = QVBoxLayout(self)  # TODO Label should display all current logs relating to autofocus and xyz stage
        self.text_display = create_colored_label(" ", self)
        self.img_display = QPixmap()
        layout1.addWidget(self.text_display)
        layout1.addWidget(self.img_display)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.canvas)

        self.setLayout(main_layout)

        self.stacked_widget = stacked_widget

        self.well_plate = well_plate

        self.DF_notengaged = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_canvas)
        # update every second

        self.exit = False

    def initviz(self, tl, bl, tr, br, r_n, c_n):

        self.data = self.well_plate.selected_wells


        self.canvas.axes[0].set_xlim(self.well_plate.corners_coords[0][0],
                                  self.well_plate.corners_coords[1][0] + (self.well_plate.corners_coords[1][0] * 0.1))
        self.canvas.axes.set_ylim(self.well_plate.corners_coords[0][1],
                                  self.well_plate.corners_coords[2][1] + (self.well_plate.corners_coords[2][1] * 0.1))

        x_values = list(range(1, c_n))
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

    def display_img_from_array(self):

        # Convert NumPy array to QImage
        height, width, channel = self.image_array.shape
        bytes_per_line = 3 * width
        self.img_display.fromImage(QImage(self.image_array.data, width, height, bytes_per_line, QImage.Format_RGB888))

    def display_text_updates(self):
        self.text_display.setText()

    def drawcoordinate(self, vector, wellname):
        try:
            # First time we have no plot reference, so do a normal plot.
            # .plot returns a list of line <reference>s, as we're
            # only getting one we can take the first element.
            self.canvas.x += [vector[0]]
            self.canvas.y += [vector[1]]
            # Note: we no longer need to clear the axis.
            if self._plot_ref is None:
                self.canvas.axes.scatter(self.canvas.x, self.canvas.y)
                logger.log(level=20,
                           msg="Wells that have been selected: {} and their coordinates {}".format(wellname,

                                                                                                   vector))
            else:
                # We have a reference, we can use it to update the data for that line.
                self._plot_ref.set_ydata(self.canvas.y)
                self._plot_ref.set_ydata(self.canvas.x)

            self.canvas.draw()



        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception(
                "What happened here. We have the following x {} and y {} values".format(self.canvas.x, self.canvas.y),
                exc_info=True)
            self.timer.timeout()

    def update_canvas(self):

        """Updates the scatterplot using the QTimer events."""

        # Only proceeds if data exists and DragonFly has completed a process
        if self.well_plate.selected_wells and self.DF_notengaged is True:

            # Start DragonFly process
            self.DF_notengaged = False
            state_dict, coords, wellname = next(iter(self.well_plate.selected_wells))

            # Draw graph only when xyz-stage has arrived at well
            if self.well_plate.move2coord(state_dict) is False:  # Delay

                # TODO a) To check quality of current session: compare linearspacing coordinates to linear correction matrix
                # TODO b) To check quality between current and subsequent session: compare current session to homography prediction
                # TODO c) To check quality of subsequent session: compare Homography with nonlinear correction and Homography calibration

                vector = self.well_plate.state_dict_2_vector(state_dict)

                self.drawcoordinate(vector, wellname)

                # Perform autofocus
                self.protocol.autofocusing(wellname=wellname)  # Significant delay

                # Obtain image with current protocol
                self.protocol.image_acquisition(wellname=wellname)  # Delay

                # Once data has been processed, we remove it
                self.data.remove((state_dict, coords, wellname))

                # End DragonFly process
                self.DF_notengaged = True

            # Maybe add text object above coordinate point indicating the xyz stage cartesian coordinate
        elif not self.well_plate.selected_wells:
            self.timer.stop()
            logger.log(level=20, msg="All wells have been dealt with. The associated variables have been saved.")
            self.protocol.autofocus.save2DT_excel()
            sys.exit()
            # logger.log(level=20, msg="Switch to save window")


if __name__ == '__main__':
    # TODO Correct this
    app = QApplication(sys.argv)
    # Update the canvas with new data
    wellplate2 = WellPlate()
    wellplate2.load_attributes(name="384_falcon_wellplate.json")
    window = CoordinatePlotAndImgDisplay(wellplate2)


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
