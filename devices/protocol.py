import glob
import logging
import os
from imaris_ims_file_reader.ims import ims
import shutil
from RestAPI import fusionrest
from devices.image_based_autofocus import AutoFocus
from devices.micrscope import Microscope
from devices.xyzstage import FusionApi, get_output, update

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class Protocol(FusionApi):
    def __init__(self):
        super().__init__()  # inherits

        self.endpoint = self.endpoint + "/{}".format("protocol")
        self.autofocus = AutoFocus()
        self.microscope = Microscope()

        if self.test is False:
            self.current_output = self.get_state()
            self.protocol_name = fusionrest.get_protocol_name()
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", os.path.basename(self.endpoint) + "_current.json"))
            self.current_output = json.load(f)

        # For z-stack algorithm
        self.z_increment = None
        self.n_acquisitions = None
        self.image_dir = None  # os.path.join(os.getcwd(), "test_rn")
        self.img_name_dict, _ = self.get_image_dir()

        # Only for live image acquisition method
        self.image_name = None  # "Phalloidin_Hoechst_GfP_HeLa"


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

    def get_image_dir(self):
        if self.test is False:
            img_name_dict = get_output(os.path.dirname(self.endpoint) + "/{}".format("datasets"))
            return img_name_dict, os.path.split(img_name_dict["Path"])[0]
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", "dataset.json"))
            img_name_dict = json.load(f)
            return img_name_dict, os.path.split(img_name_dict["Path"])[0]

    def change_image_name(self, image_name):

        if ".ims" not in image_name:
            image_name = image_name + ".ims"

        if self.image_dir not in image_name:
            self.img_name_dict["Path"] = os.path.join(self.image_dir, image_name)
        else:
            self.img_name_dict["Path"] = image_name

        if self.test is False:
            logger.log(level=20, msg="New image path: {}".format(self.img_name_dict["Path"]))
            update(self.endpoint + "/{}".format("filename"), self.img_name_dict)

    def well_folder(self, wellcoords):
        well_dir = os.path.join(self.image_dir, "well_{}".format(wellcoords))
        if not os.path.exists(well_dir):
            os.mkdir(well_dir)
        return well_dir

    def z_stack(self, wellcoord="0 0", z_increment=5, n_aqcuisitions=10):

        # Maximum z plane displacement
        height = z_increment * n_aqcuisitions
        logger.log(level=20,
                   msg="Height travelled in total {} mm. Please determine from current position that this "
                       "is safe".format(height))

        # Get well folder
        wellcoord = wellcoord.replace(" ", "-")
        well_dir = self.well_folder(wellcoords=wellcoord)

        if self.test is False:
            for i in range(n_aqcuisitions):
                # Request current z position
                state, _ = self.microscope.get_current_z()

                # Request update to target z position
                z = self.microscope.move_z_axis(z_increment, state=state)  # Delay

                # Request path change for saving images
                self.change_image_name(image_name=os.path.join(well_dir, "rawtake_n{}_well{}_zheigth{}".
                                                               format(i + 1, wellcoord, int(z))))

                # Request image acquisition
                fusionrest.run_protocol_completely("Protocol 59")
        else:
            paths = glob.glob(os.path.join(os.getcwd(), "test_rn", "2024-03-05", "*.ims"))
            for i in range(n_aqcuisitions):
                state, _ = self.microscope.get_current_z()
                z = self.microscope.move_z_axis(z_increment, state=state)
                self.change_image_name(image_name=os.path.join(well_dir, "rawtake_n{}_well{}_zheigth{}".
                                                               format(i + 1, wellcoord, int(z))))

                shutil.copy2(paths[i], self.img_name_dict["Path"])
                self.run_protocol()

        return well_dir, wellcoord

    def autofocusing(self, well_dir, autofocus_alg):

        # Get all recent z stack acquisitions
        img_paths = glob.glob(os.path.join(well_dir, "*.ims"))

        # Get autofocus algorithm
        func = getattr(self.autofocus, autofocus_alg)

        # Read .ims images
        if func is not None and callable(func):
            [func(ims(img_path, squeeze_output=True)[-2:], os.path.basename(img_path)) for img_path in
             img_paths]  # Time point 0, Channel 0, z-layer 5
            logger.log(level=20, msg="Image quality metric applied to all z-stack images")
        else:
            logger.log(level=20, msg="Image quality metric cannot be found.")

        # Turn the dictionary into a dataframe
        self.autofocus.turn2dt()

        # Index the best image
        best_score = self.autofocus.variables[autofocus_alg].idxmax()

        # Indicate the best score
        self.autofocus.variables["Estimated f"] = 0
        self.autofocus.variables.at[best_score, "Estimated f"] = 1

        # Make directory for out of focus images
        if not os.path.exists(os.path.join(well_dir, "discarded")):
            os.mkdir(os.path.join(well_dir, "discarded"))
        disc_dir = os.path.join(well_dir, "discarded")

        # Move out of focus images to new directory
        discarded_img_ids = self.autofocus.variables.loc[
            self.autofocus.variables.index != best_score, "Img_ID"].tolist()

        [os.replace(x, os.path.join(disc_dir, os.path.basename(x))) for x in img_paths if
         [y for y in discarded_img_ids if y in x]]

        # Save dataframe in well directory
        self.autofocus.save2DT_excel(well_dir, self.autofocus.variables)

    def image_acquisition(self, wellcoord="0-0"):

        # Index the z height of the best image
        well_f = self.autofocus.variables[(self.autofocus.variables["Well coords"] == wellcoord) &
                                          (self.autofocus.variables["Estimated f"] == 1.)]["Z plane"].tolist()[0]

        # Request current z position
        state, z = self.microscope.get_current_z()

        # Return well folder
        well_dir = self.well_folder(wellcoords=wellcoord)

        # Request path change for saving images
        self.change_image_name(image_name=os.path.join(well_dir, self.image_name))

        # Request update to target z position
        self.microscope.move_z_axis(new_z_height=well_f, state=state)

        # Request image acquisition using currently selected protocol
        self.run_protocol()


