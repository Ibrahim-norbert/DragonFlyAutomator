import pickle
from xyzstage import get_output, update, FusionApi
import logging
import numpy as np
import os
import json

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
            return {x: y for x, y in
                    zip(self.path_options, self.current_output)}

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
            return state, z

    def move_z_axis(self, z_increment, state):
        if state["driftstabilisationactive"]["Value"] == "False":
            current = state["referencezposition"]["Value"]
            state["referencezposition"]["Value"] -= z_increment
            self.update_state(key="referencezposition", state_dict=state)
            logger.log(level=10, msg="Updated referencezposition from {} to {}".format(current,
                                                                                       state["referencezposition"][
                                                                                           "Value"]))
