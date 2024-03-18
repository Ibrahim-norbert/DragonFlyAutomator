from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QWidget, QLineEdit, QVBoxLayout, QComboBox, QHBoxLayout, QCheckBox

from DragonFlyWellPlateAutomation.devices.protocol import Protocol
from helperfunctions import create_colored_label


# TODO Test the script and add a widget that informs operator to select the protocol needed

class GUIProtocol(QWidget):
    def __init__(self, stacked_widget, img_dir):
        super().__init__()

        self.wellcords = None
        self.stacked_widget = stacked_widget
        self.protocol = Protocol(img_dir=img_dir)

        stackie_tl = QVBoxLayout()
        self.z_increment = QLineEdit(parent=self)
        self.z_increment.setPlaceholderText("Add z spacing (mm)")
        # self.z_increment.editingFinished.connect(self.enteredvalues)
        stackie_tl.addWidget(self.z_increment)
        self.n_acquisitions = QLineEdit(parent=self)
        self.n_acquisitions.setPlaceholderText("Add acquisition number e.g. 5")
        self.n_acquisitions.editingFinished.connect(self.enteredvalues)
        stackie_tl.addWidget(self.n_acquisitions)

        stackie_tr = QVBoxLayout()
        self.z_height_travelled = create_colored_label("", self)
        stackie_tr.addWidget(self.z_height_travelled)
        self.img_name = QLineEdit(parent=self)
        self.img_name.setPlaceholderText("Please give an image name")
        stackie_tr.addWidget(self.img_name)

        horizonti_top = QHBoxLayout()
        horizonti_top.addLayout(stackie_tl)
        horizonti_top.addLayout(stackie_tr)

        horizonti_middle = QHBoxLayout()
        self.autofocus_title = create_colored_label("Choose autofocus algorithm", self)
        horizonti_middle.addWidget(self.autofocus_title)
        self.dropdown = QComboBox(self)
        for x in self.protocol.autofocus.metrics:
            self.dropdown.addItem(x)
        horizonti_middle.addWidget(self.dropdown)

        horizonti_low = QHBoxLayout()
        self.checkbox = QCheckBox('Use non-linear correction for well prediction ?', self)
        horizonti_low.addWidget(self.checkbox)
        self.enter_button = QPushButton("Run automated image acquisition", parent=self)
        horizonti_low.addWidget(self.enter_button)
        self.enter_button.clicked.connect(self.run_automated_acquisition)

        main = QVBoxLayout(self)
        main.addLayout(horizonti_top)
        main.addLayout(horizonti_middle)
        main.addLayout(horizonti_low)
        main.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main)

    # def handlePathChanged(self):
    #     if self.n_acquisitions.text() is not None and self.z_increment.text() is not None:
    #         z_increment = eval(self.z_increment.text())
    #         n_acquisitions = eval(self.n_acquisitions.text())
    #
    #         # TODO Make live display of z height.
    #         # TODO make double acquisitions.one below current z height and the other above
    #         print(n_acquisitions, z_increment)
    # print(n_acquisitions, z_increment)
    # if isinstance(n_acquisitions, int) or isinstance(n_acquisitions, float) and isinstance(z_increment, float)\
    #         or isinstance(z_increment, int):
    #     self.z_height_travelled.setText("Current z height is " + str(self.protocol.microscope.starting_z_height) +
    #                                     " and minimum z height would be " + str(self.protocol.microscope.starting_z_height -
    #                                                                             n_acquisitions*z_increment))

    def enteredvalues(self):
        n_acquisitions = eval(self.n_acquisitions.text())
        z_increment = eval(self.z_increment.text())

        if isinstance(n_acquisitions, (int, float)) is True and isinstance(z_increment, (int, float)):
            self.z_height_travelled.setText("Z position starts at {} and will end at {}.\n"
                                            "<font color='red'>Please confirm that the objective will "
                                            "not crash into the well plate.</font>".format
                                            (self.protocol.microscope.starting_z_height,
                                             round(self.protocol.microscope.starting_z_height +
                                                   (n_acquisitions * z_increment), 3)))

            # Assign the acquisition number and z increment to protocol instance
            self.protocol.n_acquisitions = n_acquisitions
            self.protocol.z_increment = z_increment

        else:
            self.z_height_travelled.setText("<font color='red'>Both entries must be integers or floats.</font>")

    def run_automated_acquisition(self):

        if self.protocol.n_acquisitions is not None and self.protocol.z_increment is not None:
            # Assign nonlinear correction for well prediction
            self.protocol.non_linear_correction = True if self.checkbox.isChecked() else False

            # Assign image name
            self.protocol.image_name = self.img_name.text()

            # Assign chosen algorithm
            self.protocol.autofocus_algorithm = self.dropdown.currentText()

            self.stacked_widget.switch2WPrtplotter()
