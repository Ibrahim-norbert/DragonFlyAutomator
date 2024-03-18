import glob
import logging
import os
import shutil
import time

from imaris_ims_file_reader.ims import ims
import json
from .micrscope import Microscope
from .image_based_autofocus import AutoFocus

from .xyzstage import FusionApi, get_output, update
from DragonFlyWellPlateAutomation.RestAPI import fusionrest

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


# TODO Need to move all files to the discarded folder and perform the focal plane acquisition in the root directory
class Protocol(FusionApi):
    def __init__(self, img_dir):
        super().__init__()  # inherits

        self.variables = None
        self.image_array = None
        self.endpoint = self.endpoint + "/{}".format("protocol")

        # TODO Calibrate starting z position using fusion, then use the autofocus
        self.autofocus = AutoFocus()
        self.autofocus_algorithm = None
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
        self.image_dir = img_dir  # os.path.join(os.getcwd(), "test_rn")
        self.img_name_dict = self.get_image_dir()

        # Only for live image acquisition method
        self.image_name = None  # "Phalloidin_Hoechst_GfP_HeLa"

        self.non_linear_correction = True

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
            time.sleep(5)
            logger.log(level=20, msg="Running protocol: {}".format(self.current_output.values()))

    def get_image_dir(self):
        if self.test is False:
            img_name_dict = get_output(os.path.dirname(self.endpoint) + "/{}".format("datasets"))
            return img_name_dict, os.path.split(img_name_dict["Path"])[0]
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", "dataset.json"))
            img_name_dict = json.load(f)
            return img_name_dict

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

    def well_folder(self, wellname):
        well_dir = os.path.join(self.image_dir, "well_{}".format(wellname))
        if not os.path.exists(well_dir):
            os.mkdir(well_dir)
        return well_dir

    def z_stack(self, wellname="0 0", z_increment=5, n_acquisitions=10):

        logger.log(level=20, msg="Z stack begins for well: {}".format(wellname))

        # Maximum z plane displacement
        height = z_increment * n_acquisitions
        logger.log(level=20,
                   msg="Total height to travel {} mm. Please determine from current position that this "
                       "is safe".format(height))

        # Get well folder
        well_dir = self.well_folder(wellname=wellname)

        if self.test is False:
            for i in range(n_acquisitions):
                logger.log(level=20, msg="Acquisition number {} of well {}".format(i + 1, wellname))

                # Request current z position
                state, _ = self.microscope.get_current_z()

                # Request update to target z position
                z = self.microscope.move_z_axis(z_increment)  # Delay

                # Request path change for saving images
                path = os.path.join(well_dir, "rawtake_n{}_well{}_zheigth{}".
                                    format(i + 1, wellname, int(z)))
                self.change_image_name(image_name=path)

                # Request image acquisition
                fusionrest.run_protocol_completely("Protocol 59")

                logger.log(level=20, msg="Got image with shape: {}".format(self.image_array.shape))
        else:
            paths = glob.glob(os.path.join(os.getcwd(), "test_rn", "2024-03-05", "*.ims"))
            for i in range(n_acquisitions):
                state, _ = self.microscope.get_current_z()
                z = self.microscope.move_z_axis(z_increment)
                # Request path change for saving images
                path = os.path.join(well_dir, "rawtake_n{}_well{}_zheigth{}".
                                    format(i + 1, wellname, int(z)))
                self.change_image_name(image_name=path)
                shutil.copy2(paths[i], self.img_name_dict["Path"])
                self.run_protocol()

        # Return to original height
        logger.log(level=20, msg="Z stack done for well and returning to original z height: {}".format(wellname))
        self.microscope.return2start_z()

        return well_dir, wellname

    def autofocusing(self, wellname):

        start = time.time()

        # Get well folder
        well_dir, wellname = self.z_stack(wellname, self.z_increment, self.n_acquisitions)

        logger.log(level=20, msg="Autofocus begins for well: {}".format(wellname))

        # Get all recent z stack acquisitions
        img_paths = glob.glob(os.path.join(well_dir, "*.ims"))

        logger.log(level=20, msg="The affected images are: {}".format(img_paths))

        # Get autofocus algorithm
        func = getattr(self.autofocus, self.autofocus_algorithm)

        # Read .ims images
        if func is not None and callable(func):
            [func(ims(img_path, squeeze_output=True), os.path.basename(img_path)) for img_path in
             img_paths]  # Time point 0, Channel 0, z-layer 5
            logger.log(level=20, msg="Image quality metric applied to all z-stack images")
        else:
            logger.log(level=20, msg="Image quality metric cannot be found.")

        logger.log(level=20, msg="Here we have the columns of dictionary before: "
                                 "".format(list(self.autofocus.variables.keys())))

        # Turn the dictionary into a dataframe
        self.variables = self.autofocus.turn2dt()

        logger.log(level=20, msg="Here we have the columns of the newly created dataframe: "
                                 "".format(list(self.variables.columns)))

        # Index the best image
        subdt = self.variables[self.variables["Metrics"] == func.__name__]
        best_score = subdt["Value"].idxmax()

        # Indicate the best score
        self.variables.loc[:, "Estimated f"] = 0
        self.variables.at[best_score, "Estimated f"] = 1

        # Index the z height of the best image
        well_f = self.variables.loc[best_score, "Z plane"].tolist()

        # Request update to target z position
        self.microscope.move_z_axis(new_z_height=well_f)

        # Make directory for out of focus images
        if not os.path.exists(os.path.join(well_dir, "discarded")):
            os.mkdir(os.path.join(well_dir, "discarded"))
        disc_dir = os.path.join(well_dir, "discarded")

        # Move out of focus images to new directory
        discarded_img_ids = self.variables.loc[
            self.variables.index != best_score, "Img_ID"].tolist()

        [os.replace(x, os.path.join(disc_dir, os.path.basename(x))) for x in img_paths if
         [y for y in discarded_img_ids if y in x]]

        self.variables.loc[:, "Elapsed time"] = time.time() - start

        # Save dataframe in well directory
        self.autofocus.save2DT_excel(well_dir, self.variables)

    def image_acquisition(self, wellname="0-0"):
        # Return well folder
        well_dir = self.well_folder(wellname=wellname)

        # Request path change for saving images
        self.change_image_name(image_name=os.path.join(well_dir, self.image_name))

        if self.test is False:

            # Request image acquisition using currently selected protocol
            self.run_protocol()
        else:
            img = "/media/ibrahim/Extended Storage/cloud/Internship/bioquant/348_wellplate_automation/test_rn/2024-03-05/rawtake_n7_well0-0_zheigth452.ims"
            shutil.copy2(img, os.path.join(well_dir, self.image_name))

        return os.path.join(well_dir, self.image_name)

    def savedatafromexecution(self, vector, wellbywell, coordinate_frame_algorithm, homography_matrix_algorithm):

        # Save xyz stage coordinates
        self.variables.loc[:, "x"] = vector[0]
        self.variables.loc[:, "y"] = vector[1]
        self.variables.loc[:,
        "Type prediction"] = "Homography" if wellbywell is True else "A priori grid"

        self.variables.loc[:,
        "Type prediction"] = 1 if self.non_linear_correction is True or coordinate_frame_algorithm == \
                                  "Linear correction matrix" else 0
        self.variables.loc[:,
        "Type homography prediction"] = homography_matrix_algorithm
        self.variables.loc[:, "Type grid prediction"] = coordinate_frame_algorithm

    def processwell(self, vector, wellname, wellbywell, coordinate_frame_algorithm, homography_matrix_algorithm):

        # Perform autofocus
        self.autofocusing(wellname=wellname)  # Significant delay

        # Obtain image with current protocol
        img_path = self.image_acquisition(wellname=wellname)  # Delay

        logger.log(level=20, msg="Path of image: {}".format(img_path))
        # Save data
        self.savedatafromexecution(vector, wellbywell, coordinate_frame_algorithm, homography_matrix_algorithm)


        return img_path


