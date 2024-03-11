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
    def __init__(self, parent):
        super().__init__(parent)

        self.frame0 = SaveDirectory.UsernamePath(stacked_widget=self)
        self.frame1 = GUIWP.SelectWellPlateDimensions(stacked_widget=self)
        self.frame2 = GUIWP.WellPlateDimensions(stacked_widget=self, well_plate=self.frame1.well_plate)
        self.frame3 = GUIWP.CustomButtonGroup(stacked_widget=self, well_plate=self.frame1.well_plate)
        self.frame4 = GUIP.GUIProtocol(stacked_widget=self)
        self.frame5 = VIZ.CoordinatePlot(stacked_widget=self, well_plate=self.frame1.well_plate,
                                         protocol=self.frame4.protocol)
        self.frame6 = GUIWP.SaveWindow(stacked_widget=self, well_plate=self.frame1.well_plate)

        self.addWidget(self.frame0)
        self.addWidget(self.frame1)
        self.addWidget(self.frame2)
        self.addWidget(self.frame3)
        self.addWidget(self.frame4)
        self.addWidget(self.frame5)
        self.addWidget(self.frame6)

    def switch2WPoption(self):
        self.setCurrentWidget(self.frame1)

    def switch2WPnew(self):
        self.setCurrentWidget(self.frame2)

    def switch2WPbuttongrid(self):
        self.frame3.creatbuttongrid()
        self.setCurrentWidget(self.frame3)

    def switch2WPrtplotter(self):
        self.setCurrentWidget(self.frame5)
        self.frame5.initviz()

    def switch2Protocol(self, data):
        self.setCurrentWidget(self.frame4)
        self.frame4.wellcords = data

    def switch2WPsavewindow(self):
        self.setCurrentWidget(self.frame5)
