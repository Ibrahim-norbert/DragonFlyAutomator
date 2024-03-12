import glob
import logging
import os.path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox

from DragonFlyWellPlateAutomation.devices.wellplate import WellPlate
from DragonFlyWellPlateAutomation.gui.helperfunctions import create_colored_label

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))

wellplate_paths = [os.path.basename(x) for x in glob.glob(os.path.join(os.getcwd(), "models", "*WellPlate*"))]


# TODO Add another widget
# TODO Test the script

class UsernamePath(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.stacked_widget = stacked_widget

        self.save_directory = QLineEdit(parent=self)
        self.save_directory.setPlaceholderText("Please enter the directory to save the images in")

        self.username = QLineEdit(parent=self)
        self.username.setPlaceholderText("Please enter your name")

        self.enter_button = QPushButton("Enter", parent=self)
        self.enter_button.clicked.connect(self.handleEnterPressed)

        # Store the default stylesheet
        self.default_stylesheet = self.save_directory.styleSheet()

        self.save_directory.textChanged.connect(self.handlePathChanged)

        # Layout of widget
        layout = QVBoxLayout(self)  # Pass the central widget to the layout
        layout.addWidget(self.username)
        layout.addWidget(self.save_directory)
        layout.addWidget(self.enter_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dropdown = QComboBox(self)
        for path in wellplate_paths:
            self.dropdown.addItem(path)

        layout1 = QVBoxLayout()
        self.selectwell_button = QPushButton("Select Well Plate", self)
        self.addwell_button = QPushButton("Add new Well Plate", self)
        layout1.addWidget(self.selectwell_button)
        layout1.addWidget(self.addwell_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.dropdown)
        main_layout.addLayout(layout1)

        layout.addLayout(main_layout)
        self.setLayout(layout)

        self.well_plate = WellPlate()

    def input_text_error_handler(self, path):
        # TODO confirm if this works
        try:
            if not os.path.exists(path) and os.path.isdir(os.path.dirname(path)):
                os.makedirs(path)
                # If the path is valid, set the text color to white
                self.save_directory.setStyleSheet("color: white;")
                logging.log(level=10, msg="Made new directory: " + path)
            elif not os.path.isdir(os.path.dirname(path)):
                error_message = "Invalid path: Please enter a valid directory."
                logging.log(level=10, msg=error_message + ": " + path)
                self.save_directory.setText(error_message)
                self.save_directory.setStyleSheet("color: red;")
            else:
                # If the path exists or the directory part is valid, set the text color to white
                self.save_directory.setStyleSheet("color: white;")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here: ", exc_info=True)

    def frameswitcher(self, path):
        # TODO confirm if this works
        try:
            if wellplate_paths and os.path.exists(path) and self.selectwell_button.clicked:
                logging.log(level=20, msg="Selected saved well-plate dimension")
                self.username.setText(self.username.text())
                logging.log(level=20, msg="Username: " + self.username.text())
                self.well_plate.load_attributes(self.dropdown.currentText())
                # Frame two
                self.stacked_widget.switch2WPbuttongrid()
            elif os.path.exists(path) and self.addwell_button.clicked:
                logging.log(level=20, msg="Selected to create new well-plate dimension")
                self.username.setText(self.username.text())
                logging.log(level=20, msg="Username: " + self.username.text())
                # Frame two
                self.stacked_widget.switch2WPnew()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here: ", exc_info=True)

    def handleEnterPressed(self):
        # This method will be called when the user presses Enter in the line edit widgets

        # Check if both username and path are not empty
        if self.username.text() and self.save_directory.text():
            # Perform the necessary checks and switch to CreateNewWellPlateTemplate
            path = self.save_directory.text()

            self.input_text_error_handler(path)

            self.frameswitcher(path)

    def handlePathChanged(self):
        # Reset the text color and placeholder text when the user starts typing
        self.save_directory.setStyleSheet(self.default_stylesheet)
