import pickle
from micrscope import Microscope
from xyzstage import FusionApi, get_output, update
import logging
import numpy as np
import os
import json
from time import sleep
logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class Protocol(FusionApi):
    def __init__(self):
        super().__init__()  # inherits
        self.endpoint = self.endpoint + "/{}".format("protocol")
        self.current_output = self.get_state()
        self.microscope = Microscope()

    def get_state(self):
        return {"current": get_output(endpoint=self.endpoint + "/{}".format("current"))}

    def run_protocol(self):
        update(self.endpoint + "/{}".format("state"), {"State": "Running"})
        logger.log(level=10, msg="Running protocol: {}".format(self.current_output.values()))

    def change_image_name(self, image_name):
	
        img_name_dict = get_output(self.endpoint + "/{}".format("filename"))
        print(img_name_dict )
        #img_name_dict["ImageName"] = image_name
        #update(self.endpoint + "/{}".format("filename"), img_name_dict)

    def z_stack(self, wellcoord="0 0"):
        # Set image name
        z_increment = 5
        n_aqcuisitions = 10
        height = z_increment * n_aqcuisitions
        logger.log(level=10,
                   msg="Height travelled in total {} mm. Please determine from current position that this is safe".format(
                       height))
        for i in range(n_aqcuisitions):
            _, z = self.microscope.get_current_z()
            #self.change_image_name(image_name="Image{}_well{}_zheigth{}".format(i + 1, wellcoord, z))
            self.run_protocol()
            sleep(3)

    # def image_autofocus(self, wellcoord):


if __name__ == '__main__':
    protocol = Protocol()

    logger.log(level=10, msg="Current Protocol: {}".format(protocol.get_state()))

    print("Change protocol image name ? ")
    answer = input()

    if answer.upper() == "YES":
        logger.log(level=10, msg="Change name of image taken")
        protocol.change_image_name("New_picture")

    print("Run current protocol ? ")
    answer = input()

    if answer.upper() == "YES":
        logger.log(level=10, msg="Protocol set to running")
        protocol.run_protocol()
        logger.log(level=10, msg="New state: {}".format(protocol.get_state()))


    print("Test Z stacking ? ")
    answer = input()

    if answer.upper() == "YES":
        logger.log(level=10, msg="Z stacking is on")
        protocol.z_stack()


