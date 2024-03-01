from devices.xyzstage import XYZStage
import logging
import numpy as np
import os
from time import sleep
import devices.CoordinateTransforms as CT

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class WellPlate(XYZStage):
    def __init__(self):
        super().__init__()
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
        self.coordinate_frame_algorithm = None

    def state_dict_2_vector(self, state_dict):
        logging.log(level=10, msg='Value key: {}, Path options: {},'
                                  'State dictionary: {}'.format(self.value_key, self.path_options, state_dict))
        return np.array(
            [state_dict[self.path_options[0]][self.value_key], state_dict[self.path_options[1]][self.value_key]])

    def vector_2_state_dict(self, vector):
        return {self.path_options[0]: {self.value_key: vector[0]}, self.path_options[1]: {self.value_key: vector[1]},
                self.path_options[-1]: {self.value_key: False}}

    def get_corner_as_vectors(self):

        try:
            specified_vectors = [self.state_dict_2_vector(self.well_plate_req_coords["Top right well"]),
                                 self.state_dict_2_vector(self.well_plate_req_coords["Top left well"]),
                                 self.state_dict_2_vector(self.well_plate_req_coords["Bottom left well"])]

            specified_vectors = specified_vectors + [np.array([specified_vectors[-3][0], specified_vectors[-1][1]])]

            # Add bottom left well

            topleft = specified_vectors[-3].astype(float)
            bottomleft = specified_vectors[-2].astype(float)
            topright = specified_vectors[-4].astype(float)
            bottomright = specified_vectors[-1].astype(float)

            logging.log(level=20, msg="Well plate dimension: state dict as vectors {}".format(specified_vectors))

            return topleft, bottomleft, topright, bottomright

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("State dict might be None", exc_info=True)

    def set_parameters(self, well_names, vectors,
                       r_n, c_n, length, height, x_spacing, y_spacing, algorithm_CF, algorithm_H):

        H = CT.homography_matrix_estimation(algorithm_H, vectors, well_names)

        self.coordinate_frame_algorithm = algorithm_CF
        self.homography_matrix_algorithm = algorithm_H
        self.r_n = r_n
        self.c_n = c_n
        self.all_well_dicts = self.list_well_state_dict_2dict(well_names, vectors)
        self.length = length
        self.height = height
        self.xspacing = x_spacing
        self.yspacing = y_spacing
        self.corners_coords = [vectors[x] for x in [0, c_n - 1, (r_n - 1) + (c_n - 1),
                                                    (r_n - 1) + (2 * (c_n - 1))]]  # Top left, Top right, Bottom left
        self.homography_matrix = H

        logging.log(level=20, msg="Well plate matrix dimension: rows: {}, columns: {}".format(r_n, c_n))
        logging.log(level=20, msg="Well plate corner coordinates: {}".format(self.corners_coords))
        logging.log(level=20, msg="Well plate dimension: length - {}, height - {}".format(length, height))
        logging.log(level=20, msg="Computed well spacing: x:spacing = {} and y_spacing = {}".format(
            x_spacing, y_spacing))

    def predict_well_coords(self, c_n, r_n, algorithm="linear spacing", algorithm_H="non-linear"):

        topleft, bottomleft, topright, bottomright = self.get_corner_as_vectors()

        if algorithm == "linear spacing":
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
            algorithm = "linear correction matrix"

        # Save all variables as parameters
        self.set_parameters(well_names, vectors,
                            r_n, c_n, length, height, x_spacing, y_spacing,
                            algorithm_CF=algorithm, algorithm_H=algorithm_H)

        return vectors, well_names, length, height, x_spacing

    def list_well_state_dict_2dict(self, well_names, vectors):

        all_well_dicts = {well_name: self.vector_2_state_dict(vector) for well_name, vector in zip(well_names,
                                                                                                   vectors)}
        return all_well_dicts

    def execute_template_coords(self, state_dict):

        # Configure drawer

        try:
            # Move stage to well
            # self.update_state(state_dict, analoguecontrol_bool=False)
            # Perform image acquisition of different Z positions
            # self.run_protocol()
            sleep(3)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("What happened here ", exc_info=True)

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


if __name__ == '__main__':
    import argparse
    import json

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

    ###Predict well cords from corners
    wellplate.predict_well_coords(args.columns, args.rows)

    print("After update: " + str(wellplate.__dict__))

    ###Save the attributes
    wellplate.save_attributes2json(partnumber="12345", manufacturer="Falcon")

    ###Test if wellplate can load attributes

    wellplate2 = WellPlate()

    wellplate2.load_attributes(name="384_falcon_wellplate.json")

    print("After loading attributes: " + str(wellplate2.__dict__))
