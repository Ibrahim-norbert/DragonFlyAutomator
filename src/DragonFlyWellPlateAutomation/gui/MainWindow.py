import glob
import logging
import os.path
import shutil
import sys
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow

from DragonFlyWellPlateAutomation.gui.FrameSwitcher import FrameManager

# Configure import logging

logger = logging.getLogger("RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))
logger.info("Directory: {}".format(os.getcwd()))


# TODO Test the script

class BackgroundMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.background_image = QPixmap(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images", "dragonfly.jpg"))
        self.overlay_image = QPixmap(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images", "BioQuant_Logo_RGB_136.png"))
        self.text = "AG Erfle & Starkuvienė"
        if self.background_image.isNull():
            print("Failed to load image")
            if os.path.exists(
                    os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "images", "dragonfly.jpg")):
                print("But appears to exist")
            else:
                print("Does not exist")

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
        self.setGeometry(500, 300, 800, 400)
        # Widget should be in the centre
        self.setCentralWidget(FrameManager(parent=self, test=True))


def cleanup():
    paths = glob.glob(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "test", "*"))
    [os.remove(path) for path in paths if ".ims" in path]
    [shutil.rmtree(path) for path in paths if "well_" in path]
    logger.log(level=20, msg=f"Files cleaned up")


def main():
    app = QApplication(sys.argv)
    window = DragonflyAutomator()
    window.show()
    app.aboutToQuit.connect(cleanup)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
