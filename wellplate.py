import pickle
from xyz_stage import xyz_stage
import logging
import numpy as np
import os
from time import sleep
import matplotlib.pyplot as plt

# Configure logging
# ogging.basicConfig(filename=os.path.join(os.getcwd(), 'dragonfly_automator.log'), level=logging.DEBUG,
#                   format='%(asctime)s - %(levelname)s - %(message)s')
# Example: Log a message from another module
logger = logging.getLogger(__name__)
logger.info("This log message is from another module.")


class WellPlate(xyz_stage):
    def __init__(self, endpoint, model):
        super().__init__(endpoint)
        self.model = model
        self.well_plate_req_coords = {"Top right well": None, "Top left well": None,
                                      "Bottom left well": None}

    # def visualise_well_plate(self, all_well_dicts):
    #
    #     import matplotlib.pyplot as plt
    #
    #     fig = plt.figure(figsize=(5,7.5))
    #
    #     for name, coord in all_well_dicts.items():
    #         plt.scatter(*list(self.state_dict_2_vector(coord)))
    #
    #     fig.savefig(os.path.join(os.getcwd(), 'well_plate_visualisation.png'))

    def execute_template_coords(self, all_state_dicts):

        for state_dict in all_state_dicts:
            # Move stage to well
            self.update_state(state_dict, analoguecontrol_bool=False)

            # Perform image acquisition of different Z positions
            # self.run_protocol()

            sleep(3)

    def state_dict_2_vector(self, state_dict):
        logging.log(level=10, msg='Value key: {}, Path options: {},'
                                  'State dictionary: {}'.format(self.value_key, self.path_options, state_dict))
        return np.array(
            [state_dict[self.path_options[0]][self.value_key], state_dict[self.path_options[1]][self.value_key]])

    def vector_2_state_dict(self, vector):
        return {self.path_options[0]: {self.value_key: vector[0]}, self.path_options[1]: {self.value_key: vector[1]},
                self.path_options[-1]: {self.value_key: False}}

    def save_parameters(self, all_well_dicts,
                        r_n, c_n, length, height, x_spacing, y_spacing):

        logging.log(level=20, msg="All well plate coordinates: {}".format(all_well_dicts))
        logging.log(level=20, msg="Well plate dimension: length - {}, height - {}".format(length, height))
        logging.log(level=20, msg="Computed well spacing: x:spacing = {} and y_spacing = {}".format(
            x_spacing, y_spacing))

        self.wellplate_matrix = (r_n, c_n)
        self.all_well_dicts = all_well_dicts
        self.length = length
        self.height = height
        self.xspacing = x_spacing
        self.yspacing = y_spacing

        if self.model is not None:
            with open(self.model + ".pkl", 'wb') as outp:
                pickle.dump(self, outp, pickle.HIGHEST_PROTOCOL)

        # self.visualise_well_plate(all_well_dicts)
        return all_well_dicts

    def get_corner_as_vectors(self, specified_vectors):
        """

        @rtype: object
        """
        topleft = specified_vectors[-3].astype(float)
        bottomleft = specified_vectors[-2].astype(float)
        topright = specified_vectors[-4].astype(float)
        bottomright = specified_vectors[-1].astype(float)

        length = np.linalg.norm(topleft - topright)
        height = np.linalg.norm(topleft - bottomleft)

        logging.log(level=20, msg="Well plate dimension: state dict as vectors {}".format(specified_vectors))

        return topleft, bottomleft, topright, bottomright, length, height

    def compute_coords_with_linearcorrection(self, c_n, r_n):

        """correction matrix obtained from:
            https://scripts.iucr.org/cgi-bin/paper?S2053230X18016515"""

        # specified_vectors = [self.state_dict_2_vector(self.well_plate_req_coords["Top right well"]),
        #                      self.state_dict_2_vector(self.well_plate_req_coords["Top left well"]),
        #                      self.state_dict_2_vector(self.well_plate_req_coords["Bottom left well"]),
        #                      self.state_dict_2_vector(self.well_plate_req_coords["Bottom right well"])]

        specified_vectors = [self.state_dict_2_vector(self.well_plate_req_coords["Top right well"]),
                             self.state_dict_2_vector(self.well_plate_req_coords["Top left well"]),
                             self.state_dict_2_vector(self.well_plate_req_coords["Bottom left well"])]

        # Add bottom left well
        specified_vectors.append(np.array([specified_vectors[-3][0], specified_vectors[-1][1]]))

        topleft, bottomleft, topright, bottomright, length, height = self.get_corner_as_vectors(specified_vectors)

        # in the calculation below, the coordinates of each drop are first calculated based on tl and br.
        # Then the bl coordinate is used to make a secondary, correction as needed.
        tr = topright - topright # Treat as 0
        tl = topleft - topright
        bl = bottomleft - topright
        br = bottomright - topright

        logging.log(level=20, msg="Well plate coordinate frame after normalisation: {}".format((tr,tl,bl,br)))

        try:
            corx = tl / float(c_n - 1)
            cory = br / float(r_n - 1)

            # cor is the correction matrix to account for misalignment of the plate vs. translation directions in x,y,z
            cor = np.array(([corx[0], cory[0], 0],
                            [corx[1], cory[1], 0],
                            [0,0,0]))

            logging.log(level=20, msg="The correction matrix: {}".format(cor))

            blpred = np.dot(cor, np.array(((c_n - 1), (r_n - 1), 0)))  # predicted position of bl based on tl and br
            logging.log(level=20, msg="The bottom left well coordinate prediction: {}".format(blpred))

            fixit = (np.append(bl, 0) - blpred) / float((c_n - 1) * (r_n - 1))  # this is the correction based on bl
            logging.log(level=20, msg="The non linear prediction: {}".format(fixit))
            # x = numbers i.e. columns
            # y = letters i.e. rows
            vectors = sum(
                [[(np.dot(cor, np.array(np.array((c, r, 0)))) + fixit * (c * r)) + np.append(topright,0) for c in range(c_n)] for r in range(r_n)], [])

            logging.log(level=20, msg="The resulting vectors: {}".format(vectors))

            well_names = sum([[str(r) + " " + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

            all_well_dicts = {well_name: self.vector_2_state_dict(vector) for well_name, vector in zip(well_names,
                                                                                                       vectors)}
            x_spacing = np.abs(vectors[int(c_n / 2)][0] - vectors[int(c_n / 2) + 1][0])
            y_spacing = np.abs(vectors[c_n * int(r_n / 2)][1] - vectors[c_n * int(r_n / 2) + 1][1])

            return self.save_parameters(all_well_dicts, r_n, c_n, length, height, x_spacing, y_spacing)
        except Exception as e:
            print(f"An unexpected output error occurred: {e}")
            logging.exception("An unexpected output error occurred", exc_info=True)

    def compute_inspect_coords(self, c_n, r_n):

        # Template
        # self.get_384_well_plate_req_coords()  # Provides coords in vector format
        try:
            specified_vectors = [self.state_dict_2_vector(self.well_plate_req_coords["Top right well"]),
                                 self.state_dict_2_vector(self.well_plate_req_coords["Top left well"]),
                                 self.state_dict_2_vector(self.well_plate_req_coords["Bottom left well"])]

            # Add bottom left well
            specified_vectors.append(np.array([specified_vectors[-3][0], specified_vectors[-1][1]]))

            topleft, bottomleft, topright, bottomright, length, height = self.get_corner_as_vectors(specified_vectors)

            # There has to be regular spacing between cells
            x_coord, x_spacing = np.linspace(topright[0], topleft[0], c_n, retstep=True)
            y_coord, y_spacing = np.linspace(topright[1], bottomright[1], r_n, retstep=True)

            logging.log(level=20, msg="Well plate dimension: length - {}, height - {}".format(length, height))
            logging.log(level=20, msg="Computed well spacing: x:spacing = {} and y_spacing = {}".format(
                x_spacing, y_spacing))

            xv, yv = np.meshgrid(x_coord, y_coord)

            vectors = np.stack([xv, yv], axis=-1)  # rows,columns i.e. x,y,2

            vectors = vectors.reshape(r_n * c_n, 2)

            well_names = sum([[str(r) + " " + str(c + 1) for c in range(c_n)] for r in range(r_n)], [])

            all_well_dicts = {well_name: self.vector_2_state_dict(vector) for well_name, vector in zip(well_names,
                                                                                                       vectors)}
            return self.save_parameters(all_well_dicts, r_n, c_n, length, height, x_spacing, y_spacing)

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            logging.exception("State dict might be None", exc_info=True)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='train a phase registration model')
    parser.add_argument("--columns", type=int, required=False, help="Enter x coordinates for xyz stage")
    parser.add_argument("--rows", type=int, required=False, help="Enter y coordinates for xyz stage")
    parser.add_argument("--analoguecontrol", type=bool, default=False,
                        help="Enter boolean for analog control of xyz stage")
    parser.add_argument("--update", type=bool, default=False, help="Enter boolean for analog control of xyz stage")
    parser.add_argument("--endpoint", type=str, required=True, help="Enter API endpoint of xyz stage")

    args = parser.parse_args()

    instance_xyz_Stage = xyz_stage(args.endpoint)

    print("Before update: " + str(instance_xyz_Stage.__dict__))

    instance_xyz_Stage.get_well_plate_req_coords()

    columns, rows = args.columns, args.rows

    if columns is not None and rows is not None:
        all_state_dicts = instance_xyz_Stage.compute_wellplate_coords(columns, rows)

        wellplate_ = WellPlate(endpoint=args.endpoint)

        # wellplate_.visualise_wellplate(all_state_dicts)
