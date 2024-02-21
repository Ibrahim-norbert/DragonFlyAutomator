from script import xyz_stage
import logging
import numpy as np
import os


# Configure logging
logging.basicConfig(filename=os.path.join(os.getcwd(),'wellplate_estimation.log'), level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class wellplate(xyz_stage):
    def __init__(self, endpoint):
        super().__init__(endpoint)


    def visualise_wellplate(self, all_well_dicts):

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()


        for name, coord in all_well_dicts.items():
            plt.Circle(self.state_dict_2_vector(coord), transform = fig.transFigure, figure = fig)

        plt.show()
        fig.savefig('plotcircles.png')

    def execute_wellplate_coords(self, all_state_dicts):

        for state_dict in all_state_dicts:
            self.update_state(state_dict, analoguecontrol_bool=False)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='train a phase registration model')
    parser.add_argument("--columns", type=int, required=False, help="Enter x coordinates for xyz stage")
    parser.add_argument("--rows", type=int, required=False, help="Enter y coordinates for xyz stage")
    parser.add_argument("--analoguecontrol", type=bool, default=False, help="Enter boolean for analog control of xyz stage")
    parser.add_argument("--update", type=bool, default=False, help="Enter boolean for analog control of xyz stage")
    parser.add_argument("--endpoint",type=str, required=True, help="Enter API endpoint of xyz stage")


    args = parser.parse_args()


    instance_xyz_Stage = xyz_stage(args.endpoint)

    print("Before update: " + str(instance_xyz_Stage.__dict__))

    instance_xyz_Stage.get_well_plate_req_coords()

    columns,rows = args.columns, args.rows

    if columns is not None and rows is not None:

        all_state_dicts = instance_xyz_Stage.compute_wellplate_coords(columns, rows)

        wellplate_ = wellplate(endpoint=args.endpoint)

        wellplate_.visualise_wellplate(all_state_dicts)
