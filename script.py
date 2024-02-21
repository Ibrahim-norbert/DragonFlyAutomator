import json
import logging
import os
import fusionrest
import numpy as np
from time import sleep
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(filename=os.path.join(os.getcwd(),'endpoints.log'), level=20,
					format='%(asctime)s - %(levelname)s - %(message)s')

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


def update(endpoint,obj):
	try:
		fusionrest.__put(endpoint, obj)
	except Exception as e:
		print(f"An unexpected update error occurred: {e}")
		logging.exception("An unexpected update error occurred", exc_info=True)




class fusion_api:
	def __init__(self):
		self.endpoint = "/v1"
		#self.current_output = get_output(self.endpoint)
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
													   " Current output is not a dictionary. Current output is " + str(self.current_output))
		self.selected_key = key
		return self.current_output[self.selected_key]


class xyz_stage(fusion_api):

	"""From what I have seen, the xyz_stage path outputs a list."""

	def __init__(self, endpoint):
		super().__init__() #inherits

		self.well_plate_req_coords = {"A1": None, "P1": None, "A24": None, "P24": None, "H12": None}
		self.endpoint = self.endpoint + "/{}/{}".format("devices","xyz-stage")



		#self.current_output = get_output(self.endpoint)

		# Opening JSON file
		f = open(r"C:\ibrahim_programme\Dragonfly_package\384_wellplate_automation\endpoint_outputs\xyz-stage.json")

		self.current_output = json.load(f)

		self.path_options = [x["Name"] for x in self.current_output]

		self.x_dict = self.current_output[0]
		self.y_dict = self.current_output[1]
		self.autoregulation_dict = self.current_output[2]
		self.coords_features = list(self.current_output[0].keys())
		self.value_key = self.coords_features[-3]
		self.min_key = self.coords_features[-2]
		self.max_key = self.coords_features[-1]


		self.xmin, self.xmax =  float(self.x_dict[self.min_key].replace(",", ".")), float(self.x_dict[self.max_key].replace(",", "."))
		self.ymin, self.ymax = float(self.y_dict[self.min_key].replace(",", ".")), float(self.y_dict[self.max_key].replace(",", "."))

		self.selected_path_option = endpoint.split("/")[-1]
		self.selected_key = None

	def get_state(self):
		return {x: get_output(endpoint=self.endpoint + "/{}".format(x)) for x in
				self.path_options}

	def enter_coords(self,x,y, state_dict):


		if x <= self.xmax and x >= self.xmin and y <= self.ymax and y >= self.ymin:
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

	def get_well_plate_req_coords(self):

		exit_ = False
		vectors = [[-48,33.1],[-48,-38.9],[60,33.1],[60,-38.9], [-48,33.1]]

		while exit_ == False:
			count = 0
			for key in self.well_plate_req_coords.keys():

				#print("Is this well " + key + " yes or no (or type exit for shutdown)?")
				#answer = str(input()).lower()
				#logging.log(level=20, msg="Well plate set coordinate answer: " + answer)
				answer = "yes"
				if answer == "yes":

					self.well_plate_req_coords[key] = self.vector_2_state_dict( vectors[count]) #self.get_state()
					count+=1
					#self.well_plate_req_coords[key] = self.get_state()
					logging.log(level=20, msg="Well: " + key + " - " + str(self.well_plate_req_coords[key]))
				# well_plate_req_coords[key] = np.array([state_dict[self.path_options[0]][self.value_key], state_dict[self.path_options[1]][self.value_key]])

				# self.well_plate_req_coords[key] = ("fay",
				#							  "beby")
				elif answer == "exit":
					exit_ = True
					break
				else:
					print(" ")
					print(" ")
					print("Please set all well coordinates again")
					print(" ")
					print(" ")
					sleep(1)
					break

				sleep(1)

			if exit_ is False:
				print("Are the coordinates given below correct, yes or no ?")
				print(self.well_plate_req_coords)
				answer = str(input()).lower()
				logging.log(level=20, msg="Confirm all selected coordinates answer: " + answer)
				logging.log(level=20, msg="Final coordinates: " + str(self.well_plate_req_coords))
				if answer == "yes":
					exit_ = True
				else:
					print("Please set all well coordinates again")

	def state_dict_2_vector(self, state_dict):
		return np.array(
			[state_dict[self.path_options[0]][self.value_key], state_dict[self.path_options[1]][self.value_key]])

	def vector_2_state_dict(self, vector):
		return {self.path_options[0]: {self.value_key: vector[0]}, self.path_options[1]: {self.value_key: vector[1]}}

	def compute_wellplate_coords(self, c_n, r_n):

		# Template
		#self.get_384_well_plate_req_coords()  # Provides coords in vector format

		specified_vectors = [self.state_dict_2_vector(state_dict) for state_dict in self.well_plate_req_coords.values()]

		length = np.linalg.norm(specified_vectors[0] - specified_vectors[2])
		height = np.linalg.norm(specified_vectors[0] - specified_vectors[1])

		# There has to be regular spacing between cells
		x_coord, x_spacing = np.linspace(specified_vectors[0][0], specified_vectors[2][0], c_n, retstep=True)
		y_coord, y_spacing = np.linspace(specified_vectors[0][1], specified_vectors[1][1], r_n, retstep=True)

		logging.log(level=20, msg="Well plate dimension: length - {}, height - {}".format(length, height))
		logging.log(level=20, msg="Computed well spacing: x:spacing = {} and y_spacing = {}".format(
			x_spacing, y_spacing))

		xv,yv = np.meshgrid(x_coord, y_coord)

		vectors = np.stack([xv, yv], axis=-1) #rows,columns i.e. x,y,2

		vectors = vectors.reshape(r_n*c_n,2)

		well_names = sum([[r.upper() + " " + str(c+1) for c in range(c_n) ]  for r in "abcdefghijklmnopqrstuvwxyz"[:r_n]],[])

		all_well_dicts = {well_name: self.vector_2_state_dict(vector)  for well_name,vector in zip(well_names,vectors)}

		logging.log(level=20, msg="All well plate coordinates: {}".format(all_well_dicts))

		self.wellplate_matrix = (r_n,c_n)
		self.all_well_dicts = all_well_dicts
		self.length = length
		self.height = height
		self.xspacing = x_spacing
		self.xspacing = y_spacing

		return all_well_dicts







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

		#if args.update is True:

		#	instance_xyz_Stage.execute_wellplate_coords(all_state_dicts)
















