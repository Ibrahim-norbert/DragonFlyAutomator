import logging
import sys

import matplotlib
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QSizePolicy, \
    QPlainTextEdit
from imaris_ims_file_reader.ims import ims
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

matplotlib.use("QtAgg")
logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


# TODO Test the script, include labels that inform on microscope status and maybe optimize the script

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, n_plots=1, dpi=100):
        fig, self.axes = plt.subplots(ncols=n_plots, dpi=dpi)
        super().__init__(fig)

        # Set size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.x = []
        self.y = []
        self.coords = None
        self.state_dict = None


def setplotlimits(xmin, xmax, ymin, ymax, axis):
    axis.set_xlim(xmin, xmax)
    axis.set_ylim(ymin, ymax)

def setticks(x_coords, x_values, ycoords, y_values, axis):
    axis.set_xticks(x_coords)
    axis.set_xticklabels(x_values)
    axis.tick_params(axis='x', labelsize='x-small')

    # Set y-axis ticks from P to A
    axis.set_yticks(ycoords)
    axis.set_yticklabels(reversed(y_values))
    axis.tick_params(axis='y', labelsize='medium')

def createplot(tr, tl, bl, c_n, r_n, coordinate_plot, image_plot
               ):
    # Coordinate plot
    ## Set limits
    x_offset = (tr[0] - tl[0]) * 0.1
    y_offset = (tl[1] - bl[1]) * 0.1

    setplotlimits(xmin=tl[0] - x_offset, xmax=tr[0] + x_offset,
                  ymin=bl[1] - y_offset, ymax=tl[1] + y_offset, axis=coordinate_plot)

    x_values = list(range(1, c_n+1))
    y_values = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:r_n]]

    setticks(x_coords=np.linspace(tl[0], tr[0], len(x_values)),
            ycoords=np.linspace(bl[1], tl[1], len(y_values)),
            x_values=x_values, y_values=y_values, axis=coordinate_plot)

    coordinate_plot.set_title('Real-Time {} well plate positioning'.format(c_n * r_n))

    coordinate_plot.grid(which='both')

    # Image display plot
    image_plot.set_axis_off()


class CustomLogger(QObject, logging.Handler):
    new_record = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.msgs = []

    def emit(self, record):
        msg = self.format(record)
        self.new_record.emit(msg)


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)


class Automation(QRunnable):
    def __init__(self, well_plate=None, protocol=None):
        super().__init__()
        self.well_plate = well_plate
        self.protocol = protocol
        self.signal = WorkerSignals()
        self.signals_coords = WorkerSignals()
        self.signals_img = WorkerSignals()

        self.mutex = QMutex()

    @pyqtSlot()
    def run(self):
        with QMutexLocker(self.mutex):
            for wellname, wellname_string in self.well_plate.selected_wells:

                vector = self.well_plate.state_dict_2_vector(self.well_plate.all_well_dicts[wellname])

                # Emit the result from the thread
                self.signals_coords.result.emit((vector, wellname, wellname_string))

                # Move stage
                self.well_plate.automated_wp_movement(wellname)

                # Perform image acquisition
                img_path = self.protocol.processwell(vector, wellname, self.well_plate.coordinate_frame_algorithm,
                                                     self.well_plate.homography_matrix_algorithm,
                                                     self.protocol.z_increment, self.protocol.n_acquisitions,
                                                     self.protocol.protocol_name, self.protocol.image_name)

                # Emit the current image from the thread
                self.signals_img.result.emit((ims(img_path, squeeze_output=True), wellname))

            self.signal.finished.emit()


