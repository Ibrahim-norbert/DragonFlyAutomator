from PyQt6.QtWidgets import QLabel


def create_colored_label(text, parent):
    label = QLabel(text, parent=parent)
    label.setStyleSheet("color: {};".format("white"))
    return label