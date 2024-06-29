import glob
import logging
import os.path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout, QComboBox

from DragonFlyWellPlateAutomation.devices.wellplate import WellPlate

logger = logging.getLogger("RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))

wellplate_paths = [os.path.basename(x) for x in glob.glob(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "models", "*WellPlate*"))]


# TODO Add another widget
# TODO Test the script

class UsernamePath(QWidget):
    def __init__(self, parent, stacked_widget, test=True):
        super().__init__(parent)

        self.username = None
        self.img_dir = None
        self.stacked_widget = stacked_widget

        # self.save_directory = QLineEdit(parent=self)
        # self.save_directory.setPlaceholderText("Please enter the directory to save the images in")

        self.username_widget = QLineEdit(parent=self)
        self.username_widget.setPlaceholderText("Please enter your name")
        self.username_widget.editingFinished.connect(self.assign_img_dir_username)

        self.enter_button = QPushButton("Enter", parent=self)
        self.enter_button.clicked.connect(self.handleEnterPressed)

        # # Store the default stylesheet
        # self.default_stylesheet = self.save_directory.styleSheet()
        # self.save_directory.textChanged.connect(self.handlePathChanged)
        # self.save_directory.editingFinished.connect(self.assign_img_dir_username)
        # Layout of widget
        layout = QVBoxLayout()  # Pass the central widget to the layout
        layout.addWidget(self.username_widget)
        # layout.addWidget(self.save_directory)

        horizonti_mini = QHBoxLayout()
        self.selectwell_button = QPushButton("Select Well Plate", self)
        self.selectwell_button.setCheckable(True)  # Set the button to be checkable
        self.selectwell_button.clicked.connect(self.clickselectwp)
        self.addwell_button = QPushButton("Add new Well Plate", self)
        self.addwell_button.setCheckable(True)  # Set the button to be checkable
        self.addwell_button.clicked.connect(self.clicknewwp)
        horizonti_mini.addWidget(self.selectwell_button)
        horizonti_mini.addWidget(self.addwell_button)

        self.dropdown = QComboBox(self)
        for path in wellplate_paths:
            self.dropdown.addItem(path)

        horizonti = QHBoxLayout()
        horizonti.addWidget(self.dropdown)
        horizonti.addLayout(horizonti_mini)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(layout)
        main_layout.addLayout(horizonti)
        main_layout.addWidget(self.enter_button)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(main_layout)

        self.well_plate = WellPlate(test=test)

    def clicknewwp(self):
        if self.selectwell_button.isChecked():
            self.selectwell_button.setChecked(False)

    def clickselectwp(self):
        if self.addwell_button.isChecked():
            self.addwell_button.setChecked(False)

    # def input_text_error_handler(self, path):
    #     try:
    #         if not os.path.exists(path) and os.path.isdir(os.path.dirname(path)):
    #             os.makedirs(path)
    #             # If the path is valid, set the text color to white
    #             self.save_directory.setStyleSheet("color: white;")
    #             logger.log(level=10, msg="Made new directory: " + path)
    #         elif not os.path.isdir(os.path.dirname(path)):
    #             error_message = "Invalid path: Please enter a valid directory."
    #             logger.log(level=10, msg=error_message + ": " + path)
    #             self.save_directory.setText(error_message)
    #             self.save_directory.setStyleSheet("color: red;")
    #         else:
    #             # If the path exists or the directory part is valid, set the text color to white
    #             self.save_directory.setStyleSheet("color: white;")
    #     except Exception as e:
    #         print(f"An unexpected error occurred: {e}")
    #         logger.exception("What happened here: ", exc_info=True)
    #
    def assign_img_dir_username(self):
       # self.img_dir = self.save_directory.text()
        self.username = self.username_widget.text()

    def handleEnterPressed(self):

        # This method will be called when the user presses enter in the line edit widgets

        # Check if both username_widget and path are not empty
        if self.username:
            # Perform the necessary checks and switch to CreateNewWellPlateTemplate

            #self.input_text_error_handler(self.img_dir)

            #self.frameswitcher(self.img_dir, self.username)

            self.frameswitcher(self.username)

    # def handlePathChanged(self):
    #     # Reset the text color and placeholder text when the user starts typing
    #     self.save_directory.setStyleSheet(self.default_stylesheet)

    def frameswitcher(self, username):
        try:
            if wellplate_paths and self.selectwell_button.isChecked():
                logger.log(level=20, msg="Selected saved well-plate dimension")
                self.username_widget.setText(username)
                logger.log(level=20, msg="Username: " + username)
                #logger.log(level=20, msg="Image directory: " + path)
                self.well_plate.load_attributes(self.dropdown.currentText())

                # Frame two
                self.stacked_widget.switch2WPbuttongrid()
            elif self.addwell_button.isChecked():
                logger.log(level=20, msg="Selected to create new well-plate dimension")
                self.username_widget.setText(username)
                logger.log(level=20, msg="Username: " + username)
                #logger.log(level=20, msg="Image directory: " + path)
                # Frame two
                self.stacked_widget.switch2WPnew()
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.exception("What happened here: ", exc_info=True)
