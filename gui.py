import glob
import logging
import os.path
import sys

from PyQt6.QtGui import QIcon, QPainter, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget, QMainWindow, QLineEdit, QVBoxLayout, \
    QLabel, QComboBox, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt
from wellplate import wellplate

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


def create_colored_label(text, parent):
    label = QLabel(text, parent=parent)
    label.setStyleSheet("color: {};".format("white"))
    return label


class WellPlateDimensions(QWidget):
    def __init__(self, stacked_widget, endpoint, model):
        super().__init__()

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
        self.dropdown.addItem("Top left well")
        self.dropdown.addItem("Bottom left well")
        self.dropdown.addItem("Top right well")

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

        self.stacked_widget.addWidget(self)

        options = [self.dropdown.itemText(index) for index in range(self.dropdown.count())]
        self.well_plate = wellplate(endpoint=endpoint, well1=options[0], well2=options[1], well3=options[2],
                                    model=model)

    def read_well_coordinate(self):

        try:
            self.well_plate.well_plate_req_coords[self.dropdown.currentText()] = self.well_plate.get_state()
            vector = self.well_plate.state_dict_2_vector(
                self.well_plate.well_plate_req_coords[self.dropdown.currentText()])
            self.placeholder_coordinates.setText(str(vector))
            logging.log(level=20, msg="Well: " + self.dropdown.currentText() + " - " + str(vector))

            if None not in self.well_plate.well_plate_req_coords.values():
                final = self.well_plate.well_plate_req_coords.items()
                logging.log(level=20, msg="Final coordinates: " + str(final))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("Must select one of the well options first before ", exc_info=True)

    def enter_button_click(self):

        if None not in self.well_plate.well_plate_req_coords.values():
            self.well_plate.compute_template_coords(self.column_n, self.row_n)


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
        self.save_directory.returnPressed.connect(self.handleEnterPressed)
        self.username.returnPressed.connect(self.handleEnterPressed)

        # Layout of widget
        layout = QVBoxLayout(self)  # Pass the central widget to the layout
        layout.addWidget(self.username)
        layout.addWidget(self.save_directory)
        layout.addWidget(self.enter_button)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.stacked_widget.addWidget(self)

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
                logging.log(level=20, msg="Made new directory: " + path)
            elif not os.path.isdir(os.path.dirname(path)):
                error_message = "Invalid path: Please enter a valid directory."
                logging.log(level=20, msg=error_message + ": " + path)
                self.save_directory.setText(error_message)
                self.save_directory.setStyleSheet("color: red;")
            else:
                # If the path exists or the directory part is valid, set the text color to white
                self.save_directory.setStyleSheet("color: white;")

            if os.path.exists(path):
                self.username.setText(self.username.text())
                logging.log(level=20, msg="Username: " + self.username.text())
                self.stacked_widget.setCurrentIndex(1)

    def handlePathChanged(self):
        # Reset the text color and placeholder text when the user starts typing
        self.save_directory.setStyleSheet(self.default_stylesheet)


class DragonflyAutomator(BackgroundMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dragonfly Automator")
        self.setGeometry(500, 300, 800, 400)

        self.stacked_widget = QStackedWidget()
        # Widget should be in the centre
        self.setCentralWidget(self.stacked_widget)

        self.frame_1 = UsernamePath(self.stacked_widget)

        self.model = None
        #files = glob.glob("*.pkl")
        #if files is None:
         #   self.model = None

        self.frame_2 = WellPlateDimensions(self.stacked_widget, endpoint="v1/devices/xyz-stage", model=self.model)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragonflyAutomator()
    window.show()
    sys.exit(app.exec())
