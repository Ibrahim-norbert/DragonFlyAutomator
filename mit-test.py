#!/usr/bin/env python3

print("initialising")

import fusionrest
from time import sleep
import os
import logging

logging.basicConfig(filename=os.path.join(os.getcwd(), 'dragonfly_automator.log'), level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
def wait_for_input_trigger():
	# insert your code here
	print("(pretending to wait for input trigger)")
	sleep(2)

def send_output_trigger():
	# insert your code here
	print("(pretending to send output trigger)")
	sleep(3)


def procedure(protocol1_name, protocol2_name, num_repeats):
	for i in range(1, num_repeats+1):
		print("==== start loop #%d ====" % i)

		wait_for_input_trigger()

		print("== run %s ==" % protocol1_name)
		fusionrest.run_protocol_completely(protocol1_name)

		send_output_trigger()

		print("== run %s ==" % protocol2_name)
		fusionrest.run_protocol_completely(protocol2_name)

		send_output_trigger()


if __name__ == '__main__':
	try:
		procedure("Protocol A", "Protocol B", 3)
		print("\nsuccess")
	except Exception as ex:
		print(ex)
