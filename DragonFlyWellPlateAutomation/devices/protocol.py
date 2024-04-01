import glob
import json
import logging
import os
import shutil
import time

from imaris_ims_file_reader.ims import ims

from DragonFlyWellPlateAutomation.RestAPI import fusionrest
from DragonFlyWellPlateAutomation.devices.image_based_autofocus import AutoFocus
from DragonFlyWellPlateAutomation.devices.micrscope import Microscope
from DragonFlyWellPlateAutomation.devices.xyzstage import FusionApi, get_output, update

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


# TODO Need to move all files to the discarded folder and perform the focal plane acquisition in the root directory
class Protocol(FusionApi):
    def __init__(self):
        super().__init__()  # inherits

        self.image_dir = None
        self.autofocus = AutoFocus()
        self.variables = None
        self.image_array = None
        self.endpoint = self.endpoint + "/{}".format("protocol")

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

    def run_protocol(self, protocol_name):
        if self.test is False:
            fusionrest.run_protocol_completely(protocol_name=protocol_name)
            logger.log(level=20, msg="Running protocol: {}".format(self.current_output.values()))
        else:
            time.sleep(5)
            logger.log(level=20, msg="Running protocol: {}".format(self.current_output.values()))

    def get_image_dir(self):
        if self.test is False:
            img_name_dict = get_output(os.path.dirname(self.endpoint) + "/{}".format("datasets/current"))
            return img_name_dict
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", "dataset.json"))
            img_name_dict = json.load(f)
            return img_name_dict

    def update_img_name(self, image_path):

        if ".ims" not in image_path:
            image_path = image_path + ".ims"

        if self.image_dir not in image_path:
            self.img_name_dict["Path"] = os.path.join(self.image_dir, image_path)
        else:
            self.img_name_dict["Path"] = image_path

        if self.test is False:
            logger.log(level=20, msg="New image path: {}".format(self.img_name_dict["Path"]))
            update(self.endpoint + "/{}".format("datasets/current"), self.img_name_dict)

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
            for direction in [True, False]:
                for i in range(n_acquisitions):
                    logger.log(level=20, msg="Acquisition number {} of well {}".format(i + 1, wellname))

                    # Request current z position
                    state, _ = self.microscope.get_current_z()

                    # Request update to target z position
                    z = self.microscope.move_z_axis({"up": direction, "Value": z_increment})  # Delay

                    # Request path change for saving images
                    img_path = os.path.join(well_dir, "rawtake_n{}_well{}_zheigth{}".
                                            format(i + 1, wellname, int(z)))

                    # Request image acquisition
                    self.image_acquisition(img_path, "Protocol 59")

                    logger.log(level=20, msg="Got image with shape: {}".format(self.image_array.shape))

                self.microscope.return2start_z()
        else:
            for direction in [True, False]:
                for i in range(n_acquisitions):
                    state, _ = self.microscope.get_current_z()
                    # Request update to target z position
                    z = self.microscope.move_z_axis({"up": direction, "Value": z_increment})  # Delay

                    # Request path change for saving images
                    img_path = os.path.join(well_dir, "rawtake_n{}_well{}_zheigth{}".
                                            format(i + 1, wellname, int(z)))

                    self.image_acquisition(img_path, "Protocol 59")

                self.microscope.return2start_z()

        # Return to original height
        logger.log(level=20, msg="Z stack done for well {}".format(wellname))

        return well_dir, wellname

    def load_ims_imgs(self, img_path):
        img = ims(img_path, squeeze_output=True)
        return img[0, :, 0].astype(float)

    def autofocusing(self, wellname, z_increment, n_acquisitions):

        start = time.time()

        logger.log(level=20, msg="Autofocus begins for well: {}".format(wellname))

        # Get well folder
        well_dir, wellname = self.z_stack(wellname, z_increment, n_acquisitions)

        # Get all recent z stack acquisitions
        img_paths = glob.glob(os.path.join(well_dir, "*.ims"))

        logger.log(level=20, msg="The affected images are: {}".format([os.path.basename(x) for x in img_paths]))

        # Get autofocus algorithm
        func = getattr(self.autofocus, self.autofocus_algorithm)

        # Refresh the autofocus variable
        self.autofocus.refresh()

        # Read .ims images
        if func is not None and callable(func):
            [func(self.load_ims_imgs(img_path), os.path.basename(img_path)) for img_path in
             img_paths]  # Time point 0, Channel 0, z-layer 5
            logger.log(level=20, msg="Image quality metric applied to all z-stack images")
        else:
            logger.log(level=20, msg="Image quality metric cannot be found.")

        logger.log(level=10, msg="Here we have the columns of dictionary before: {}"
                                 "".format(list(self.autofocus.variables.keys())))

        # Turn the dictionary into a dataframe
        self.variables = self.autofocus.turn2dt()

        logger.log(level=10, msg="Here we have the columns of the newly created dataframe: {}"
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

        self.variables.loc[:, "Elapsed time"] = time.time() - start

        return well_dir

    def image_acquisition(self, img_path, protocol_name):

        # Request path change for saving images
        self.update_img_name(image_path=img_path)

        if self.test is False:
            # Request image acquisition using currently selected protocol
            self.run_protocol(protocol_name)
        else:
            img = os.path.join(os.getcwd(), "test_rn/2024-03-05/rawtake_n7_well0-0_zheigth452.ims")
            shutil.copy2(img, self.img_name_dict["Path"])

        return self.img_name_dict["Path"]

    def savedatafromexecution(self, vector, coordinate_frame_algorithm, homography_matrix_algorithm, well_dir):

        # Save xyz stage coordinates
        self.variables.loc[:, "x"] = vector[0]
        self.variables.loc[:, "y"] = vector[1]

        self.variables.loc[:,
        "Type prediction"] = 1 if self.non_linear_correction is True or coordinate_frame_algorithm == \
                                  "Linear correction matrix" else 0
        self.variables.loc[:,
        "Type homography prediction"] = homography_matrix_algorithm
        self.variables.loc[:, "Type grid prediction"] = coordinate_frame_algorithm

        # Save dataframe in well directory
        self.autofocus.save2DT_excel(well_dir, self.variables)

    def processwell(self, vector, wellname, coordinate_frame_algorithm, homography_matrix_algorithm, z_spacing,
                    n_aqcuisitions, protocol_name, img_name):

        # Perform autofocus
        well_dir = self.autofocusing(wellname=wellname, z_increment=z_spacing,
                                     n_acquisitions=n_aqcuisitions)  # Significant delay

        # Obtain image with current protocol
        img_path = self.image_acquisition(os.path.join(well_dir, img_name), protocol_name)  # Delay

        logger.log(level=20, msg="Path of image: {}".format(img_path))
        # Save data
        self.savedatafromexecution(vector, coordinate_frame_algorithm, homography_matrix_algorithm, well_dir)

        return img_path
