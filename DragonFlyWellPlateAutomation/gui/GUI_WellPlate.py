import glob
import logging
import os
from time import sleep

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget, QLineEdit, QVBoxLayout, QComboBox, QHBoxLayout
from matplotlib import pyplot as plt

from DragonFlyWellPlateAutomation.devices.wellplate import WellPlate
from DragonFlyWellPlateAutomation.gui.helperfunctions import create_colored_label

wellplate_paths = [os.path.basename(x) for x in glob.glob(os.path.join(os.getcwd(), "models", "*WellPlate*"))]

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))
logger.debug("Directory: {}".format(os.getcwd()))


# TODO Make this script cohesive
# TODO Find out what dynamical means in method context
# TODO Test the script
# TODO Switch order of widgets enter is below add well plate name and edit boxes must be larger

class CreateNewWellPlateTemplate(QWidget):
    def __init__(self, stacked_widget, well_plate):
        super().__init__()

        self.well_plate = well_plate
        self.stacked_widget = stacked_widget

        horizonti_tl = QHBoxLayout()
        self.column_n = QLineEdit(parent=self)
        self.column_n.setPlaceholderText("Column number")
        horizonti_tl.addWidget(self.column_n)
        self.row_n = QLineEdit(parent=self)
        self.row_n.setPlaceholderText("Row number")
        horizonti_tl.addWidget(self.row_n)

        stackie_tl = QVBoxLayout()
        stackie_tl.addWidget(
            create_colored_label("Please confirm the number of columns and rows\nin the well plate: ", self))
        stackie_tl.addLayout(horizonti_tl)

        stackie_tm = QVBoxLayout()
        stackie_tm.addWidget(create_colored_label("Select type of coordinate frame prediction: ", self))
        self.typegridpred = QComboBox(parent=self)
        for gridpred in self.well_plate.coordinate_frame_algorithms:
            self.typegridpred.addItem(gridpred)
        stackie_tm.addWidget(self.typegridpred)

        stackie_tr = QVBoxLayout()
        stackie_tr.addWidget(create_colored_label("Select type of homography matrix estimator: ", self))
        self.typehomopred = QComboBox(parent=self)
        for homopred in self.well_plate.homography_matrix_algorithms:
            self.typehomopred.addItem(homopred)
        stackie_tr.addWidget(self.typehomopred)

        horizonti_top = QHBoxLayout()
        horizonti_top.addLayout(stackie_tl)
        horizonti_top.addLayout(stackie_tm)
        horizonti_top.addLayout(stackie_tr)

        horizontie_mt = QHBoxLayout()
        horizontie_mt.addWidget(create_colored_label(
            "Please move the stage to the following wells and press read to confirm their coordinates "
            ": ", self))
        self.placeholder_coordinates = create_colored_label("", self)
        horizontie_mt.addWidget(self.placeholder_coordinates)

        horizonti_ml = QHBoxLayout()
        self.dropdown = QComboBox(self)
        options = list(self.well_plate.homography_source_coordinates.keys())
        for x in options:
            self.dropdown.addItem(x)
        horizonti_ml.addWidget(self.dropdown)
        self.read_button = QPushButton("Read", self)
        self.read_button.clicked.connect(self.read_well_coordinate)
        horizonti_ml.addWidget(self.read_button)

        stackie_middle = QVBoxLayout()
        stackie_middle.addLayout(horizontie_mt)
        stackie_middle.addLayout(horizonti_ml)

        horizonti_lower = QHBoxLayout()
        horizonti_lower.addWidget(create_colored_label("To save well plate template please add\nmanufacturer name "
                                                       "and model ID. If not, leave empty", self))

        self.partnumber = QLineEdit(parent=self)
        self.partnumber.setPlaceholderText("Model ID")
        horizonti_lower.addWidget(self.partnumber)
        self.manufacturer = QLineEdit(parent=self)
        self.manufacturer.setPlaceholderText("Manufacturer name")
        horizonti_lower.addWidget(self.manufacturer)

        self.enter_button = QPushButton("Enter", parent=self)
        self.enter_button.clicked.connect(self.enter_button_click)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(horizonti_top)
        main_layout.addLayout(stackie_middle)
        main_layout.addLayout(horizonti_lower)
        main_layout.addWidget(self.enter_button)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

    def read_well_coordinate(self):

        try:
            # Read and save well plate corners
            self.well_plate.homography_source_coordinates[self.dropdown.currentText()] = self.well_plate.get_state(
                test_key=self.dropdown.currentText())

            # Return them as vectors
            vector = self.well_plate.state_dict_2_vector(
                self.well_plate.homography_source_coordinates[self.dropdown.currentText()])

            # Display them in GUI
            self.placeholder_coordinates.setText(str(vector))

            logger.log(level=10, msg="Well: " + self.dropdown.currentText() + " - " + str(vector))

            # Once all corners are read, log the values
            if None not in self.well_plate.homography_source_coordinates.values():
                final = self.well_plate.homography_source_coordinates.items()
                logger.log(level=10, msg="Final coordinates: " + str(final))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.exception("Must select one of the well options first before ", exc_info=True)

    def enter_button_click(self):

        try:
            if None not in self.well_plate.homography_source_coordinates.values():

                # Compute the wellplate grid
                vectors, well_names, length, height, x_spacing = self.well_plate.predict_well_coords(
                    int(self.column_n.text()), int(self.row_n.text()), self.well_plate.homography_source_coordinates,
                    self.typegridpred.currentText(), self.typehomopred.currentText())

                # Save well plate template
                if self.partnumber.text() and self.manufacturer.text():
                    self.well_plate.save_attributes2json(self.manufacturer.text(), self.partnumber.text())
                    logger.log(level=10, msg="Saved new well plate template")

                # Switch to frame three
                self.stacked_widget.switch2WPbuttongrid()

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.exception("What happened here ", exc_info=True)


