from PyQt6.QtWidgets import QPushButton, QWidget, QLineEdit, QVBoxLayout, QComboBox, QHBoxLayout

from devices.protocol import Protocol
from gui.helperfunctions import create_colored_label


class GUIProtocol(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.wellcords = None
        self.stacked_widget = stacked_widget
        self.protocol = Protocol()

        z_stack_layout_0 = QVBoxLayout()
        self.img_name = QLineEdit(parent=self)
        self.img_name.setPlaceholderText("Please give a image name")
        z_stack_layout_0.addWidget(self.img_name)
        self.z_increment = QLineEdit(parent=self)
        self.z_increment.setPlaceholderText("mm")
        z_stack_layout_0.addWidget(self.z_increment)
        self.n_acquisitions = QLineEdit(parent=self)
        self.n_acquisitions.setPlaceholderText("e.g. 5")
        z_stack_layout_0.addWidget(self.n_acquisitions)
        self.autofocus_title = create_colored_label("Choose autofocus algorithm", self)
        z_stack_layout_0.addWidget(self.autofocus_title)

        self.dropdown = QComboBox(self)

        self.protocol.autofocus.metrics = {key: values for key, values in self.__dict__.items() if
                                           callable(values) and values not in ["calculate_summed_power",
                                                                               "power_spectrum"]}

        for x in self.protocol.autofocus.metrics:
            self.dropdown.addItem(x)
        z_stack_layout_0.addWidget(self.dropdown)

        z_stack_layout_2 = QHBoxLayout()

        z_stack_layout_1 = QVBoxLayout()
        self.z_height_travelled = create_colored_label("",
                                                       self)
        z_stack_layout_1.addWidget(self.z_height_travelled)
        self.enter_button = QPushButton("Run automated image acquisition", parent=self)
        z_stack_layout_1.addWidget(self.enter_button)
        self.enter_button.clicked.connect(self.run_automated_acquisition)

        z_stack_layout_2.addLayout(z_stack_layout_0)
        z_stack_layout_2.addLayout(z_stack_layout_1)

        self.setLayout(z_stack_layout_2)

    def enteredvalues(self):
        n_acquisitions = eval(self.n_acquisitions.text())
        z_increment = eval(self.z_increment.text())

        if isinstance((n_acquisitions, z_increment), (int, float)) is True:
            self.z_height_travelled.setText("Z position starts at {} and will end at {}.\n"
                                            "<font color='red'>Please confirm that the objective will "
                                            "not crash into the well plate.</font>".format
                                            (self.protocol.microscope.current_z_height()[-1],
                                             self.protocol.microscope.current_z_height()[-1] +
                                             (n_acquisitions * z_increment)))

            # Assign the acquisition number and z increment to protocol instance
            self.protocol.n_acquisitions = n_acquisitions
            self.protocol.z_increment = z_increment

            # Assign image name
            self.protocol.image_name = self.img_name

        else:
            self.z_height_travelled.setText("<font color='red'>Both entries must be integers or floats.</font>")

    def run_automated_acquisition(self):

        if self.protocol.n_acquisitions is not None and self.protocol.z_increment is not None:
            self.protocol.autofocus.alg = getattr(self.protocol.autofocus, self.dropdown.currentText())
            self.stacked_widget.switch2WPrtplotter()
