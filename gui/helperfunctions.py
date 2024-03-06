from PyQt6.QtWidgets import QLabel
from PyQt6.QtWidgets import QStackedWidget
import GUI_WellPlate as GUIWP
import visualisation as VIZ
import config


def create_colored_label(text, parent):
    label = QLabel(text, parent=parent)
    label.setStyleSheet("color: {};".format("white"))
    return label


class FrameManager(QStackedWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.frame0 = config.UsernamePath(stacked_widget=self)
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

    def switch2WPrtplotter(self):
        self.setCurrentWidget(self.frame4)

    def switch2WPsavewindow(self):
        self.setCurrentWidget(self.frame5)
