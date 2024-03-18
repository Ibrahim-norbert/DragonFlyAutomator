import copy
import traceback

import matplotlib
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, QLabel
import logging
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from imaris_ims_file_reader.ims import ims
from DragonFlyWellPlateAutomation.gui.helperfunctions import create_colored_label

matplotlib.use("QtAgg")
logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


# TODO Test the script, include labels that inform on microscope status and maybe optimize the script

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


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class QtWorker(QRunnable):
    """Worker thread"""

    def __init__(self, fn, *args, **kwargs):
        super(QtWorker, self).__init__()
        # Store constructor arguments (re-used for processing)
        self.is_working = False
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """My code"""
        # Retrieve args/kwargs here; and fire processing using them
        self.is_working = True
        try:
            result = self.fn(
                *self.args, **self.kwargs
            )

        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.finished.emit()


class Automation(QRunnable):
    def __init__(self, well_plate, protocol):
        super().__init__()
        self.well_plate = well_plate
        self.protocol = protocol
        self.signals_coords = WorkerSignals()
        self.signals_img = WorkerSignals()
       # self.mutex = QMutex()

    @pyqtSlot()
    def run(self):

        for state_dict, coords, wellname in self.well_plate.selected_wells:

            if self.well_plate.wellbywell is True:
                vector = self.well_plate.mapwell2xyzstagecoords(coords[1], coords[0],
                                                                non_linear_correction=self.protocol.non_linear_correction)
                state_dict = self.well_plate.vector_2_state_dict(vector)

            result = self.well_plate.state_dict_2_vector(state_dict), wellname

            # Emit the result from the thread
            self.signals_coords.result.emit(result)

            # Move stage
            vector, wellname = self.well_plate.automated_wp_movement((state_dict, coords, wellname))

            # Perform image acquisition
            img_path = self.protocol.processwell(vector, wellname, self.well_plate.wellbywell,
                                                 self.well_plate.coordinate_frame_algorithm,
                                                 self.well_plate.homography_matrix_algorithm)

            # Emit the current image from the thread
            self.signals_img.result.emit(img_path)


class CoordinatePlotAndImgDisplay(QWidget):
    def __init__(self, stacked_widget, well_plate, protocol, parent=None):
        super().__init__(parent)
        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.

        # Plot
        self.canvas = MplCanvas(parent=self, n_plots=2, dpi=300)
        self._plot_ref = None




        self.current_wells = []
        self.protocol = protocol
        self.nocoordsleft = None
        self.image_array = None
        self.img = []
        self.data = None
        self.doneplotting = True

        layout1 = QVBoxLayout()
        self.text_display = create_colored_label(" ", self)
        self.img_display = QLabel()
        layout1.addWidget(self.text_display)
        layout1.addWidget(self.img_display)

        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.canvas)
        main_layout.addLayout(layout1)
        self.setLayout(main_layout)

        self.stacked_widget = stacked_widget

        self.well_plate = well_plate

        self.DF_notengaged = True

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.drawcoordinate)
        self.timer.start(1000)

        # update every second

        self.exit = False



        self.threadpool = QThreadPool()

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

        self.startprocess()
    @pyqtSlot(object)
    def addcoorddata(self, result):
        vector, wellname = result
        self.canvas.x += [vector[0]]
        self.canvas.y += [vector[1]]
        self.current_wells += [wellname]
        logger.log(level=20,
                   msg="Wells that have been selected: {} and their coordinates {}".format(wellname,

                                                                                           vector))

    @pyqtSlot(object)
    def display_img_from_array(self, img_path):
        """Updates the scatterplot using the QTimer events."""
        try:
            # TODO we should look into this
            img = ims(img_path, squeeze_output=True)
            logger.log(level=20, msg="Shape of img: {}".format(img.shape))
            time, channel, z, height, width = img.shape
            input_img = img[0, :, 0].astype(np.uint8)
            logger.log(level=20, msg="Image has dimensions: {}".format(input_img.shape))
            bytes_per_line = 3 * width
            image = QImage(input_img.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.img_display.setPixmap(pixmap)
        except Exception as e:
            logger.log(level=40, msg="What happened here {}".format(e))

    def drawcoordinate(self):
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
            logger.exception(
                "What happened here. We have the following x {} and y {} values".format(self.canvas.x, self.canvas.y),
                exc_info=True)

    # TODO Appears to be the best option.

    def startprocess(self):
        self.text_display.setText(logger.handlers[-1].log_messages[-1])
        worker = Automation(self.well_plate, self.protocol)
        worker.signals_coords.result.connect(self.addcoorddata, Qt.ConnectionType.BlockingQueuedConnection)
        worker.signals_img.result.connect(self.display_img_from_array,Qt.ConnectionType.BlockingQueuedConnection)
        worker.setAutoDelete(True)
        self.threadpool.start(worker)

    def close(self):
        self.text_display.setText("We are done")


def main():
    from DragonFlyWellPlateAutomation.devices.wellplate import WellPlate
    from DragonFlyWellPlateAutomation.devices.protocol import Protocol
    # TODO Correct this
    app = QApplication(sys.argv)
    # Update the canvas with new data
    p = Protocol("/media/ibrahim/Extended Storage/cloud/Internship/bioquant/348_wellplate_automation/test_rn")
    wellplate2 = WellPlate()
    wellplate2.load_attributes(name="384_WellPlate_12345_Falcon.json")
    window = CoordinatePlot(well_plate=wellplate2, protocol=p)
    window.initviz()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
