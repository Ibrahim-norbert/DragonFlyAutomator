import logging
import os
import sys
from time import sleep
import numpy as np
import json
from DragonFlyWellPlateAutomation.devices import CoordinateTransforms as CT
from .xyzstage import XYZStage, get_output

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


# TODO go over the signature mismatch problem in the last method and include more logs

class WellPlate(XYZStage):
    def __init__(self):
        super().__init__()
        self.selected_wells = None
        self.well_plate_req_coords = {"Top left well": {}, "Bottom left well": {}, "Top right well": {}}
        self.corners_coords = None
        self.yspacing = None
        self.xspacing = None
        self.height = None
        self.length = None
        self.all_well_dicts = None
        self.homography_matrix = None
        self.c_n = None
        self.r_n = None
        self.homography_matrix_algorithm = None
        # TODO Add to protocol window
        self.homography_matrix_algorithms = ["Levenberg-Marquardt", "SVD"]
        self.coordinate_frame_algorithm = None
        self.coordinate_frame_algorithms = ["Linear spacing", "Linear correction matrix"]
        self.currentwellposition = None
        self.wellbywell = False
        self.non_linear_correction = True

    def get_state(self, test_key=None):

        if self.test is False:
            return {x: get_output(endpoint=self.endpoint + "/{}".format(x)) for x in
                    self.path_options}

        else:
            file = os.path.join(os.getcwd(), r"endpoint_outputs",
                                "{}xposition.json".format(test_key.replace(" well", "_")))
            f = open(file)
            x_ = json.load(f)
            # Opening JSON file
            file = os.path.join(os.getcwd(), r"endpoint_outputs",
                                "{}yposition.json".format(test_key.replace(" well", "_")))
            f = open(file)
            y_ = json.load(f)

            return {x: [x_, y_, None][id] for id, x in enumerate(self.path_options)}

    def state_dict_2_vector(self, state_dict):
        logger.log(level=10, msg='Value key: {}, Path options: {},'
                                 'State dictionary: {}'.format(self.value_key, self.path_options, state_dict))
        return np.array(
            [state_dict[self.path_options[0]][self.value_key], state_dict[self.path_options[1]][self.value_key]])

    def vector_2_state_dict(self, vector):
        return {self.path_options[0]: {self.value_key: vector[0]}, self.path_options[1]: {self.value_key: vector[1]},
                self.path_options[-1]: {self.value_key: False}}

    def get_corner_as_vectors(self):

        print("1. Getting all four corner wells coordinates as vectors")

        try:
            specified_vectors = [self.state_dict_2_vector(self.well_plate_req_coords["Top right well"]),
                                 self.state_dict_2_vector(self.well_plate_req_coords["Top left well"]),
                                 self.state_dict_2_vector(self.well_plate_req_coords["Bottom left well"])]

            # Top right, Bottom left = Bottom right
            specified_vectors = specified_vectors + [np.array([specified_vectors[-3][0], specified_vectors[-1][1]])]

            # Add bottom left well

            topleft = specified_vectors[1].astype(float)
            bottomleft = specified_vectors[2].astype(float)
            topright = specified_vectors[0].astype(float)
            bottomright = specified_vectors[3].astype(float)

            logger.log(level=20, msg="Well plate dimension: state dict as vectors {}".format(specified_vectors))

            return topleft, bottomleft, topright, bottomright

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.exception("State dict might be None", exc_info=True)

    def createwellplatestatedict(self, wellcoords_key, vectors):

        all_well_dicts = {wellcoords_key: self.vector_2_state_dict(vector) for wellcoords_key,
        vector in zip(wellcoords_key, vectors)}
        return all_well_dicts

    def set_parameters(self, well_names, vectors,
                       r_n, c_n, length, height, x_spacing, y_spacing, algorithm_CF, algorithm_H):

        print("Saving all variables associated to the coordinate system.")

        H = CT.homography_matrix_estimation(algorithm_H, vectors, well_names)

        self.coordinate_frame_algorithm = algorithm_CF
        self.homography_matrix_algorithm = algorithm_H
        self.r_n = r_n
        self.c_n = c_n
        self.all_well_dicts = self.createwellplatestatedict(well_names, vectors)
        self.length = length
        self.height = height
        self.xspacing = x_spacing
        self.yspacing = y_spacing
        self.corners_coords = [vectors[x] for x in [0, c_n - 1, (r_n * c_n) - c_n,
                                                    (r_n * c_n) - 1]]  # Top left, Top right, Bottom left
        self.homography_matrix = H

        logger.log(level=20, msg="Well plate matrix dimension: rows: {}, columns: {}".format(r_n, c_n))
        logger.log(level=20, msg="Well plate corner coordinates: {}".format(self.corners_coords))
        logger.log(level=20, msg="Well plate dimension: length - {}, height - {}".format(length, height))
        logger.log(level=20, msg="Computed well spacing: x:spacing = {} and y_spacing = {}".format(
            x_spacing, y_spacing))

    def predict_well_coords(self, c_n, r_n, algorithm="linear spacing", algorithm_H="non-linear"):

        topleft, bottomleft, topright, bottomright = self.get_corner_as_vectors()

        print("2. Computing coordinate space from well corners using {}".format(algorithm))

        if algorithm == self.coordinate_frame_algorithms[0]:
            vectors, well_names, length, height, x_spacing, y_spacing = CT.linearspacing(topright, topleft,
                                                                                         bottomright,
                                                                                         bottomleft, c_n=c_n,
                                                                                         r_n=r_n)
        else:
            vectors, well_names, length, height, x_spacing, y_spacing = CT.linearcorrectionmatrix(topright, topleft,
                                                                                                  bottomright,
                                                                                                  bottomleft,
                                                                                                  c_n=c_n,
                                                                                                  r_n=r_n)
            algorithm = self.coordinate_frame_algorithms[1]

        # Save all variables as parameters
        self.set_parameters(well_names, vectors,
                            r_n, c_n, length, height, x_spacing, y_spacing,
                            algorithm_CF=algorithm, algorithm_H=algorithm_H)

        return vectors, well_names, length, height, x_spacing

    # TODO Create widget that gives option for mapping
    def mapwellintegercoords2alphabet(self, wellcoords_key):
        r_str, c_str = wellcoords_key.split("-")
        r, c = int(r_str), int(c_str)
        label = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".upper()[r] + c_str
        return label, r_str, c_str, r, c

    # TODO Include widget for mandatory calibration in protocol window
    def mapwell2xyzstagecoords(self, c, r, non_linear_correction=True):
        if non_linear_correction is False:
            xyz_vector = CT.homography_application(self.homography_matrix, c, r)
        else:
            blpred = CT.homography_application(self.homography_matrix, 1, self.r_n)
            xyz_vector = CT.homography_fixit_calibration(blpred, self.bl, self.homography_matrix,
                                                         c, r, self.c_n, self.r_n)
        return xyz_vector

    def move2coord(self, state_dict):

        # Configure drawer

        try:
            # Move stage to well
            #
            logger.log(level=20, msg="Stage has its position updated")

            # Wait until we reach well position
            if self.test is False:
                self.update_state(state_dict, analoguecontrol_bool=False)
                count = 0
                while self.state_dict_2_vector(self.get_state()) != self.state_dict_2_vector(state_dict):
                    logger.log(level=20, msg="Stage is moving to new position")
                    if count == 60:
                        sys.exit("XYZ-stage failed to reach well position. Current {} and target {}. Please look at"
                                 "log file to find any errors".format(self.state_dict_2_vector(state_dict),
                                                                      self.state_dict_2_vector(self.get_state())))
                    count += 1
                    sleep(1)
            else:
                #length = np.linalg.norm(np.array([0, 0]) - np.array(self.state_dict_2_vector(state_dict)))
                logger.log(level=20, msg="Stage is moving to new position")
                sleep(10)

            logger.log(level=20, msg="Stage has arrived at target position")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logger.exception("What happened here ", exc_info=True)

    def save_attributes2json(self, partnumber, manufacturer):

        # Create a dictionary with attribute names and values
        attributes = {key: attr for key, attr in self.__dict__.items() if
                      not callable(attr)}

        # Create a dictionary with attribute names and values
        attributes = {key: attr.tolist() if isinstance(attr, np.ndarray) else attr for key,
        attr in attributes.items()}

        with open(os.path.join(os.getcwd(), "models", '{}_WellPlate_{}_{}.json'.format(self.c_n * self.r_n, partnumber,
                                                                                       manufacturer)), 'w') as f:
            json.dump(attributes, f)

    def load_attributes(self, name):
        f = open(os.path.join(os.getcwd(), "models", '{}'.format(name)))
        attributes = json.load(f)
        self.__dict__.update(attributes)
        self.wellbywell = True

    def automated_wp_movement(self, selected_wellbuttons):
        state_dict, coords, wellname = selected_wellbuttons

        # Draw graph only when xyz-stage has arrived at well
        self.move2coord(state_dict)  # Delay

        # TODO a) To check quality of current session: compare linearspacing coordinates to linear correction matrix
        # TODO b) To check quality between current and subsequent session: compare current session to homography prediction
        # TODO c) To check quality of subsequent session: compare Homography with nonlinear correction and Homography calibration

        vector = self.state_dict_2_vector(state_dict)

        # Once data has been processed, we remove it
        self.selected_wells.pop(0)

        return vector, wellname


