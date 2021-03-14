import gurobipy as gp
import networkx as nx
from datetime import datetime
import matplotlib.pyplot

import os
#import read
import time
import csv
import classes
import misc

user = 'samuel_kroger'
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = user + '_' + dt_string
filename = filename.strip()

ext = "../data/"

anchored = True
radius_bounded = False



#options 	'no_heur', 'brute_force', 'eccentricity'
heuristic_status = 'no_heur'
#options 	'no_conn', ''flow', 'vermyev'
connectivity = 'no_conn'

r = 0



user = 'samuel_kroger'
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = user + '_' + dt_string + '.csv'
filename = filename.strip()




with open('../results/' + filename + '.csv', 'w') as doc:
	doc.write('''instances, , , ,Base Model, , , ,Base Model with warm start , , , , Reduced Model , , , , Reduced Model with warm start\n
	             #name, #nodes, #edges, #k-cores, #vars, LB, UB, time, #vars, LB, UB, time,#vars, LB, UB, time, #vars, LB, UB, time, #vars, LB, UB, time, \n''')

for file in os.listdir(ext):
	with open('../results/' + filename + '.csv', 'a') as doc:
		if file[-4:] == '.txt':

			G = nx.readwrite.adjlist.read_adjlist(ext + file, nodetype = int)

			for k in range(2,3):
				for b in range(2, 3):
					results = []

					start_time = time.time()
					instance = classes.base_model(filename, G, gp.Model(), k, b, r, radius_bounded, connectivity)
					instance.set_up_model()
					#instance.relaxation()
					instance.optimize()
					instance_results = instance.output_results()
					end_time = time.time()
					time_elapsed = end_time - start_time
					instance_results.append(time_elapsed)
					results.append(instance_results)





					'''
					start_time = time.time()
					instance = classes.base_model(filename, G, gp.Model(), k, b, r, radius_bounded, connectivity)
					instance.remove_y_edges()
					instance.warm_start()
					instance.set_up_model()
					instance.optimize()
					instance_results = instance.output_results()
					end_time = time.time()
					time_elapsed = end_time - start_time
					instance_results.append(time_elapsed)
					results.append(instance_results)

					start_time = time.time()
					instance = classes.base_model(filename, G, gp.Model(), k, b, r, radius_bounded, connectivity)
					instance.y_saturated()
					instance.set_up_model()
					instance.optimize()
					instance_results = instance.output_results()
					end_time = time.time()
					time_elapsed = end_time - start_time
					instance_results.append(time_elapsed)
					results.append(instance_results)

					start_time = time.time()
					instance = classes.base_model(filename, G, gp.Model(), k, b, r, radius_bounded, connectivity)
					instance.warm_start()
					instance.set_up_model()
					instance.optimize()
					instance_results = instance.output_results()
					end_time = time.time()
					time_elapsed = end_time - start_time
					instance_results.append(time_elapsed)
					results.append(instance_results)

					start_time = time.time()
					instance = classes.reduced_model(filename, G, gp.Model(), k, b, r, radius_bounded, connectivity)
					instance.set_up_model()
					instance.optimize()
					instance_results = instance.output_results()
					end_time = time.time()
					time_elapsed = end_time - start_time
					instance_results.append(time_elapsed)
					results.append(instance_results)
					'''




					string = ''
					for result in results:
						string += misc.csv_print(result[0], result[1], result[2], result[4]) + ','
					k_core_num = instance_results[3]
					doc.write(file[:-4] + str(k)+ '-' + str(b) + ', ' + str(len(G.nodes)) + ',' + str(len(G.edges)) +',' + str(k_core_num) + ',' + string + '\n')
