import pickle

from script import xyz_stage
import logging
import numpy as np
import os
from time import sleep
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(filename=os.path.join(os.getcwd(), 'dragonfly_automator.log'), level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class wellplate(xyz_stage):
    def __init__(self, endpoint, well1, well2, well3, model):
        super().__init__(endpoint)
        self.model = model
        self.well_plate_req_coords = {well1: None, well2: None, well3: None}

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
            self.update_state(state_dict, analoguecontrol_bool=False)

    # def get_well_plate_req_coords(self):
    #
    #     exit_ = False
    #     vectors = [[-48, 33.1], [-48, -38.9], [60, 33.1], [60, -38.9], [-48, 33.1]]
    #
    #     while exit_ == False:
    #         count = 0
    #         for key in self.well_plate_req_coords.keys():
    #
    #             # print("Is this well " + key + " yes or no (or type exit for shutdown)?")
    #             # answer = str(input()).lower()
    #             # logging.log(level=20, msg="Well plate set coordinate answer: " + answer)
    #             answer = "yes"
    #             if answer == "yes":
    #
    #                 self.well_plate_req_coords[key] = self.vector_2_state_dict(vectors[count])  # self.get_state()
    #                 count += 1
    #                 # self.well_plate_req_coords[key] = self.get_state()
    #                 logging.log(level=20, msg="Well: " + key + " - " + str(self.well_plate_req_coords[key]))
    #             # well_plate_req_coords[key] = np.array([state_dict[self.path_options[0]][self.value_key], state_dict[self.path_options[1]][self.value_key]])
    #
    #             # self.well_plate_req_coords[key] = ("fay",
    #             #							  "beby")
    #             elif answer == "exit":
    #                 exit_ = True
    #                 break
    #             else:
    #                 print(" ")
    #                 print(" ")
    #                 print("Please set all well coordinates again")
    #                 print(" ")
    #                 print(" ")
    #                 sleep(1)
    #                 break
    #
    #             sleep(1)
    #
    #         if exit_ is False:
    #             print("Are the coordinates given below correct, yes or no ?")
    #             print(self.well_plate_req_coords)
    #             answer = str(input()).lower()
    #             logging.log(level=20, msg="Confirm all selected coordinates answer: " + answer)
    #             logging.log(level=20, msg="Final coordinates: " + str(self.well_plate_req_coords))
    #             if answer == "yes":
    #                 exit_ = True
    #             else:
    #                 print("Please set all well coordinates again")

    def state_dict_2_vector(self, state_dict):
        logging.log(level=10, msg='Value key: {}, Path options: {},'
                                  'State dictionary: {}'.format(self.value_key, self.path_options, state_dict))
        return np.array(
            [state_dict[self.path_options[0]][self.value_key], state_dict[self.path_options[1]][self.value_key]])

    def vector_2_state_dict(self, vector):
        return {self.path_options[0]: {self.value_key: vector[0]}, self.path_options[1]: {self.value_key: vector[1]}}

    def compute_template_coords(self, c_n, r_n):

        # Template
        # self.get_384_well_plate_req_coords()  # Provides coords in vector format
        try:
            specified_vectors = [self.state_dict_2_vector(self.well_plate_req_coords["Top right well"]),
                                 self.state_dict_2_vector(self.well_plate_req_coords["Top left well"]),
                                 self.state_dict_2_vector(self.well_plate_req_coords["Bottom left well"])]

            #Add bottom left well
            specified_vectors.append(np.array([specified_vectors[-3][0], specified_vectors[-1][1]]))


            logging.log(level=20, msg="Well plate dimension: state dict as vectors {}".format(specified_vectors))

            topleft = specified_vectors[-3].astype(float)
            bottomleft = specified_vectors[-2].astype(float)
            topright = specified_vectors[-4].astype(float)
            bottomright = specified_vectors[-1].astype(float)


            length = np.linalg.norm(topleft - topright)
            height = np.linalg.norm(topleft - bottomleft)

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

            logging.log(level=20, msg="All well plate coordinates: {}".format(all_well_dicts))

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

        wellplate_ = wellplate(endpoint=args.endpoint)

        # wellplate_.visualise_wellplate(all_state_dicts)
