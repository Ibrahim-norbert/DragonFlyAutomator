import glob
import logging
import os
import sys
from time import sleep
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget, QLineEdit, QVBoxLayout, QComboBox, QHBoxLayout
from matplotlib import pyplot as plt
from DragonFlyWellPlateAutomation.devices.wellplate import WellPlate
from helperfunctions import create_colored_label

wellplate_paths = [os.path.basename(x) for x in glob.glob(os.path.join(os.getcwd(), "models", "*WellPlate*"))]

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))
logging.debug("Directory: {}".format(os.getcwd()))


# TODO Make this script cohesive
# TODO Find out what dynamical means in method context
# TODO Test the script

class CreateNewWellPlateTemplate(QWidget):
    def __init__(self, stacked_widget, well_plate):
        super().__init__()

        # TODO Add functionality to choose between methods of learning the homography matrix

        self.well_plate = well_plate
        self.stacked_widget = stacked_widget

        self.column_n = QLineEdit(parent=self)
        self.column_n.setPlaceholderText("Column number")
        self.row_n = QLineEdit(parent=self)
        self.row_n.setPlaceholderText("Row number")

        layout1 = QHBoxLayout()
        layout1.addWidget(self.column_n)
        layout1.addWidget(self.row_n)

        label1 = create_colored_label("Please confirm the number of columns and rows in the well plate: ", self)
        layout2 = QVBoxLayout()
        layout2.addWidget(label1)
        layout2.addLayout(layout1)

        self.read_button = QPushButton("Read", self)
        self.read_button.clicked.connect(self.read_well_coordinate)
        self.dropdown = QComboBox(self)
        options = list(self.well_plate.well_plate_req_coords.keys())
        for x in options:
            self.dropdown.addItem(x)

        layout3 = QHBoxLayout()
        layout3.addWidget(self.read_button)
        layout3.addWidget(self.dropdown)

        self.placeholder_coordinates = create_colored_label("", self)
        label2 = QHBoxLayout()
        label2.addWidget(create_colored_label(
            "Please move the stage to the following wells and press read to confirm their coordinates "
            ": ", self))
        label2.addWidget(self.placeholder_coordinates)

        layout4 = QVBoxLayout()
        layout4.addLayout(label2)
        layout4.addLayout(layout3)

        self.enter_button = QPushButton("Enter", parent=self)
        self.enter_button.clicked.connect(self.enter_button_click)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(layout2)
        main_layout.addLayout(layout4)
        main_layout.addWidget(self.enter_button)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout1 = QHBoxLayout()
        layout1.addWidget(create_colored_label("To save well plate template please add manufacturer name "
                                               "and model ID. If not, leave empty", self))

        self.partnumber = QLineEdit(parent=self)
        self.partnumber.setPlaceholderText("Please enter model ID")
        layout1.addWidget(self.partnumber)
        self.manufacturer = QLineEdit(parent=self)
        self.manufacturer.setPlaceholderText("Please enter manufacturer name")
        layout1.addWidget(self.manufacturer)

        main_layout.addLayout(layout1)
        self.setLayout(main_layout)

    def read_well_coordinate(self):

        try:
            # Read and save well plate corners
            self.well_plate.well_plate_req_coords[self.dropdown.currentText()] = self.well_plate.get_state(
                test_key=self.dropdown.currentText())

            # Return them as vectors
            vector = self.well_plate.state_dict_2_vector(
                self.well_plate.well_plate_req_coords[self.dropdown.currentText()])

            # Display them in GUI
            self.placeholder_coordinates.setText(str(vector))

            logging.log(level=10, msg="Well: " + self.dropdown.currentText() + " - " + str(vector))

            # Once all corners are read, log the values
            if None not in self.well_plate.well_plate_req_coords.values():
                final = self.well_plate.well_plate_req_coords.items()
                logging.log(level=10, msg="Final coordinates: " + str(final))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("Must select one of the well options first before ", exc_info=True)

    def enter_button_click(self):

        try:
            if None not in self.well_plate.well_plate_req_coords.values():

                # Save well plate template
                if self.partnumber.text() and self.manufacturer.text():
                    self.well_plate.save_attributes2json(self.manufacturer.text(), self.partnumber.text())
                    logger.log(level=10, msg="Saved new well plate template")

                # TODO Make learning homography algorithm an attribute and also grid making algorithm

                # Compute the wellplate grid
                self.well_plate.predict_well_coords(int(self.column_n.text()), int(self.row_n.text()))

                # Switch to frame three
                self.stacked_widget.switch2WPbuttongrid()

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here ", exc_info=True)


