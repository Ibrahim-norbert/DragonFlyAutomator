import logging
import os.path
import sys

from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow

import sys
sys.path[0] =  r"C:\Users\Piotr Wajda\Desktop\384_wellplate\Dragonfly_package\348_wellplate_automation-main"

from DragonFlyWellPlateAutomation.gui.FrameSwitcher import FrameManager

# Configure import logging

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))
logger.info("Directory: {}".format(os.getcwd()))


# TODO Test the script

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


class DragonflyAutomator(BackgroundMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Dragonfly Automator")
        self.setGeometry(500, 300, 800, 400)
        # Widget should be in the centre
        self.setCentralWidget(FrameManager(parent=self, test=True))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DragonflyAutomator()
    window.show()
    sys.exit(app.exec())
