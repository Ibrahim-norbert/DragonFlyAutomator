import logging
import os.path
import sys

from PyQt6.QtGui import QIcon, QPainter, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget, QMainWindow, QLineEdit, QVBoxLayout
from PyQt6.QtCore import Qt

directory = os.path.dirname(os.getcwd())

# Configure logging
logging.basicConfig(filename=os.path.join(directory, 'wellplate_estimation.log'),
                    format='%(asctime)s - %(levelname)s - %(message)s')


class WellAsButton(QPushButton):
    def __init__(self, text, parent, coordinates):
        super().__init__(text=text, parent=parent)

        self.coordinates = coordinates
        self.color = "#00aa00"
        self.setStyleSheet("background-color: {}; color: #ffffff;".format(self.color))
        self.setCheckable(True)

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
    def __init__(self, all_state_dicts):
        super().__init__()

        layout = QGridLayout(self)

        for key, well_state_dict in all_state_dicts.items():
            r, c = int(key.split(" ")[0]), int(key.split(" ")[-1])
            label = "abcdefghijklmnopqrstuvwxyz".upper()[r] + key.split(" ")[-1]
            button = WellAsButton(text=label, parent=self, coordinates=(r, c))
            button.clicked.connect(button.handleButtonClick)
            layout.addWidget(button, button.coordinates[0], button.coordinates[1])

        self.setLayout(layout)


class wellplatedimensions(QWidget):
    def __init__(self):
        super().__init__()

        layout = QGridLayout(self)


        self.save_directory = QLineEdit(parent=self)
        self.save_directory.setPlaceholderText("Column number")

        self.username = QLineEdit(parent=self)
        self.username.setPlaceholderText("Row number")


        #TODO give small display fields for the sample readings
        #.........................


        self.enter_button = QPushButton("Enter", parent=self)
        self.enter_button.clicked.connect(self.handleButtonClick)

        layout = QVBoxLayout(self)  # Pass the central widget to the layout

        layout.addWidget(self.username)
        layout.addWidget(self.save_directory)
        layout.addWidget(self.enter_button)

        # Set layout alignment to center
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)




class BackgroundMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.background_image = QPixmap(os.path.join(directory, "dragonfly.jpg"))
        self.overlay_image = QPixmap(os.path.join(directory, "BioQuant_Logo_RGB_136.png"))
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


class DragonflyAutomator(BackgroundMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dragonfly Automator")
        self.setGeometry(100, 100, 800, 400)

        central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(central_widget)  # Set the central widget for the QMainWindow

        self.save_directory = QLineEdit(parent=central_widget)
        self.save_directory.setPlaceholderText("Please enter the directory to save the images in")

        self.username = QLineEdit(parent=central_widget)
        self.username.setPlaceholderText("Please enter your name")

        self.enter_button = QPushButton("Enter", parent=central_widget)
        self.enter_button.clicked.connect(self.handleButtonClick)

        layout = QVBoxLayout(central_widget)  # Pass the central widget to the layout

        layout.addWidget(self.username)
        layout.addWidget(self.save_directory)
        layout.addWidget(self.enter_button)

        # Set layout alignment to center
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Store the default stylesheet
        self.default_stylesheet = self.save_directory.styleSheet()

        self.save_directory.textChanged.connect(self.handlePathChanged)

    def handleButtonClick(self):
        path = self.save_directory.text()

        if not os.path.exists(path) and os.path.isdir(os.path.dirname(path)):
            os.makedirs(path)
            # If the path is valid, set the text color to white
            self.save_directory.setStyleSheet("color: white;")
            logging.log(level=20, msg="Made new directory: " + path)
            # Reset the error_displayed flag
        elif not os.path.isdir(os.path.dirname(path)):
            error_message = "Invalid path: Please enter a valid directory."
            self.save_directory.setText(error_message)
            self.save_directory.setStyleSheet("color: red;")

        else:
            # If the path exists or the directory part is valid, set the text color to white
            self.save_directory.setStyleSheet("color: white;")

        if os.path.exists(path):
            self.username.setText(self.username.text())
            # self.empirical_wellplate()

    def handlePathChanged(self):
        # Reset the text color and placeholder text when the user starts typing
        self.save_directory.setStyleSheet(self.default_stylesheet)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragonflyAutomator()
    window.show()
    sys.exit(app.exec())
