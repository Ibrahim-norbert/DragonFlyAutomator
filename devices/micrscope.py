import sys
from devices.xyzstage import get_output, update, FusionApi
import logging
import copy
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

        # Get it once
        self.test_state = {x: {"Value": y["Value"]} for x, y in
                           zip(self.path_options, self.current_output)}

        self.current_z_height = self.get_current_z()

    def get_state(self):
        if self.test is False:
            return {x: get_output(endpoint=self.endpoint + "/{}".format(x)) for x in
                    self.path_options}
        else:
            # Make copy
            return copy.deepcopy(self.test_state)

    def update_state(self, key, state_dict):
        if self.test is False:
            if state_dict is not None:
                update(self.endpoint + "/{}".format(key), state_dict[key])
        else:
            self.test_state["referencezposition"]["Value"] = str(state_dict["referencezposition"]["Value"]).replace(".",
                                                                                                                    ",")

    def get_current_z(self):
        if self.test is False:
            state = self.get_state()
            z = eval(state["referencezposition"]["Value"].replace(",", "."))
            state["referencezposition"]["Value"] = z
            logger.log(level=20, msg="Current Z: {}".format(z))
            return state, z
        else:
            state = self.get_state()
            z = eval(state["referencezposition"]["Value"].replace(",", "."))
            state["referencezposition"]["Value"] = z
            logger.log(level=20, msg="Current Z: {}".format(z))
            return state, z

    def move_z_axis(self, z_increment=None, state=None, new_z_height=None):
        if state["driftstabilisationactive"]["Value"] == "False":
            current = state["referencezposition"]["Value"]
            if z_increment is not None:
                state["referencezposition"]["Value"] -= z_increment
            elif new_z_height is not None:
                state["referencezposition"]["Value"] = float(new_z_height)

            self.update_state(key="referencezposition", state_dict=state)
            logger.log(level=20, msg="Updated referencezposition from {} to {}".format(current,
                                                                                       state["referencezposition"][
                                                                                           "Value"]))
            # We wait until the microscope has moved position to target Z.
            count = 0
            while state["referencezposition"]["Value"] != self.get_current_z()[-1]:
                logger.log(level=20, msg="Microscope is moving to new position")
                if count == 10:
                    msg = ("Microscope failed to reach z position. Current {} and target {}. Please look at log file "
                           "to find any errors").format(self.get_current_z()[-1],
                                                        state["referencezposition"]["Value"])
                    logger.log(level=40, msg=msg)

                    sys.exit(msg)
                count += 1
                sleep(3)

            return state["referencezposition"]["Value"]
