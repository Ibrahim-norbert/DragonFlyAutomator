import logging

from PyQt6.QtWidgets import QLabel

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


def create_colored_label(text, parent):
    label = QLabel(text, parent=parent)
    label.setStyleSheet("color: {};".format("white"))
    return label