def main():
    import argparse

    parser = argparse.ArgumentParser(description='train a phase registration model')
    parser.add_argument("--rows", type=int, required=False, help="Enter number of rows", default=16)
    parser.add_argument("--columns", type=int, required=False, help="Enter number of columns", default=24)

    keys = ["Top right well", "Top left well", "Bottom left well"]

    wellplate = WellPlate()

    for test_key in keys:
        # Opening JSON file
        file = os.path.join(os.getcwd(), r"endpoint_outputs", "{}xposition.json".format(test_key.replace(" well", "_")))
        f = open(file)
        x_ = json.load(f)
        # Opening JSON file
        file = os.path.join(os.getcwd(), r"endpoint_outputs", "{}yposition.json".format(test_key.replace(" well", "_")))
        f = open(file)
        y = json.load(f)

        wellplate.well_plate_req_coords[test_key] = {x: [x_, y, None][id] for id,
        x in enumerate(["xposition", "yposition"])}

    print("Before update: " + str(wellplate.__dict__))

    args = parser.parse_args()

    # Predict well cords from corners
    wellplate.predict_well_coords(args.columns, args.rows)

    print("After update: " + str(wellplate.__dict__))

    # Save the attributes
    wellplate.save_attributes2json(partnumber="12345", manufacturer="Falcon")

    # Test if wellplate can load attributes

    wellplate2 = WellPlate()

    wellplate2.load_attributes(name="384_falcon_wellplate.json")

    print("After loading attributes: " + str(wellplate2.__dict__))

    print("-----------------------------------------------------")

    print("Testing well plate row and column arrangement mapping to xyz-stage coordinate system: ")
    print(" ")
    print(" ")
    print(" ")

    wellplate2.predict_well_coords(args.columns, args.rows)


if __name__ == '__main__':
    main()
