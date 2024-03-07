import os.path
import sys
import logging
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QMainWindow, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt

logger = logging.getLogger(__name__)
logger.info("This log message is from {}".format(__name__))


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
        self.setLayout(layout)

    def handleEnterPressed(self):
        # This method will be called when the user presses Enter in the line edit widgets

        # Check if both username and path are not empty
        if self.username.text() and self.save_directory.text():
            # Perform the necessary checks and switch to WellPlateDimensions
            path = self.save_directory.text()

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

            if os.path.exists(path):
                self.username.setText(self.username.text())
                logging.log(level=10, msg="Username: " + self.username.text())
                # Frame two
                self.stacked_widget.switch2WPoption()

    def handlePathChanged(self):
        # Reset the text color and placeholder text when the user starts typing
        self.save_directory.setStyleSheet(self.default_stylesheet)
