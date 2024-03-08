import glob
import logging
import os
import sys
from time import sleep
import numpy as np
from PyQt6.QtWidgets import QGridLayout, QPushButton, QWidget, QLineEdit, QVBoxLayout, QComboBox, QHBoxLayout, \
    QApplication
from PyQt6.QtCore import Qt, QTimer
from matplotlib import pyplot as plt
from devices.micrscope import Microscope
from devices.wellplate import WellPlate
from devices.protocol import Protocol
from devices.image_based_autofocus import AutoFocus
from gui.helperfunctions import create_colored_label


class GUIProtocol(QWidget):
    def __init__(self):
        super().__init__()

        self.img = None
        self.img_name = None
        self.autofocus = AutoFocus()
        z_stack_layout_0 = QVBoxLayout()
        self.z_increment = QLineEdit(parent=self)
        self.z_increment.setPlaceholderText("mm")
        z_stack_layout_0.addWidget(self.z_increment)
        self.n_aqcuisitions = QLineEdit(parent=self)
        self.n_aqcuisitions.setPlaceholderText("e.g. 5")
        z_stack_layout_0.addWidget(self.n_aqcuisitions)
        self.autofocus_title = create_colored_label("Choose autofocus algorithm", self)
        z_stack_layout_0.addWidget(self.autofocus_title)
        self.dropdown = QComboBox(self)
        for x in self.autofocus.metrics:
            self.dropdown.addItem(x)
        z_stack_layout_0.addWidget(self.dropdown)

        z_stack_layout_2 = QHBoxLayout()

        z_stack_layout_1 = QVBoxLayout()
        self.z_height_travelled = create_colored_label("Z position starts at {} and will end at {}, confirm that \n the objective will not crash into the well plate.".format(), self)
        z_stack_layout_1.addWidget(self.z_height_travelled)
        self.enter_button = QPushButton("Enter", parent=self)
        z_stack_layout_1.addWidget(self.enter_button)
        self.enter_button.clicked.connect(self.enter_button_click)

        z_stack_layout_2.addLayout(z_stack_layout_0)
        z_stack_layout_2.addLayout(z_stack_layout_1)
        
        self.setLayout(z_stack_layout_2)
        
    def run_automated_acquisition(self):
        
        if self.dropdown.currentText() == "Variance":
            f = self.autofocus.maximum_variance


        