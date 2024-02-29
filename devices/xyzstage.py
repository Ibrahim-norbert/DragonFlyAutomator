import json
import logging
import os
import numpy as np
from RestAPI import fusionrest

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.".format(__name__))

#TODO need to remove the testers

def get_address(endpoint):
    try:
        return fusionrest.__make_address(endpoint)
    except Exception as e:
        print(f"An unexpected address error occurred: {e}")
        logging.exception("An unexpected address error occurred", exc_info=True)


def get_output(endpoint):
    try:
        return fusionrest.__get(endpoint)
    except Exception as e:
        print(f"An unexpected output error occurred: {e}")
        logging.exception("An unexpected output error occurred", exc_info=True)


def update(endpoint, obj):
    try:
        fusionrest.__put(endpoint, obj)
    except Exception as e:
        print(f"An unexpected update error occurred: {e}")
        logging.exception("An unexpected update error occurred", exc_info=True)


class FusionApi:
    def __init__(self):
        self.endpoint = "/v1"
        # self.current_output = get_output(self.endpoint)
        self.endpoint = "/v1"
        self.selected_path_option = "/v1"
        self.path_options = "/v1"
        self.address = None
        self.selected_key = None
        self.current_output = None

    def get_current_address(self):
        self.address = get_address(self.endpoint)
        return self.address

    def get_current_output(self):

        self.current_output = get_output(self.endpoint)

        return self.current_output

    def get_path_options(self):
        """
        If current path is not a dictionary or list, then we have reached the end path
        """
        if isinstance(self.current_output, dict):
            out = list(self.current_output.keys())
            self.path_options = out
            print(out)
            return out
        elif isinstance(self.current_output, list):
            out = self.current_output
            self.path_options = out
            print(out)
            return out
        else:
            print("Current output is neither dictionary no list, it is " + str(self.current_output))

    def go_to_next_path_output(self, path_option):

        out = self.get_path_options()

        assert out is not None, "No further path outputs"

        if not isinstance(path_option, str):
            path_option = str(path_option)

        assert path_option in out, "Please give correct spelling. "

        self.selected_path_option = path_option  # update

        self.endpoint += "/{}".format(self.selected_path_option)

        self.current_output = self.get_current_output()

        self.address = self.get_current_address()

        self.path_options = out

        return self.current_output

    def get_value(self, key):

        """Key are the keys of a dictionary or elements of a list"""
        assert isinstance(self.current_output, dict), ("Value cannot be retrieved."
                                                       " Current output is not a dictionary. Current output is " + str(
            self.current_output))
        self.selected_key = key
        return self.current_output[self.selected_key]

    def save_attributes2json(self, name):

        # Create a dictionary with attribute names and values
        attributes = {key: attr for key, attr in self.__dict__.items() if
                      not callable(attr)}

        # Create a dictionary with attribute names and values
        attributes = {key: attr.tolist() if isinstance(attr, np.ndarray) else attr for key,
        attr in attributes.items()}

        with open(os.path.join(os.getcwd(), "models", '{}.json'.format(name)), 'w') as f:
            json.dump(attributes, f)

    def load_attributes(self, name):
        f = open(os.path.join(os.getcwd(), "models", '{}'.format(name)))
        attributes = json.load(f)
        self.__dict__.update(attributes)


class XYZStage(FusionApi):
    """From what I have seen, the XYZStage path outputs a list."""

    def __init__(self, endpoint="v1"):
        super().__init__()  # inherits

        self.endpoint = self.endpoint + "/{}/{}".format("devices", "xyz-stage")

        # self.current_output = get_output(self.endpoint)

        # Opening JSON file

        f = open(os.path.join(os.getcwd(), r"endpoint_outputs", "xyz-stage.json"))

        self.current_output = json.load(f)

        self.path_options = [x["Name"] for x in self.current_output]

        self.x_dict = self.current_output[0]
        self.y_dict = self.current_output[1]
        self.autoregulation_dict = self.current_output[2]
        self.coords_features = list(self.current_output[0].keys())
        self.value_key = self.coords_features[-3]
        self.min_key = self.coords_features[-2]
        self.max_key = self.coords_features[-1]

        self.xmin, self.xmax = float(self.x_dict[self.min_key].replace(",", ".")), float(
            self.x_dict[self.max_key].replace(",", "."))
        self.ymin, self.ymax = float(self.y_dict[self.min_key].replace(",", ".")), float(
            self.y_dict[self.max_key].replace(",", "."))

        self.selected_path_option = endpoint.split("/")[-1]
        self.selected_key = None

    def get_state(self, test_key=None):
        # return {x: get_output(endpoint=self.endpoint + "/{}".format(x)) for x in
        #         self.path_options}

        # [[-48, 33.1], [-48, -38.9], [60, 33.1], [60, -38.9], [-48, 33.1]]

        # Opening JSON file
        file = os.path.join(os.getcwd(), r"endpoint_outputs", "{}xposition.json".format(test_key.replace(" well", "_")))
        f = open(file)
        x_ = json.load(f)
        # Opening JSON file
        file = os.path.join(os.getcwd(), r"endpoint_outputs", "{}yposition.json".format(test_key.replace(" well", "_")))
        f = open(file)
        y = json.load(f)
        return {x: [x_, y, None][id] for id, x in enumerate(self.path_options)}

    def enter_coords(self, x, y, state_dict):

        if self.xmax >= x >= self.xmin and self.ymax >= y >= self.ymin:
            state_dict[self.path_options[0]][self.value_key] = float(x)
            state_dict[self.path_options[1]][self.value_key] = float(y)
            return state_dict

    def update_state(self, state_dict, analoguecontrol_bool=False):

        if state_dict is not None:
            state_dict[self.path_options[-1]][self.value_key] = analoguecontrol_bool

            update(self.endpoint + "/{}".format(self.path_options[0]), state_dict[self.path_options[0]])
            update(self.endpoint + "/{}".format(self.path_options[1]), state_dict[self.path_options[1]])
            update(self.endpoint + "/{}".format(self.path_options[2]), state_dict[self.path_options[2]])

            return state_dict


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='train a phase registration model')
    parser.add_argument("--x", type=int, required=False, help="Enter x coordinates for xyz stage")
    parser.add_argument("--y", type=int, required=False, help="Enter y coordinates for xyz stage")
    parser.add_argument("--analoguecontrol", type=bool, default=False,
                        help="Enter boolean for analog control of xyz stage")
    parser.add_argument("--update", type=bool, default=False, help="Enter boolean for analog control of xyz stage")
    parser.add_argument("--endpoint", type=str, required=True, help="Enter API endpoint of xyz stage")

    args = parser.parse_args()

    instance_xyz_Stage = XYZStage(args.endpoint)

    print("Before update: " + str(instance_xyz_Stage.__dict__))

    x, y = args.x, args.y

    if x is not None and y is not None:
        state_dict = instance_xyz_Stage.enter_coords(x, y, instance_xyz_Stage.get_state())
        if args.update is True:
            instance_xyz_Stage.update_state(state_dict=state_dict, analoguecontrol_bool=args.analoguecontrol)
