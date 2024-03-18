import logging
from PyQt6.QtWidgets import QStackedWidget
import GUI_Protocol as GUIP
import GUI_WellPlate as GUIWP
import SaveDirectory
import Visualisation as VIZ

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


# TODO check device instance passages as parameters between relevant frames

class FrameManager(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Well plate related
        self.frame0 = SaveDirectory.UsernamePath(stacked_widget=self)
        self.frame1 = GUIWP.CreateNewWellPlateTemplate(stacked_widget=self, well_plate=self.frame0.well_plate)
        self.frame2 = GUIWP.CustomButtonGroup(stacked_widget=self, well_plate=self.frame0.well_plate)

        # Protocol related
        self.frame3 = GUIP.GUIProtocol(stacked_widget=self, img_dir=self.frame0.save_directory)
        self.frame4 = VIZ.CoordinatePlotAndImgDisplay(stacked_widget=self, well_plate=self.frame0.well_plate,
                                                      protocol=self.frame3.protocol)

        self.addWidget(self.frame0)
        self.addWidget(self.frame1)
        self.addWidget(self.frame2)
        self.addWidget(self.frame3)
        self.addWidget(self.frame4)

    def switch2WPnew(self):
        self.setCurrentWidget(self.frame1)

    def switch2WPbuttongrid(self):
        self.frame2.creatbuttongrid()
        self.setCurrentWidget(self.frame2)

    def switch2WPrtplotter(self):
        self.setCurrentWidget(self.frame4)
        self.frame4.initviz()

    def switch2Protocol(self):
        self.setCurrentWidget(self.frame3)


def main():
    FrameManager()


if __name__ == '__main__':
    main()