class Calibration(QWidget):
    def __init__(self, wellplate, buttons, wellname, parent=None):
        super().__init__(parent=parent)

        self.wellplate = wellplate

        main_layout = QVBoxLayout(self)
        self.calibrationdisplay = create_colored_label(parent=self, text="")
        self.calibrationdisplay.setWordWrap(True)
        main_layout.addWidget(self.calibrationdisplay)

        horizonti_ml = QHBoxLayout()
        self.placeholder_coordinates = create_colored_label("", self)
        self.placeholder_coordinates.setWordWrap(True)
        horizonti_ml.addWidget(self.placeholder_coordinates)
        self.read_button = QPushButton("Read", self)
        self.read_button.clicked.connect(self.read_calibration_well)
        horizonti_ml.addWidget(self.read_button)

        main_layout.addLayout(horizonti_ml)
        self.setLayout(main_layout)
        self.buttons = buttons

        self.move2calibration_well(wellname)

    def move2calibration_well(self, wellname):
        self.wellplate.automated_wp_movement(wellname)  # Delay #Give message on GUI to inform to refrain from closing
                                                        # the application

        self.calibrationdisplay.setText("Have we arrived on mid-point of well {} ?"
                                        "If not, please move stage accordingly, then press read and "
                                        "afterwards enter.".format(wellname))

    def read_calibration_well(self):
        state = self.wellplate.get_state(test_key="Bottom right well")
        self.wellplate.bottomright_calibration = self.wellplate.state_dict_2_vector(state)
        self.placeholder_coordinates.setText("Current coordinates: {}".format(self.wellplate.bottomright_calibration))
        [button.setEnabled(True) for button in self.buttons]


class WellAsButton(QPushButton):
    def __init__(self, text=None, wellname_string=None, parent=None, coordinates=None, xyz_stage_state=None):
        super().__init__(text=wellname_string, parent=parent)

        self.coordinates = coordinates  # integer coords
        self.wellname = text
        self.wellname_string = wellname_string
        self.color = "#00aa00"
        self.setStyleSheet("background-color: {}; color: #ffffff;".format(self.color))
        self.setCheckable(True)
        self.setEnabled(False)
        self.well_state_dict = xyz_stage_state

    def handleButtonClick(self):
        if self.isChecked():
            self.color = "#ff0000"
        else:
            self.color = "#00aa00"
        self.setStyleSheet("background-color: {}; color: #ffffff;".format(self.color))

        print(f"{self.text()} {'Selected' if self.isChecked() else 'Deselected'}")

    def mouseDoubleClickEvent(self, event):
        self.toggle()  # Toggle the check state
        self.handleButtonClick()


class CustomButtonGroup(QWidget):
    def __init__(self, stacked_widget, well_plate):
        super().__init__()

        self.main_layout = QHBoxLayout(self)
        self.buttons = None
        self.enter_button = None
        self.checked_buttons = None
        self.stacked_widget = stacked_widget
        self.well_plate = well_plate

    def createcalibrationwidget(self, well_plate, buttons, wellname):

        self.calibration_widget = Calibration(well_plate, buttons, wellname, parent=self)
        self.main_layout.addWidget(self.calibration_widget)

    def creatbuttongrid(self):

        layout = QGridLayout()

        self.buttons = []

        for wellname in self.well_plate.wellnames:
            wellname_string, r_str, c_str, r, c = self.well_plate.mapwellintegercoords2alphabet(wellname)
            button = WellAsButton(text=wellname, parent=self, coordinates=(r, c), wellname_string=wellname_string)
            button.clicked.connect(button.handleButtonClick)
            self.buttons.append(button)
            layout.addWidget(button, button.coordinates[0], button.coordinates[1])
            button.setFixedSize(25, 15)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        self.enter_button = QPushButton("Enter", parent=self)
        self.enter_button.clicked.connect(self.handleEnterPressed)
        main_layout.addWidget(self.enter_button)

        self.createcalibrationwidget(self.well_plate, self.buttons, self.well_plate.wellnames[-1])
        self.main_layout.addLayout(main_layout)
        self.setLayout(self.main_layout)

    def handleEnterPressed(self):
        try:

            # Add to well plate instance
            self.well_plate.selected_wells = [(button.wellname, button.wellname_string) for button
                                              in
                                              self.buttons if
                                              button.isChecked()]
            logger.log(level=20, msg="Wells that have been selected: {}".format([x[-1] for x in
                                                                                 self.well_plate.selected_wells]))

            # Automatic updater -> threading ?
            self.stacked_widget.switch2Protocol()  # -> Underneath for loop or in parallel to

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.exception("What happened here ", exc_info=True)