def main():
    import argparse

    parser = argparse.ArgumentParser(description='train a phase registration model')
    parser.add_argument("--img_name", type=str, required=False, help="Enter image name",
                        default="Session")
    parser.add_argument("--well_coords", type=str, required=True, help="Enter well coordinates as 0-0 "
                                                                       "instead of A1")
    parser.add_argument("--z_spacing", type=float, required=True, help="Enter z spacing for z-stack")
    parser.add_argument("--n_acquisitions", type=int, required=True, help="Enter number of acquisitions "
                                                                          "in z-stack")
    parser.add_argument("--autofocus_alg", type=str, required=True,
                        help="Choose autofocus algorithm: " + str(AutoFocus().metrics))
    parser.add_argument("--image_dir", type=str, required=True, help="Enter the image directory path")

    args = parser.parse_args()

    imagename = args.img_name
    wellcoord = args.well_coords
    z_spacing = args.z_spacing
    n_aqcuisitions = args.n_acquisitions
    autofocus_alg = args.autofocus_alg

    protocol = Protocol(args.image_dir)

    print("This is a test run, no change in state of the microscope is performed.")

    protocol.test = True

    protocol.image_name = imagename
    protocol.autofocus_algorithm = autofocus_alg

    logger.log(level=20, msg="Current Protocol: {}".format(protocol.get_state()))

    logger.log(level=20, msg="Change name of image taken")
    protocol.change_image_name(image_name=imagename)

    logger.log(level=20, msg="Protocol set to running")
    protocol.run_protocol()
    logger.log(level=20, msg="New state: {}".format(protocol.get_state()))

    logger.log(level=20, msg="Z stacking is on")
    welldir, wellcoord = protocol.z_stack(wellname=wellcoord, z_increment=z_spacing, n_acquisitions=n_aqcuisitions)

    logger.log(level=20, msg="Autofocusing is on")
    protocol.autofocusing(wellcoord)

    logger.log(level=20, msg="image acquisition is on")
    protocol.image_acquisition(wellcoord)


if __name__ == '__main__':
    main()
