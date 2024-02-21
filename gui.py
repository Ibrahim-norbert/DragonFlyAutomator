from PyQt6.QtWidgets import QApplication, QGridLayout, QPushButton, QWidget, QButtonGroup, QMainWindow
import sys
from wellplate import wellplate

class WellAsButton(QPushButton):
    def __init__(self, text, parent, coordinates):
        super().__init__(text=text, parent=parent)

        self.coordinates = coordinates
        self.color = "#00aa00"
        self.setStyleSheet("background-color: {}; color: #ffffff;".format(self.color))
        self.setCheckable(True)


class CustomButtonGroup:

    """
    In PyQt, QButtonGroup is not directly subclassable because it is not meant to be a widget itself but rather a
    container for managing groups of radio buttons or checkable buttons. However, you can create a class that
    encapsulates a QButtonGroup and extends its functionality. This class can have additional methods
    and properties to handle your specific use case

    """
    def __init__(self, all_state_dicts):
        self.button_group = QButtonGroup()

        self.selected_buttons = set()

        for key, well_state_dict in all_state_dicts.items():
            r, c = int(key.split(" ")[0]), int(key.split(" ")[-1])
            label = "abcdefghijklmnopqrstuvwxyz".upper()[r] + key.split(" ")[-1]
            button = WellAsButton(text=label, parent=self, coordinates=(r, c))
            self.addButton(button)



        self.connectButtons(self.handleButtonClick)

    def addButton(self, button):
        self.button_group.addButton(button)

    def handleButtonClick(self, button):
        if button.isChecked():
            print(f"{button.text()} selected")
        else:
            print(f"{button.text()} deselected")

    def connectButtons(self, callback):
        self.button_group.buttonClicked.connect(callback)

#TODO How can i make group button as its own widget ????
class DragonflyAutomator(QMainWindow):
    def __init__(self, all_state_dicts):
        super().__init__()

        layout = QGridLayout(self)
        layout.addWidget(button, button.coordinates[0], button.coordinates[1]) #TODO Solve this

        CustomButtonGroup(parent=self, all_state_dicts=all_state_dicts)

        #self.setCentralWidget(buttons)

        self.setWindowTitle("Dragonfly Automator")
        self.setGeometry(100, 100, 400, 300)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='train a phase registration model')
    parser.add_argument("--columns", type=int, required=False, help="Enter x coordinates for xyz stage")
    parser.add_argument("--rows", type=int, required=False, help="Enter y coordinates for xyz stage")
    parser.add_argument("--analoguecontrol", type=bool, default=False, help="Enter boolean for analog control of xyz stage")
    parser.add_argument("--update", type=bool, default=False, help="Enter boolean for analog control of xyz stage")
    parser.add_argument("--endpoint",type=str, required=True, help="Enter API endpoint of xyz stage")


    args = parser.parse_args()


    wellplate_ = wellplate(endpoint=args.endpoint)

    print("Before update: " + str(wellplate_.__dict__))

    wellplate_.get_well_plate_req_coords()

    columns,rows = args.columns, args.rows

    if columns is not None and rows is not None:

        all_state_dicts = wellplate_.compute_wellplate_coords(columns, rows)

        # 2. Create an instance of QApplication
        app = QApplication(sys.argv)  # Handles command line arguments but as empty list is given no command line argument
        # handling is instructed

        window = DragonflyAutomator(all_state_dicts)

        # window.setGeometry(50, 50, 280, 80)  # x,y positions and width,height of window
        window.show()

        sys.exit(app.exec())







#
# import sys
#
#
# from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
#
#
# WINDOW_SIZE = 235
#
#
# class PyCalcWindow(QMainWindow):
#
#     """PyCalc's main window (GUI or view)."""
#
#
#     def __init__(self):
#
#         super().__init__()
#
#         self.setWindowTitle("PyCalc")
#
#         self.setFixedSize(WINDOW_SIZE, WINDOW_SIZE)
#
#         centralWidget = QWidget(self)
#
#         self.setCentralWidget(centralWidget)
#
#
# def main():
#
#     """PyCalc's main function."""
#
#     pycalcApp = QApplication([])
#
#     pycalcWindow = PyCalcWindow()
#
#     pycalcWindow.show()
#
#     sys.exit(pycalcApp.exec())
#
#
# if __name__ == "__main__":
#
#     main()


#window.setGeometry(50, 50, 280, 80) #x,y positions and width,height of window
#helloMsg = QLabel("<h1>Hello, World!</h1>", parent=window) #Widget or graphical component. It displays HTML formatted text, here the text is provided as a h1 header
#helloMsg.move(60, 15) #Moves the text within the coordinates of the window

# 4. Show your application's GUI
#window.show() #Paints the widgets and is added to the application event queue.

# 5. Run your application's event loop
#sys.exit(app.exec())# The application event loop is started using .exec. This is wrapped into sys.exit() which enables
# clean exit from python and release of memory resources when the application is terminated.