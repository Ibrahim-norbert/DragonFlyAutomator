import pickle
from script import xyz_stage
import logging
import numpy as np
import os
from script import fusion_api
import json

#logging.basicConfig(filename=os.path.join(os.getcwd(), 'dragonfly_automator.log'), level=logging.DEBUG,
 #                   format='%(asctime)s - %(levelname)s - %(message)s')


class EMCCD2(fusion_api):
    def __init__(self):
        super().__init__()  # inherits

        self.endpoint = self.endpoint + "/{}/{}".format("devices", "ixon-emccd-2")
        f = open(os.path.join(os.getcwd(), r"endpoint_outputs", "ixon-emccd-2.json"))

        self.current_output = json.load(f)

        print(self.current_output[0]["Name"])
        self.path_options = [x["Name"] for x in self.current_output if x is not None]

        logging.log(level=10, msg="The next path destinations of ixon-emccd-2: {}".format(self.path_options))


EMCCD2()
