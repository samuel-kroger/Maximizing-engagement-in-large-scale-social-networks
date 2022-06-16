from datetime import datetime
from classes import *
import json
import os
import time
import classes


#user = 'samuel_kroger'
ext = "../data/"
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M")
filename = dt_string + '.csv'
filename = filename.strip()

f = open('data.json')
data = json.load(f)

for request in data['single']:
	print("starting: ",
		'\n filename: ', request['filename'],
		'\n model_type: ', request['model_type'],
		'\n k: ', request['k'],
		'\n b: ', request['b'],
		'\n r: ', request['r'])

	G = classes.read_graph(ext + request['filename'])

	start_time = time.time()
	instance = globals()[request['model_type']](filename, request['filename'][:-4], G, request['model_type'], request['k'], request['b'], request['r'], request['y_saturated'], request['additonal_facet_defining'], request['y_val_fix'], request['fractional_callback'], request['relax'])
	if request['warm_start']:
		#instance.remove_y_edges()
		instance.RCM_warm_start()
	'''
	if instance.model_type == "cut_model":
		#instance.warm_start_one()
		#instance.center_fixing_idea_recursive()
		#instance.dominated_fixing_idea()
		#instance.dominated_fixing_idea_power_graph()
		#instance.dominated_fixing_idea_power_graph_sam()
	'''

	instance.optimize()
	instance.print_model()

	end_time = time.time()

	instance.save_to_file(str(round(end_time - start_time, 2)))
