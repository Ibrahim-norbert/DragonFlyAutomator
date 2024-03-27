import copy
import json
import logging
import os
import sys
from time import sleep

from .xyzstage import get_output, update, FusionApi

logger = logging.getLogger("DragonFlyWellPlateAutomation.RestAPI.fusionrest")
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
        logger.log(level=10, msg="The next path destinations of microscope: {}".format(self.path_options))

        # Used only in test phase
        self.test_state = {x: {"Value": y["Value"]} for x, y in
                           zip(self.path_options, self.current_output)}

        self.starting_z_height = self.get_current_z()[-1]

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
            sleep(10)
            self.test_state["referencezposition"]["Value"] = str(state_dict["referencezposition"]["Value"]).replace(".",
                                                                                                                    ",")

    def get_current_z(self):
        state = self.get_state()
        z = eval(state["referencezposition"]["Value"].replace(",", "."))
        state["referencezposition"]["Value"] = z
        logger.log(level=20, msg="Current Z: {}".format(z))
        return state, z

    def move_z_axis(self, z_increment={"up": True, "Value": 5}, new_z_height=None):
        logger.log(level=20, msg="Moving z axis")

        state, z = self.get_current_z()

        if state["driftstabilisationactive"]["Value"] == "False":
            current = state["referencezposition"]["Value"]
            if new_z_height is None:
                increment = z_increment["Value"]
                if z_increment["up"] == True:
                    state["referencezposition"]["Value"] += increment
                else:
                    state["referencezposition"]["Value"] -= increment
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

    def return2start_z(self):
        self.move_z_axis(new_z_height=self.starting_z_height)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Testing microscope stage for movement of z stage')
    parser.add_argument("--z_height", type=float, required=True, help="Enter the z height")

    microscope = Microscope()

    microscope.test = True

    args = parser.parse_args()

    # Get state
    state = microscope.get_state()
    logger.log(level=20, msg="Get state")

    # Update state
    microscope.update_state("referencezposition", state_dict=state)
    logger.log(level=20, msg="Update z position")

    # Get current z height
    z = microscope.get_current_z()
    logger.log(level=20, msg="Current z height")

    # Move stage to new z height
    microscope.move_z_axis(new_z_height=args.z_height)
    logger.log(level=20, msg="Move z height from {} to {}".format(z, microscope.get_current_z()))


if __name__ == '__main__':
    main()
