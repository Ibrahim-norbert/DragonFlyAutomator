from devices.micrscope import Microscope
from devices.xyzstage import FusionApi, get_output, update
import logging
import os
import json
from RestAPI import fusionrest

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class Protocol(FusionApi):
    def __init__(self):
        super().__init__()  # inherits
        self.endpoint = self.endpoint + "/{}".format("protocol")

        if self.test is False:
            self.current_output = self.get_state()
            self.protocol_name = fusionrest.get_protocol_name()
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", os.path.basename(self.endpoint) + "_current.json"))
            self.current_output = json.load(f)

        self.microscope = Microscope()

    def get_state(self):
        if self.test is False:
            return fusionrest.get_state()
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", os.path.basename(self.endpoint) + "_current.json"))
            return json.load(f)


    def run_protocol(self):
        if self.test is False:
            fusionrest.run_protocol_completely(protocol_name=self.protocol_name)
            logger.log(level=10, msg="Running protocol: {}".format(self.current_output.values()))
        else:
            logger.log(level=10, msg="Running protocol: {}".format(self.current_output.values()))

    def change_image_name(self, image_name):
        if self.test is False:
            img_name_dict = get_output(os.path.dirname(self.endpoint) + "/{}".format("datasets"))
            img_path = img_name_dict["Path"]

            logger.log(level=20, msg="Current image path: {}".format(img_path))
            if ".ims" not in image_name:
                image_name = image_name + ".ims"

            img_name_dict["Path"] = os.path.join(os.path.split(img_path)[0], image_name)
            logger.log(level=20, msg="New image path: {}".format(img_name_dict["Path"]))
            update(self.endpoint + "/{}".format("filename"), img_name_dict)
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", "dataset.json"))
            img_name_dict = json.load(f)

            img_path = img_name_dict["Path"]

            logger.log(level=20, msg="Current image path: {}".format(img_path))
            if ".ims" not in image_name:
                image_name = image_name + ".ims"

            img_name_dict["Path"] = os.path.join(os.path.split(img_path)[0], image_name)
            logger.log(level=20, msg="New image path: {}".format(img_name_dict["Path"]))

    def z_stack(self, img_name="image", wellcoord="0 0", z_increment = 5, n_aqcuisitions = 10):
        # Set image name
        height = z_increment * n_aqcuisitions
        logger.log(level=10,
                   msg="Height travelled in total {} mm. Please determine from current position that this is safe".format(
                       height))
        if self.test is False:
            for i in range(n_aqcuisitions):
                state, _ = self.microscope.get_current_z()
                z = self.microscope.move_z_axis(z_increment, state=state)
                self.change_image_name(image_name="{}{}_well{}_zheigth{}".format(img_name, i + 1, wellcoord, int(z)))
                self.run_protocol()
        else:
            for i in range(n_aqcuisitions):
                state, _ = self.microscope.get_current_z()
                z = self.microscope.move_z_axis(z_increment, state=state)
                self.change_image_name(image_name="{}{}_well{}_zheigth{}".format(img_name, i + 1, wellcoord, int(z)))
                self.run_protocol()



if __name__ == '__main__':
    protocol = Protocol()


    print("Is this a test? ")
    answer = input()

    if answer.upper() == "NO":
        protocol.test = False
    else:
        protocol.test = True


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