class WellAsButton(QPushButton):
    def __init__(self, text, parent, coordinates, xyz_stage_state):
        super().__init__(text=text, parent=parent)

        self.coordinates = coordinates #integer coords
        self.wellname = text
        self.color = "#00aa00"
        self.setStyleSheet("background-color: {}; color: #ffffff;".format(self.color))
        self.setCheckable(True)
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

        self.buttons = None
        self.enter_button = None
        self.checked_buttons = None
        self.stacked_widget = stacked_widget
        self.well_plate = well_plate

    def creatbuttongrid(self):

        layout = QGridLayout()

        self.buttons = []

        for well_key, state_dict in self.well_plate.all_well_dicts.items():
            wellname, r_str, c_str, r, c = self.well_plate.mapwellintegercoords2alphabet(well_key)
            button = WellAsButton(text=wellname, parent=self, coordinates=(r, c), xyz_stage_state=state_dict)
            button.clicked.connect(button.handleButtonClick)
            self.buttons.append(button)
            layout.addWidget(button, button.coordinates[0], button.coordinates[1])
            button.setFixedSize(25, 15)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(layout)
        self.enter_button = QPushButton("Enter", parent=self)
        self.enter_button.clicked.connect(self.handleEnterPressed)
        main_layout.addWidget(self.enter_button)

        self.setLayout(main_layout)

    def handleEnterPressed(self):
        try:
            self.checked_buttons = [(button.well_state_dict, button.coordinates, button.wellname) for button in self.buttons if
                                    button.isChecked()]

            logging.log(level=10, msg="Wells that have been selected: {}".format(self.checked_buttons))

            # Add to well plate instance
            self.well_plate.selected_wells = self.checked_buttons

            # Automatic updater -> threading ?
            self.stacked_widget.switch2Protocol()  # -> Underneath for loop or in parallel to

            # And with for loop -> multithreading?

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here ", exc_info=True)





if __name__ == '__main__':

    # TODO Correct this
    well_plate = WellPlate()
    well_plate.load_attributes(name="384_falcon_wellplate.json")

    fig, axes = plt.subplots(dpi=300)

    axes.set_xlim(well_plate.corners_coords[0][0], well_plate.corners_coords[1][0])
    axes.set_ylim(well_plate.corners_coords[0][1], well_plate.corners_coords[2][1])

    x_values = list(range(1, 25))
    y_values = [x for x in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[:well_plate.r_n]]

    # Set y-axis ticks from P to A
    axes.set_yticks(
        np.linspace(well_plate.corners_coords[0][1], well_plate.corners_coords[2][1],
                    len(y_values)))
    axes.set_yticklabels(reversed(y_values))

    axes.set_title(
        'Real-Time {} well plate positioning'.format(well_plate.c_n * well_plate.r_n))

    for key, value in well_plate.all_well_dicts.items():
        data = well_plate.state_dict_2_vector(value)
        axes.scatter(data[0], data[1])
        sleep(0.1)
        plt.show()

    # def update_canvas():
    #     if wellplate2.all_well_dicts:
    #         key, value = next(iter(wellplate2.all_well_dicts.items()))
    #         window.canvas.CoordinateFrameVisualisation(wellplate2.corners_coords,
    #                                                    wellplate2.r_n, wellplate2.c_n,
    #                                                    )
    #         wellplate2.all_well_dicts.pop(key)  # Remove the processed entry
    #         QTimer.singleShot(5000, update_canvas)
    #
    # update_canvas()
    # window.show()
    # sys.exit(app.exec())
