from PyQt6.QtWidgets import QLabel
from PyQT6 import QStackedWigdet


def create_colored_label(text, parent):
    label = QLabel(text, parent=parent)
    label.setStyleSheet("color: {};".format("white"))
    return label



    