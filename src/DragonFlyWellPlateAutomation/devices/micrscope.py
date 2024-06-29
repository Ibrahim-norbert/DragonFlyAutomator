import json
import logging
import os
from time import sleep

from DragonFlyWellPlateAutomation.devices.xyzstage import get_output, update, FusionApi

logger = logging.getLogger("RestAPI.fusionrest")
logger.info("This log message is from {}.py".format(__name__))


class Microscope(FusionApi):
    def __init__(self):
        super().__init__()  # inherits

        self.endpoint = self.endpoint + "/{}/{}".format("devices", "microscope")

        if self.test is False:
            self.current_output = get_output(self.endpoint)
        else:
            f = open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "endpoint_outputs", os.path.basename(self.endpoint) + ".json"))
            self.current_output = json.load(f)

        self.path_options = [x["Name"] for x in self.current_output if x is not None]
        logger.log(level=10, msg="The next path destinations of microscope: {}".format(self.path_options))

        # Used only in test phase
        self.test_https = {x: {"Value": y["Value"]}  for x, y in
                           zip(self.path_options, self.current_output)}

        self.starting_z_height = self.get_current_z()[-1]

    def get_state(self):
        if self.test is False:
            return {x: get_output(endpoint=self.endpoint + "/{}".format(x)) for x in
                    self.path_options}
        else:
            # Make copy
            return {x: self.test_https[x] for x in self.path_options}

    def update_state(self, key, state_dict):
        logger.log(level=20, msg="Updating Z position: {}".format(state_dict[key]["Value"]))
        if self.test is False:
            if state_dict is not None:
                update(self.endpoint + "/{}".format(key), state_dict[key])
        else:
            if not isinstance(state_dict[key]["Value"], str):
                state_dict[key]["Value"] = str(state_dict[key]["Value"])
            self.test_https["referencezposition"]["Value"] = state_dict[key]["Value"].replace(".", ",")




    def get_current_z(self):
        state = self.get_state()
        z = state["referencezposition"]["Value"]

        if isinstance(z, str):
            if "," in z:
                z = z.replace(",",".")
            z = eval(z)

        state["referencezposition"]["Value"] = z
        logger.log(level=20, msg="Current Z: {}".format(z))
        return state, z

    def changezvalue(self, state, z_increment, new_z_height):

        current = state["referencezposition"]["Value"]

        if new_z_height is None:
            increment = z_increment["Value"]
            if z_increment["up"] == True:
                state["referencezposition"]["Value"] += increment
            else:
                state["referencezposition"]["Value"] -= increment
        elif new_z_height is not None:
            state["referencezposition"]["Value"] = new_z_height


        if self.test is False:
            state["referencezposition"]["Value"] = round(state["referencezposition"]["Value"], 3)
        else:
            state["referencezposition"]["Value"] = str(round(state["referencezposition"]["Value"], 3))


        return state, current

    def updatezposition(self, state, current):

        logger.log(level=20,
                   msg="Updated referencezposition from {} to {}".format(current, state["referencezposition"]["Value"]))

        self.update_state(key="referencezposition", state_dict=state)

        sleep(10)

    def move_z_axis(self, z_increment={"up": True, "Value": 5}, new_z_height=None):

        logger.log(level=20, msg="Moving z axis")

        state, z = self.get_current_z()

        state, current = self.changezvalue(state, z_increment, new_z_height)

        self.updatezposition(state, current)

        return state["referencezposition"]["Value"]

    def return2start_z(self):
        logger.log(level=20, msg="Return z axis to starting position: {}".format(self.starting_z_height))
        self.move_z_axis(new_z_height=self.starting_z_height)




