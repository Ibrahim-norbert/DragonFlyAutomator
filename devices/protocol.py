import glob
import json
import logging
import os

from imaris_ims_file_reader.ims import ims

from RestAPI import fusionrest
from devices.image_based_autofocus import AutoFocus
from devices.micrscope import Microscope
from devices.xyzstage import FusionApi, get_output, update

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class Protocol(FusionApi):
    def __init__(self):
        super().__init__()  # inherits
        self.z_increment = None
        self.n_acquisitions = None
        self.endpoint = self.endpoint + "/{}".format("protocol")
        self.autofocus = AutoFocus()
        self.microscope = Microscope()

        self.image_name = None

        if self.test is False:
            self.current_output = self.get_state()
            self.protocol_name = fusionrest.get_protocol_name()
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", os.path.basename(self.endpoint) + "_current.json"))
            self.current_output = json.load(f)

        self.image_dir = "/media/ibrahim/Extended Storage/cloud/Internship/bioquant/348_wellplate_automation/test_rn"
        self.img_name_dict, _ = self.get_image_dir()

    def get_state(self):
        if self.test is False:
            return fusionrest.get_state()
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", os.path.basename(self.endpoint) + "_current.json"))
            return json.load(f)

    def run_protocol(self):
        if self.test is False:
            fusionrest.run_protocol_completely(protocol_name=self.protocol_name)
            logger.log(level=20, msg="Running protocol: {}".format(self.current_output.values()))
        else:
            logger.log(level=20, msg="Running protocol: {}".format(self.current_output.values()))

    # TODO unable to get image directory look at it again.
    def get_image_dir(self): #Look at this
        if self.test is False:
            img_name_dict = get_output(os.path.dirname(self.endpoint) + "/{}".format("datasets"))
            return img_name_dict, os.path.split(img_name_dict["Path"])[0]
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", "dataset.json"))
            img_name_dict = json.load(f)
            return img_name_dict, os.path.split(img_name_dict["Path"])[0]

    def change_image_name(self, image_name):
        if self.test is False:

            if ".ims" not in image_name:
                image_name = image_name + ".ims"

            if self.image_dir not in image_name:
                self.img_name_dict["Path"] = os.path.join(self.image_dir, image_name)
            else:
                self.img_name_dict["Path"] = image_name

            logger.log(level=20, msg="New image path: {}".format(self.img_name_dict["Path"]))
            update(self.endpoint + "/{}".format("filename"), self.img_name_dict)

        else:

            if ".ims" not in image_name:
                image_name = image_name + ".ims"

            if self.image_dir not in image_name:
                self.img_name_dict["Path"] = os.path.join(self.image_dir, image_name)
            else:
                self.img_name_dict["Path"] = image_name

            self.img_name_dict["Path"] = os.path.join(self.image_dir, image_name)

            logger.log(level=20, msg="New image path: {}".format(self.img_name_dict["Path"]))

    def well_folder(self, wellcoords):
        well_dir = os.path.join(self.image_dir, "well_{}".format(wellcoords))
        if not os.path.exists(well_dir):
            os.mkdir(well_dir)
        return well_dir

    def z_stack(self, wellcoord="0 0", z_increment=5, n_aqcuisitions=10):
        # Set image name
        height = z_increment * n_aqcuisitions
        logger.log(level=20,
                   msg="Height travelled in total {} mm. Please determine from current position that this is safe".format(
                       height))
        wellcoord = wellcoord.replace(" ", "-")
        well_dir = self.well_folder(wellcoords=wellcoord)

        if self.test is False:
            for i in range(n_aqcuisitions):
                state, _ = self.microscope.get_current_z()
                z = self.microscope.move_z_axis(z_increment, state=state)  # Delay
                self.change_image_name(image_name=os.path.join(well_dir, "rawtake_n{}_well{}_zheigth{}".
                                                               format(i + 1, wellcoord, int(z))))

                fusionrest.run_protocol_completely("Protocol 59")
        else:
            paths = glob.glob("/media/ibrahim/Extended Storage/cloud/Internship/bioquant/348_wellplate_automation/test_rn/2024-03-05/*.ims")
            for i in range(n_aqcuisitions):
                state, _ = self.microscope.get_current_z()
                z = self.microscope.move_z_axis(z_increment, state=state)
                self.change_image_name(image_name=os.path.join(well_dir, "rawtake_n{}_well{}_zheigth{}".
                                                               format(i + 1, wellcoord, int(z))))

                os.rename(paths[i], self.img_name_dict["Path"])
                self.run_protocol()

        return well_dir

    # TODO continue working on image based autofocus
    # TODO the dicarded o,ages are not filtered to their new directory correctly
    def autofocusing(self, well_dir, autofocus_alg):

        # Get all recent z stack acquisitions
        img_paths = glob.glob(os.path.join(well_dir, "*.ims"))

        # Read .ims images
        func = getattr(self.autofocus, autofocus_alg, None)

        if func is not None and callable(func):
            f = [func(ims(img_path, squeeze_output=True)[-2:], os.path.basename(img_path)) for img_path in
            img_paths]  # Time point 0, Channel 0, z-layer 5
        else:
            f = "We have a problem"

        self.autofocus.turn2dt()
        # Best Z focus ?
        best_score = self.autofocus.variables[autofocus_alg].idxmax()

        # Save best score
        self.autofocus.variables["Estimated f"] = 0
        self.autofocus.variables.at[best_score, "Estimated f"] = 1

        # Make directory for out of focus images
        if not os.path.exists(os.path.join(well_dir, "discarded")):
            os.mkdir(os.path.join(well_dir, "discarded"))
        disc_dir = os.path.join(well_dir, "discarded")

        # Move out of focus images to new directory
        discarded_img_ids = self.autofocus.variables.loc[self.autofocus.variables.index != best_score, "Img_ID"].tolist()

        [os.replace(x, os.path.join(disc_dir, os.path.basename(x))) for x in img_paths if
         [y for y in discarded_img_ids if y in x]]

        self.autofocus.save2DT_excel(well_dir, self.autofocus.variables)

    def image_acquisition(self, wellcoord="0 0"):

        # TODO For this all uses must be confocal !!!!!!!!!!!!!!!

        well_f = self.autofocus.variables[(self.autofocus.variables["Well coords"] == wellcoord) &
                                          self.autofocus.variables["Estimated f"] == 1]["Z plane"]
        state, z = self.microscope.get_current_z()

        well_dir = self.well_folder(wellcoords=wellcoord)

        self.change_image_name(image_name=os.path.join(well_dir, self.image_name))

        self.microscope.move_z_axis(new_z_height=well_f, state=state)

        self.run_protocol()


if __name__ == '__main__':
    protocol = Protocol()

    print("Is this a test? ")
    answer = input()

    if answer.upper() == "NO":
        protocol.test = False
    else:
        protocol.test = True

    logger.log(level=20, msg="Current Protocol: {}".format(protocol.get_state()))

    logger.log(level=20, msg="Change name of image taken")
    protocol.change_image_name("New_picture")

    logger.log(level=20, msg="Protocol set to running")
    protocol.run_protocol()
    logger.log(level=20, msg="New state: {}".format(protocol.get_state()))

    logger.log(level=20, msg="Z stacking is on")
    welldir = protocol.z_stack()

    logger.log(level=20, msg="Autofocusing is on")
    protocol.autofocusing(welldir, autofocus_alg="Brenner")

    logger.log(level=20, msg="image acquisition is on")
    protocol.image_acquisition()
