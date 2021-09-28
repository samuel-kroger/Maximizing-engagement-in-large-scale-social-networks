import gurobipy as gp
import networkx as nx
from datetime import datetime
import matplotlib.pyplot

import json
import os
#import read
import time
import csv
import classes
import misc
import test



user = 'samuel_kroger'
ext = "../data/"
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = user + '_' + dt_string + '.csv'
filename = filename.strip()


spacing = 8*', '

with open('../results/' + filename, 'w') as doc:
	doc.write('instances, , , , , , Base Model' + spacing +  'Reduced Model' + spacing + 'Reduced Model with warm start'+ spacing +  'Reduced Model with warm start and y_edges' + spacing + 'Reduced Model y_saturated' + spacing + 'Reduced Model Conflict Warm Start' + '\n' +
	          '#name, k, b, #nodes, #edges, #k-cores,' + 6*' #vars, #edges_removed, time_to_remove_edges, #y-sat_nodes, time_to_find_y_sat, UB, LB, time,' + '\n')


f = open('data.json')
data = json.load(f)


for request in data['strong']:
	print("starting: ",
	      '\n filename: ', filename,
	      '\n model_type: ', request['model_type'],
	      '\n k: ', request['k'],
	      '\n b: ', request['b'],
	      '\n r: ', request['r'])
	with open('../results/' + filename, 'a') as doc:

		G = nx.readwrite.adjlist.read_adjlist(ext + request['filename'], nodetype = int)
		G = nx.relabel.convert_node_labels_to_integers(G, first_label = 0)

		results = []


		start_time = time.time()
		if request['model_type'] == 'naive':
			instance = classes.base_model(filename, G, gp.Model(), request['model_type'], request['k'], request['b'], request['r'])
		if request['model_type'] == 'strong':
			instance = classes.reduced_model(filename, G, gp.Model(), request['model_type'], request['k'], request['b'], request['r'])
		if request['model_type'] == 'vermyev':
			instance = classes.vermyev_model(filename, G, gp.Model(), request['model_type'], request['k'], request['b'], request['r'])
		if request['model_type'] == 'cut_model':
			instance = classes.cut_model(filename, G, gp.Model(), request['model_type'], request['k'], request['b'], request['r'])
		if request['model_type'] == 'extended_cut_model':
			instance = classes.extended_cut_model(filename, G, gp.Model(), request['model_type'], request['k'], request['b'], request['r'])



		if request['y_saturated']:
			instance.y_saturated()
		if request['remove_y_edges']:
			instance.remove_y_edges()
		if request['warm_start']:
			instance.warm_start()
		if request['core_fix']:
			instance.fix_k_core()

		#instance.set_up_model()

		instance.optimize()

		instance_results = instance.output_results()
		end_time = time.time()
		time_elapsed = end_time - start_time
		instance_results.append(time_elapsed)
		results.append(instance_results)

		instance.print_model()

		instance.free_model()

		string = ''
		for result in results:
			string += misc.csv_print(result[0], result[1], result[2], result[3], result[4], result[5], result[6], result[8]) + ','
		k_core_num = instance_results[7]
		doc.write(request['filename'][:-4] + ',' +  str(request['k']) + ',' + str(request['b']) + ', ' + str(len(G.nodes)) + ',' + str(len(G.edges)) +',' + str(k_core_num) + ',' + string + '\n')
