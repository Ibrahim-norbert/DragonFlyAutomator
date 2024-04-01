import logging

from PyQt6.QtWidgets import QStackedWidget

import DragonFlyWellPlateAutomation.gui.GUI_Protocol as GUIP
import DragonFlyWellPlateAutomation.gui.GUI_WellPlate as GUIWP
import DragonFlyWellPlateAutomation.gui.SaveDirectory as SaveDirectory
import DragonFlyWellPlateAutomation.gui.Visualisation as VIZ

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


# TODO check device instance passages as parameters between relevant frames

class FrameManager(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Well plate related
        self.frame0 = SaveDirectory.UsernamePath(stacked_widget=self)
        self.frame1 = GUIWP.CreateNewWellPlateTemplate(stacked_widget=self, well_plate=self.frame0.well_plate)
        self.frame2 = GUIWP.CustomButtonGroup(stacked_widget=self, well_plate=self.frame1.well_plate)

        # Protocol related
        self.frame3 = GUIP.GUIProtocol(stacked_widget=self)
        self.frame4 = VIZ.CoordinatePlotAndImgDisplay(stacked_widget=self)

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
        self.frame4.initviz(self.frame1.well_plate, self.frame3.protocol)

    def switch2Protocol(self):
        self.setCurrentWidget(self.frame3)

