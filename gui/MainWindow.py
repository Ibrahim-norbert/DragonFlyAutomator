import os.path
import sys
import logging
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QMainWindow, QLineEdit, QVBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt

import GUI_WellPlate as GUIWP
import visualisation as VIZ

# Configure logging

logger = logging.getLogger(__name__)
logger.info("This log message is from another module.")
logging.debug("Directory: {}".format(os.getcwd()))


    
class BackgroundMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_image = QPixmap(os.path.join(os.getcwd(), "images", "dragonfly.jpg"))
        self.overlay_image = QPixmap(os.path.join(os.getcwd(), "images", "BioQuant_Logo_RGB_136.png"))
        self.text = "AG Erfle & Starkuvienė"

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw the background image
        painter.drawPixmap(self.rect(), self.background_image)

        # Draw the overlay image in the top-left corner
        painter.drawPixmap(0, 0, self.overlay_image)

        # Set the text color to white
        painter.setPen(QColor("white"))

        # Set font properties if needed
        font = QFont()
        font.setPointSize(25)
        painter.setFont(font)

        # Add text next to the small picture
        painter.drawText(self.overlay_image.width(), 35, self.text)



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

class FrameManager(QStackedWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.frame0 = GUIWP.UsernamePath(stackedwidget=self)
        self.frame1 = GUIWP.SelectWellPlateDimensions(stacked_widget=self)
        self.frame2 = GUIWP.WellPlateDimensions(stacked_widget=self)
        self.frame3 = GUIWP.CustomButtonGroup(stacked_widget=self)
        self.frame4 = VIZ.CoordinatePlot(stacked_widget=self)
        self.frame5 = GUIWP.SaveWindow(stacked_widget=self)



        self.addWidget(self.frame1)
        self.addWidget(self.frame2)
        self.addWidget(self.frame3)
        self.addWidget(self.frame4)
        self.addWidget(self.frame5)
        
    def switch2WPoption(self):
        self.setCurrentWidget(self.frame1)

    def switch2WPnew(self):
        self.setCurrentWidget(self.frame2)

    def switch2WPbuttongrid(self):
        self.setCurrentWidget(self.frame3)

    def switch2WPrtplotter(self, data):
        self.setCurrentWidget(self.frame4)
        #Once the data is assigned we have regular update of the function
        self.frame.initupdate(data)

    def switch2WPsavewindow(self):
        self.setCurrentWidget(self.frame5)




class DragonflyAutomator(BackgroundMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dragonfly Automator")
        self.setGeometry(500, 300, 800, 400)

        self.stacked_widget = QStackedWidget()
        # Widget should be in the centre
        self.setCentralWidget(self.stacked_widget)

        # Frame one
        self.stacked_widget.addWidget(UsernamePath(self.stacked_widget))

    # def add_switch_to_next_widget(self, widget):
    #     .addWidget(widget)
    #     self.stacked_widget.setCurrentWidget(widget)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragonflyAutomator()
    window.show()
    sys.exit(app.exec())
