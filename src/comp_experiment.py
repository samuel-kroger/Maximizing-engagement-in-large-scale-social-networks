from datetime import datetime
from classes import *
import json
import os
import time
import classes

ext = "../data/"
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M")
filename = dt_string + '.csv'
filename = filename.strip()

f = open('data.json')
data = json.load(f)

for request in data['table_2']:
	print("starting: ",
		'\n filename: ', request['filename'],
		'\n model_type: ', request['model_type'],
		'\n k: ', request['k'],
		'\n b: ', request['b'],
		'\n r: ', request['r'])

	G = classes.read_graph(ext + request['filename'])

	start_time = time.time()
	instance = globals()[request['model_type']](filename, request['filename'][:-4], G, request['model_type'], request['k'], request['b'], request['r'], request['relax'], request['warm_start'], request['prop_8'], request['prop_9'], request['prop_10'], request['prop_11'])
	if request['warm_start'] == "RCM":
		instance.RCM_warm_start()
	if request['warm_start'] == "OLAK":
		instance.OLAK_warm_start()

	instance.optimize()
	#instance.print_model()
	end_time = time.time()

	instance.save_to_file(str(round(end_time - start_time, 2)))
	instance.save_to_file_table_2(str(round(end_time - start_time, 2)))