class CoordinatePlotAndImgDisplay(QWidget):
    def __init__(self, stacked_widget, parent=None):
        super().__init__(parent)
        self.imgdisplay = None
        self.coordplot = None
        self.stacked_widget = stacked_widget
        self.canvas = MplCanvas(n_plots=2)
        self.text_display = QPlainTextEdit(self)
        self.text_display.setReadOnly(True)
        self.current_coordwells = []
        self.current_imgwells = []

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.text_display)
        main_layout.addWidget(self.canvas)
        self.setLayout(main_layout)

        self.threadpool = QThreadPool(self)

    def initviz(self, well_plate, protocol):
        tl, tr, bl, _ = well_plate.corners_coords  # Top left, Top right, Bottom left
        r_n, c_n = well_plate.r_n, well_plate.c_n

        # Create the coordinate plot
        createplot(tr, tl, bl, c_n, r_n, self.canvas.axes[0], self.canvas.axes[1]
                   )

        # Start data generation
        self.startprocess(well_plate, protocol)

    def addcoorddata(self, result):
        vector, wellname, wellname_string = result
        self.canvas.x.append(vector[0])
        self.canvas.y.append(vector[1])
        self.current_coordwells.append(wellname_string)
        logger.log(level=20,
                   msg="Wells that have been selected: {} and their coordinates {}".format(wellname_string,
                                                                                           vector))

    def addimgdata(self, result):
        img, wellname = result
        self.img = img[0, :, 0].astype(float)
        self.current_imgwells.append(wellname)

    @pyqtSlot(object)
    def updatecoord(self, result):
        try:
            self.addcoorddata(result)
            if self.coordplot is None:
                self.coordplot = self.canvas.axes[0].scatter(self.canvas.x, self.canvas.y, c="r")
                self.canvas.axes[0].text(self.canvas.x[-1], self.canvas.y[-1],
                                         self.current_coordwells[-1], ha='center', va='bottom', fontsize="small")
                logger.log(level=20,
                           msg="Create the following coordinate plot of well: {} and "
                               "their coordinates {}".format(self.current_coordwells[-1],
                                                             [self.canvas.x[-1], self.canvas.y[-1]]))
            else:
                # We have a reference, we can use it to update the data for that line.
                self.coordplot.set_offsets(list(zip(self.canvas.x, self.canvas.y)))
                self.canvas.axes[0].text(self.canvas.x[-1], self.canvas.y[-1],
                                         self.current_coordwells[-1], ha='center', va='bottom', fontsize="small")
                logger.log(level=20,
                           msg="Continue the following coordinate plot of well: {} and "
                               "their coordinates {}".format(self.current_coordwells[-1],
                                                             [self.canvas.x[-1], self.canvas.y[-1]]))
            self.canvas.draw()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.exception(
                "What happened here. We have the following x {} and y {} values".format(self.canvas.x, self.canvas.y),
                exc_info=True)

    @pyqtSlot(object)
    def updateimg(self, result):
        self.addimgdata(result)
        try:
            logger.log(level=20, msg="Shape of img: {}".format(self.img.shape))
            logger.log(level=20, msg="Image has dimensions: {}".format(self.img.shape))

            if self.imgdisplay is None:
                self.imgdisplay = self.canvas.axes[1].imshow(self.img, cmap="gray")

            else:
                # We have a reference, we can use it to update the data for that line.
                self.imgdisplay.set_data(self.img)

            logger.log(level=20,
                       msg="Display the autofocused image for well {}".format(self.current_imgwells[-1]))
            self.canvas.axes[1].set_title("Image taken of well {}".format(self.current_imgwells[-1]))
            self.canvas.draw()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.exception(
                "What happened here. We have the following x {} and y {} values".format(self.canvas.x, self.canvas.y),
                exc_info=True)

    @pyqtSlot()
    def close_updater(self):
        self.text_display.appendPlainText("We are done")

    def startprocess(self, well_plate, protocol):
        worker = Automation(well_plate, protocol)
        worker.signals_coords.result.connect(self.updatecoord)
        worker.signals_img.result.connect(self.updateimg)
        worker.signal.finished.connect(self.close_updater)
        # Setup logger
        handler = CustomLogger()
        logger.addHandler(handler)
        handler.new_record.connect(self.text_display.appendPlainText)
        worker.setAutoDelete(True)
        self.threadpool.start(worker)


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