if __name__ == '__main__':

    import argparse
    import json

    parser = argparse.ArgumentParser(description='train a phase registration model')
    parser.add_argument("--img_name", type=str, required=False, help="Enter image name",
                        default="Session")
    parser.add_argument("--well_coords", type=str, required=True, help="Enter well coordinates as 0-0 "
                                                                       "instead of A1")
    parser.add_argument("--z_spacing", type=float, required=True, help="Enter z spacing for z-stack")
    parser.add_argument("--n_acquisitions", type=float, required=True, help="Enter number of acquisitions "
                                                                            "in z-stack")
    parser.add_argument("--autofocus_alg", type=str, required=True,
                        help="Choose autofocus algorithm: " + str(AutoFocus().metrics))
    parser.add_argument("--image_dir", type=str, required=True, help="Enter the image directory path")

    args = parser.parse_args()

    imagename = args.img_name
    wellcoord = args.well_coords
    z_increment = args.z_spacing
    n_aqcuisitions = args.n_acquisitions
    autofocus_alg = args.autofocus_alg

    protocol = Protocol()

    print("This is a test run, no change in state of the microscope is performed.")

    protocol.test = True

    logger.log(level=20, msg="Current Protocol: {}".format(protocol.get_state()))

    logger.log(level=20, msg="Change name of image taken")
    protocol.change_image_name(image_name=imagename)

    logger.log(level=20, msg="Protocol set to running")
    protocol.run_protocol()
    logger.log(level=20, msg="New state: {}".format(protocol.get_state()))

    logger.log(level=20, msg="Z stacking is on")
    welldir, wellcoord = protocol.z_stack(wellcoord=wellcoord, z_increment=z_increment, n_aqcuisitions=n_aqcuisitions)

    logger.log(level=20, msg="Autofocusing is on")
    protocol.autofocusing(welldir, autofocus_alg=autofocus_alg)

    logger.log(level=20, msg="image acquisition is on")
    protocol.image_acquisition(wellcoord)
