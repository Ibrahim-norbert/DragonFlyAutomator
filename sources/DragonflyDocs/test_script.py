import requests
import os

host = "localhost"
port = 15120
version = 'v1'

def __make_address(endpoint):
	return "http://{}:{}/{}/{}".format(host, port, version, endpoint)



print(__make_address('devices'))


def __get(endpoint):
	response = requests.get(__make_address(endpoint))
	# print("debug: received text [[%s]]" % response.text)
	#make catch error statement to simply error
	return response.json()

json_dict = __get(endpoint='devices')

print('This endpoint leads to the following options: ' + str(json_dict.values()))  

def __put(endpoint, obj):
	body = json.dumps(obj)
	__put_plain(endpoint, body)

def __put_plain(endpoint, body):
	response = requests.put(__make_address(endpoint), data=body)
	print(response)


def set_xy_stage(x_1):

	endpoint = 'devices'
	json_dict = __get(endpoint)#dict with single list containing device names

	address = __make_address(endpoint=os.path.join(endpoint ,json_dict[endpoint.title()][1]))
	
	response = requests.get(address)

	xyz_stage_list = response.json() #single list of dicts
	
	x_dict = xyz_stage_list[0] #dict for x param

	keys,values = list(zip(*x_dict.items()))

	regex_expression = "([0-9]+,{1}[0-9]+)"

	x_0 = float(values[1].replace(",", ".")) #[float(x.replace(",", ".")) if regex.match(regex_expression,x) is not None else x for x in values]

	max_x = float(values[3].replace(",", "."))

	min_x = float(values[2].replace(",", "."))

	assert x_0 + x_1 < values[3] or  x_0 + x_1 > values[2], 'The value goes beyond the maximum or minimum allowed values of: ' + values[3] + ' and ' + values[2]
	
	print(x_0 + x_1)

	values[1] = x_0

	x_dict = dict(zip(keys,values)) #dict for x param

	#path = os.path.join(endpoint ,json_dict[endpoint.title()][1],values[0])

	__put(endpoint=path, x_dict)
















	
	

set_xy_stage(x=5)


