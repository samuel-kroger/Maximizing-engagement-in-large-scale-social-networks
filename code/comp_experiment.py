import gurobipy as gp
import networkx as nx
from datetime import datetime
from classes import *
import matplotlib.pyplot

import json
import os
#import read
import time
import csv
import classes
import misc
import test



#user = 'samuel_kroger'
ext = "../data/"
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M")
filename = dt_string + '.csv'
filename = filename.strip()


spacing = 8*', '


f = open('data.json')
data = json.load(f)


for request in data['single']:
	print("starting: ",
	      '\n filename: ', filename,
	      '\n model_type: ', request['model_type'],
	      '\n k: ', request['k'],
	      '\n b: ', request['b'],
	      '\n r: ', request['r'])

	G = nx.readwrite.adjlist.read_adjlist(ext + request['filename'], nodetype = int)
	G = nx.relabel.convert_node_labels_to_integers(G, first_label = 0)

	start_time = time.time()
	#klass = 
	instance = globals()[request['model_type']](filename, request['filename'][:-4], G, request['model_type'], request['k'], request['b'], request['r'], request['y_saturated'])

	if request['remove_y_edges']:
		instance.remove_y_edges()
	if request['warm_start']:
		instance.warm_start()
	if request['core_fix']:
		instance.fix_k_core() 

	instance.optimize()
	end_time = time.time()

	instance.save_to_file(str(end_time - start_time))