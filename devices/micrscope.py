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
        self.current_output = get_output(self.endpoint)
        print(self.current_output[0]["Name"])
        self.path_options = [x["Name"] for x in self.current_output if x is not None]
        logging.log(level=10, msg="The next path destinations of microscope: {}".format(self.path_options))

    def get_state(self):
        return {x: get_output(endpoint=self.endpoint + "/{}".format(x)) for x in
                self.path_options}

    def update_state(self, key, state_dict):

        if state_dict is not None:
            update(self.endpoint + "/{}".format(key), state_dict[key])

    def get_current_z(self):
        state = self.get_state()
        z = state["referencezposition"]["Value"]
        return state, z

    def move_z_axis(self, z_increment, state):
        if state["driftstabilisationactive"]["Value"] == "False":
            current = state["referencezposition"]["Value"]
            state["referencezposition"]["Value"] -= z_increment
            self.update_state(key="referencezposition", state_dict=state)
            logger.log(level=10, msg="Updated referencezposition from {} to {}".format(current, state["referencezposition"]["Value"]))





