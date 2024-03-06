import glob
import logging
import os
import sys
from time import sleep
import numpy as np
from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget, QLineEdit, QVBoxLayout, QComboBox, QHBoxLayout, \
    QApplication
from PyQt6.QtCore import Qt, QTimer
from matplotlib import pyplot as plt
from devices.micrscope import Microscope
from devices.protocol import Protocol
from devices.wellplate import WellPlate
from gui.helperfunctions import create_colored_label

wellplate_paths = [os.path.basename(x) for x in glob.glob(os.path.join(os.getcwd(), "models", "*WellPlate*"))]

logger = logging.getLogger(__name__)
logger.info("This log message is from another module.")
logging.debug("Directory: {}".format(os.getcwd()))


# TODO Make this script cohesive
# TODO Find out what dynamical means in method context
class SelectWellPlateDimensions(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.stacked_widget = stacked_widget

        self.dropdown = QComboBox(self)
        for path in wellplate_paths:
            self.dropdown.addItem(path)

        layout1 = QVBoxLayout()
        self.selectwell_button = QPushButton("Select Well Plate", self)
        self.selectwell_button.clicked.connect(self.selectwellplate)
        self.addwell_button = QPushButton("Add new Well Plate", self)
        self.addwell_button.clicked.connect(self.addwell)
        layout1.addWidget(self.selectwell_button)
        layout1.addWidget(self.addwell_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.dropdown)
        main_layout.addLayout(layout1)

        self.well_plate = WellPlate()

    def selectwellplate(self):
        try:
            path = self.dropdown.currentText()
            self.well_plate.load_attributes(path)
            self.stacked_widget.switch2WPbuttongrid()
            
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here: ", exc_info=True)

    def addwell(self):
        try:
            self.stacked_widget.switch2WPnew()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here: ", exc_info=True)


class WellPlateDimensions(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.well_plate = WellPlate()
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
        self.setLayout(main_layout)

    def read_well_coordinate(self):

        try:
            self.well_plate.well_plate_req_coords[self.dropdown.currentText()] = self.well_plate.get_state(
                test_key=self.dropdown.currentText())
            # self.well_plate.well_plate_req_coords[self.dropdown.currentText()] = self.well_plate.get_state()
            vector = self.well_plate.state_dict_2_vector(
                self.well_plate.well_plate_req_coords[self.dropdown.currentText()])
            self.placeholder_coordinates.setText(str(vector))
            logging.log(level=10, msg="Well: " + self.dropdown.currentText() + " - " + str(vector))
            if None not in self.well_plate.well_plate_req_coords.values():
                final = self.well_plate.well_plate_req_coords.items()
                logging.log(level=10, msg="Final coordinates: " + str(final))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("Must select one of the well options first before ", exc_info=True)

    def enter_button_click(self):

        try:
            if None not in self.well_plate.well_plate_req_coords.values():
                
                #Compute the wellplate grid
                self.well_plate.predict_well_coords(int(self.column_n.text()), int(self.row_n.text()))
                
                # Switch to frame three
                self.stacked_widget.switch2WPbuttongrid()
                
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here ", exc_info=True)


class WellAsButton(QPushButton):
    def __init__(self, text, parent, coordinates, well_coordinate):
        super().__init__(text=text, parent=parent)

        self.coordinates = coordinates
        self.color = "#00aa00"
        self.setStyleSheet("background-color: {}; color: #ffffff;".format(self.color))
        self.setCheckable(True)
        self.well_state_dict = well_coordinate

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
    def __init__(self, stacked_widget):
        super().__init__()

        #self.protocol = Protocol()
        self.well_plate = WellPlate()

        layout = QGridLayout()

        self.buttons = []
        for key, well_state_dict in self.well_plate.all_well_dicts.items():
            r, c = int(key.split(" ")[0]), int(key.split(" ")[-1])
            label = "abcdefghijklmnopqrstuvwxyz".upper()[r] + key.split(" ")[-1]
            button = WellAsButton(text=label, parent=self, coordinates=(r, c), well_coordinate=well_state_dict)
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

        self.stacked_widget = stacked_widget


    def handleEnterPressed(self):
        try:
            self.checked_buttons = [(button.well_state_dict, button.coordinates) for button in self.buttons if
                                    button.isChecked()]

            logging.log(level=10, msg="Wells that have been selected: {}".format(self.checked_buttons))

            
            #Automatic updater -> threading ?
            self.stacked_widget.switch2WPrtplotter() #-> Underneath for loop or in parallel to it ??

            #And with for loop -> multithreading?
            for out in self.checked_buttons:
                state_dict, coords = out
                self.well_plate.currentwellposition = out
                self.well_plate.move2coord(state_dict) #3 second delay

                #Move well plate
                sleep(3)
                
            



        
            # for button in self.checked_buttons:
            # self.well_plate.execute_template_coords(button[0].values())
            # logging.log(level=10, msg="Well coordinates: {}".format(button[1]))
            # self.protocol.z_stack(button[1])
            


            # Perform image acquisition of different Z positions
            # self.run_protocol()
            # TODO See if there is a cleaner method for this
            ## TODO Maybe add the self.wellplate into the consturctor and the timer too ? and make it a child ?
            # Visualiser(CoordinatePlot(well_plate=self.well_plate,
            #                          checked_buttons=self.checked_buttons),
            ##          stacked_widget=self.stacked_widget,
            #        next_widget=SaveWindow(self.well_plate, stacked_widget=self.stacked_widget))

            # execute stage

            # execute pictures

            # execute save

            # self.visualiser.Update()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here ", exc_info=True)


class SaveWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.wellplate = WellPlate()

        layout = QHBoxLayout()
        layout.addWidget(create_colored_label("Would you like to save this new coordinate transformation ?", self))
        self.yes_button = QPushButton("Yes", parent=self)
        self.yes_button.clicked.connect(self.save)
        layout.addWidget(self.yes_button)
        self.no_button = QPushButton("No", parent=self)
        self.no_button.clicked.connect(self.save)
        layout.addWidget(self.no_button)
        self.setLayout(layout)

        self.stacked_widget = stacked_widget

    def save(self):


            # layout = QHBoxLayout()
            # self.manufacturer = QLineEdit(parent=self)
            # self.manufacturer.setPlaceholderText("Manufacturer name")
            # layout.addWidget(self.manufacturer)
            # self.partnumber = QLineEdit(parent=self)
            # self.partnumber.setPlaceholderText("Part number")
            # layout.addWidget(self.partnumber)
            # self.confirm_button = QPushButton("Confirm", parent=self)
            # self.confirm_button.clicked.connect(self.confirm)
            # layout.addWidget(self.confirm_button)
            #
            # main_layout = QVBoxLayout()
            # main_layout.addLayout(self.layout())
            # main_layout.addLayout(layout)
            #
            # self.setLayout(main_layout)

        self.wellplate.save_attributes2json("Falcon", "12345678")
        logger.log(level=10, msg="SAVED")
        sys.exit()

        # elif self.no_button.isChecked():
        #     # Create a button
        #     button = QPushButton('Exit', self)
        #     # Connect the button to the quit method
        #     button.clicked.connect(self.close)
        #
        #     self.stacked_widget.addWidget(button)
        #     self.stacked_widget.setCurrentWidget(button)

    def confirm(self):
        self.wellplate.save_attributes2json(self.manufacturer.text(), self.partnumber.text())



if __name__ == '__main__':
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
