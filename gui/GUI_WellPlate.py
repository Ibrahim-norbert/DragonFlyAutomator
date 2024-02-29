import glob
import logging
import os
from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget, QLineEdit, QVBoxLayout, QComboBox, QHBoxLayout
from PyQt6.QtCore import Qt
from helperfunctions import create_colored_label
from devices.wellplate import WellPlate
from devices.helperfunctions import RealTimePlot

wellplate_paths = [os.path.basename(x) for x in glob.glob(os.path.join(os.getcwd(), "models", "*WellPlate*"))]

logger = logging.getLogger(__name__)
logger.info("This log message is from another module.")
logging.debug("Directory: {}".format(os.getcwd()))


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
            self.stacked_widget.addWidget(CustomButtonGroup(self.well_plate, self.stacked_widget))
            self.stacked_widget.setCurrentIndex(2)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here: ", exc_info=True)

    def addwell(self):
        try:
            self.stacked_widget.addWidget(WellPlateDimensions(self.stacked_widget, self.well_plate))
            self.stacked_widget.setCurrentIndex(2)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here: ", exc_info=True)


class WellPlateDimensions(QWidget):
    def __init__(self, stacked_widget, wellplate):
        super().__init__()
        self.well_plate = wellplate
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
            self.well_plate.well_plate_req_coords[self.dropdown.currentText()] = self.well_plate.get_state(test_key=self.dropdown.currentText())
            #self.well_plate.well_plate_req_coords[self.dropdown.currentText()] = self.well_plate.get_state()
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
                self.well_plate.predict_well_coords(int(self.column_n.text()), int(self.row_n.text()))

                # Frame three
                self.stacked_widget.addWidget(CustomButtonGroup(self.well_plate, self.stacked_widget))
                self.stacked_widget.setCurrentIndex(3)
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
    def __init__(self, well_plate, stacked_widget):
        super().__init__()

        self.well_plate = well_plate

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
        # Set stretch factors for rows and columns
        # layout.setColumnStretch(0, 0.6)  # Adjust the stretch factor for columns as needed
        # layout.setRowStretch(0, 1)  # Adjust the stretch factor for rows as needed
        #
        # container_layout = QVBoxLayout(self)
        # container_layout.addLayout(layout)

        self.setLayout(main_layout)

        self.stacked_widget = stacked_widget

    def handleEnterPressed(self):
        checked_buttons = [button.well_state_dict for button in self.buttons if button.isChecked()]

        logging.log(level=10, msg="Wells that have been selected: {}".format(checked_buttons))

        self.visualiser = RealTimePlot()

        self.stacked_widget.addWidget(self.visualiser)
        self.stacked_widget.setCurrentIndex(4)


        # This executes the xzystage movement
        self.well_plate.execute_template_coords(checked_buttons, self.visualiser)

        self.stacked_widget.addWidget(SaveWindow())
        self.stacked_widget.setCurrentIndex(5)


class SaveWindow(QWidget):
    def __init__(self):
        super().__init__()

        # self.model = model

        # self.yes_widget = QPushButton("Yes", self)
        # self.no_widget = QPushButton("No", self)

        # yes_no_widget = QHBoxLayout()
        # yes_no_widget.addWidget(self.yes_widget)
        # yes_no_widget.addWidget(self.no_widget)

        layout = QHBoxLayout()
        layout.addWidget(create_colored_label("Would you like to save this new coordinate transformation ?", self))

        self.setLayout(layout)

    # yes_no_widget.addWidget(message)

    # self.setLayout(yes_no_widget)

    # def savemodel(self):

    #  if self.yes_widget.isChecked():
