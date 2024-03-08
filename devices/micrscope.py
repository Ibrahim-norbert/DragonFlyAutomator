import sys

from devices.xyzstage import get_output, update, FusionApi
import logging
import numpy as np
import os
import json
from time import sleep

logger = logging.getLogger(__name__)
logger.info("This log message is from {}.py".format(__name__))


class Microscope(FusionApi):
    def __init__(self):
        super().__init__()  # inherits

        self.endpoint = self.endpoint + "/{}/{}".format("devices", "microscope")

        if self.test is False:
            self.current_output = get_output(self.endpoint)
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", os.path.basename(self.endpoint) + ".json"))
            self.current_output = json.load(f)

        self.path_options = [x["Name"] for x in self.current_output if x is not None]
        logging.log(level=10, msg="The next path destinations of microscope: {}".format(self.path_options))

    def get_state(self):
        if self.test is False:
            return {x: get_output(endpoint=self.endpoint + "/{}".format(x)) for x in
                    self.path_options}
        else:
            f = open(os.path.join(os.getcwd(), "endpoint_outputs", os.path.basename(self.endpoint) + ".json"))
            return {x: y for x, y in
                    zip(self.path_options, json.load(f))}

    def update_state(self, key, state_dict):
        if self.test is False:
            if state_dict is not None:
                update(self.endpoint + "/{}".format(key), state_dict[key])
        else:
            pass

    def get_current_z(self):
        if self.test is False:
            state = self.get_state()
            z = state["referencezposition"]["Value"]
            return state, z
        else:
            state = self.get_state()
            z = eval(state["referencezposition"]["Value"].replace(",", "."))
            state["referencezposition"]["Value"] = z
            return state, z

    def move_z_axis(self, z_increment, state):
        if state["driftstabilisationactive"]["Value"] == "False":
            current = state["referencezposition"]["Value"]
            state["referencezposition"]["Value"] -= z_increment
            self.update_state(key="referencezposition", state_dict=state)
            logger.log(level=10, msg="Updated referencezposition from {} to {}".format(current,
                                                                                       state["referencezposition"][
                                                                                           "Value"]))
            # We wait until the microscope has moved position to target Z.
            count = 0
            while state["referencezposition"]["Value"] != self.get_current_z()[-1]:
                logger.log(level=20, msg="Microscope is moving to new position")
                if count == 10:
                    sys.exit("Microscope failed to reach z position. Current {} and target {}. Please look at"
                             "log file to find any errors".format(self.get_current_z()[-1],
                                                                  state["referencezposition"]["Value"]))
                count += 1
                sleep(3)

            return state["referencezposition"]["Value"]
