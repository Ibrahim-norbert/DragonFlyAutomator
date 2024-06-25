import glob
import json
import logging
import os
import shutil
import time
import datetime

from imaris_ims_file_reader.ims import ims

from DragonFlyWellPlateAutomation.RestAPI import fusionrest
from DragonFlyWellPlateAutomation.devices.image_based_autofocus import AutoFocus
from DragonFlyWellPlateAutomation.devices.micrscope import Microscope
from DragonFlyWellPlateAutomation.devices.xyzstage import FusionApi, get_output, update

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


class Protocol(FusionApi):
    def __init__(self, test=True):
        super().__init__()  # inherits

        self.test = test

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
        self.image_dir = os.path.dirname(self.img_name_dict["Path"])


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

            logger.log(level=20, msg="Running protocol: {}".format(fusionrest.get_protocol_name()))
            fusionrest.run_protocol_completely(protocol_name=protocol_name)

        else:
            time.sleep(5)
            logger.log(level=20, msg="Running protocol: {}".format(self.current_output.values()))

    def get_image_dir(self):
        if self.test is False:
            img_name_dict = get_output(os.path.dirname(self.endpoint) + "/{}".format("datasets/current"))
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs/datasets.json"))
            img_name_dict = json.load(f)

        logger.log(level=20, msg="Image directory given as: {}".format(img_name_dict["Path"]))
        return img_name_dict

    def update_img_name(self, image_path):
        pass

        # if ".ims" not in image_path:
        #     image_path = image_path + ".ims"
        #
        # if self.image_dir not in image_path:
        #     self.img_name_dict["Path"] = os.path.join(self.image_dir, image_path)
        # else:
        #     self.img_name_dict["Path"] = image_path
        #
        # if self.test is False:
        #     logger.log(level=20, msg="New image path: {}".format(self.img_name_dict["Path"]))
        #     update(self.endpoint + "/{}".format("datasets/current"), self.img_name_dict)

    def well_folder(self, wellname):
        well_dir = os.path.join(os.path.dirname(self.image_dir), "well_{}".format(wellname))
        if not os.path.exists(well_dir):
            os.mkdir(well_dir)
        return well_dir

    def z_stack(self, wellname="0 0", z_increment=5, n_acquisitions=10):

        self.microscope.starting_z_height = self.microscope.get_current_z()[-1]

        logger.log(level=20, msg="Z stack begins for well: {}".format(wellname))

        # Maximum z plane displacement
        height = z_increment * n_acquisitions
        logger.log(level=20,
                   msg="Total height to travel {} mm. Please determine from current position that this "
                       "is safe".format(height))

        # Info
        z_heights = []
        acquisition_n = []

        if self.test is False:
            for direction in [True, False]:
                for i in range(n_acquisitions):
                    logger.log(level=20, msg="Acquisition number {} of well {}".format(i + 1, wellname))

                    # Request current z position
                    state, _ = self.microscope.get_current_z()

                    # Request update to target z position
                    z = self.microscope.move_z_axis({"up": direction, "Value": z_increment})  # Delay

                    z_heights.append(z)
                    acquisition_n.append(i)

                    # Request image acquisition
                    self.image_acquisition("Protocol 59")

                self.microscope.return2start_z()
        else:
            for direction in [True, False]:
                for i in range(n_acquisitions):
                    state, _ = self.microscope.get_current_z()
                    # Request update to target z position
                    z = self.microscope.move_z_axis({"up": direction, "Value": z_increment})  # Delay

                    # Request path change for saving images
                    if isinstance(z, str):
                        z = eval(z)

                    z_heights.append(z)
                    acquisition_n.append(i)

                    self.image_acquisition("Protocol 59")

                self.microscope.return2start_z()

        # Return to original height
        logger.log(level=20, msg="Z stack done for well {}".format(wellname))

        return z_heights, acquisition_n

    def load_ims_imgs(self, img_path):
        img = ims(img_path, squeeze_output=True)
        return img[0, :, 0].astype(float)  # time point, channel, z level

    def autofocusing(self, wellname, z_increment, n_acquisitions):

        start = time.time()  # Start time

        logger.log(level=20, msg="Autofocus begins for well: {}".format(wellname))

        # Perform z stack
        z_heights, acquisition_n = self.z_stack(wellname, z_increment, n_acquisitions)
        logger.log(level=20, msg="Obtaining images from the following directory: {}".format(
            self.image_dir))

        if self.test is True:
            img_paths = glob.glob(
                os.path.join(os.path.dirname(self.image_dir), "*Protocol 59*.ims"))
        else:
            img_paths = glob.glob(
                os.path.join(self.image_dir, "*Protocol 59*.ims"))

        n_imgs = 2 * n_acquisitions
        if len(img_paths) > n_imgs:
            img_paths.sort(key=os.path.getmtime)
            img_paths = img_paths[-n_imgs:]

        logger.log(level=20, msg="The affected images are: {}".format([os.path.basename(x) for x in img_paths]))

        # Get autofocus algorithm
        func = getattr(self.autofocus, self.autofocus_algorithm)

        # Refresh the autofocus variable
        self.autofocus.refresh()

        # Populate autofocus variable
        if func is not None and callable(func):
            [func(self.load_ims_imgs(img_path), (z_heights[indx], acquisition_n[indx],
                                                 wellname, os.path.basename(img_path))) for indx, img_path in
             enumerate(img_paths)]  # Time point 0, Channel 0, z-layer 5
            logger.log(level=20, msg="Image quality metric applied to all z-stack images")
        else:
            logger.log(level=20, msg="Image quality metric cannot be found.")

        # Turn the dictionary into a dataframe
        self.variables = self.autofocus.turn2dt()

        # Get focal plane
        self.variables, well_f = self.determinefocalplane(func, self.variables)  ## Added this function 02.04

        # Request update to focal z position
        self.microscope.move_z_axis(new_z_height=well_f)  ## Made this function more compact 02.04

        timer = time.time() - start
        self.variables.loc[:, "Elapsed time"] = timer

        logger.log(level=20, msg="Autofocus ended for well {} with elapsed time: {}".format(wellname, timer))

    def determinefocalplane(self, func, dt):

        # Index the best image
        subdt = dt[dt["Metrics"] == func.__name__]
        best_score = subdt["Value"].idxmax()

        # Indicate the best score
        dt.loc[:, "Estimated f"] = 0
        dt.at[best_score, "Estimated f"] = 1

        # Index the z height of the best image
        well_f = dt.loc[best_score, "Z plane"].tolist()

        return dt, well_f

    def image_acquisition(self, protocol_name):

        if self.test is False:
            # Request image acquisition using currently selected protocol
            self.run_protocol(protocol_name)
        else:
            timestemp = str(datetime.datetime.now().strftime(
                "%Y-%m-%d_%H_%M"))
            img_path_old = os.path.join(os.getcwd(), "test/test_dir/rawtake_n1_well3-2_zheigth485.ims")
            ### Apply root directory of img name dict only in test
            img_path = os.path.join(os.path.dirname(self.image_dir),
                                    "{}_{}.ims".format(protocol_name, timestemp))
            shutil.copy2(img_path_old, img_path)

    def savedatafromexecution(self, vector, coordinate_frame_algorithm, homography_matrix_algorithm, wellname):

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
        self.autofocus.save2DT_excel(self.well_folder(wellname=wellname), self.variables)

    def processwell(self, vector, wellname, coordinate_frame_algorithm, homography_matrix_algorithm, z_spacing,
                    n_aqcuisitions, protocol_name):

        # Perform autofocus
        self.autofocusing(wellname=wellname, z_increment=z_spacing,
                          n_acquisitions=n_aqcuisitions)  # Significant delay

        # Obtain image with current protocol
        self.image_acquisition(protocol_name)  # Delay

        self.microscope.return2start_z()

        # Save data
        self.savedatafromexecution(vector, coordinate_frame_algorithm, homography_matrix_algorithm, wellname)
