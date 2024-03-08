


class GUIProtocol(Qwidget):
    def __init__():
        super().__init__()

        self.img_name = None

        z_stack_layout_0 = QVBoxLayout()
        self.z_increment = QLineEdit(parent=self)
        self.z_increment.setPlaceholderText("mm")
        z_stack_layout.addWidget(self.z_increment)
        self.n_aqcuisitions = QLineEdit(parent=self)
        self.n_aqcuisitions.setPlaceholderText("e.g. 5")
        z_stack_layout.addWidget(self.n_aqcuisitions)

        
        z_stack_layout_1 = QHBoxLayout()
        self.z_height_travelled = create_colored_label("Z position starts at {} and will end at {}, confirm that the objective will not crash into the sample.".format(), self)
        self.z_increment.setPlaceholderText("mm")

        