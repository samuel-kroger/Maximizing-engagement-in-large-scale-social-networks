import gurobipy as gp
from gurobipy import GRB
import networkx as nx
from networkx.algorithms import approximation
from matplotlib import pylab as pl
from datetime import datetime
import matplotlib.pyplot as plt
import read

import os
import read
import time
import main
import csv


user = 'samuel_kroger'
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = user + '_' + dt_string + '.csv'
filename = filename.strip()

ext = "../data/"

anchored = True
radius_bounded = False

#options 	'no_heur', 'brute_force', 'eccentricity'
heuristic_status = 'no_heur'
#options 	'no_conn', ''flow', 'vermyev'
connectivity = 'no_conn'

r = 0

with open('../results/' + filename, 'w') as doc:
	doc.write('''instances, , , ,Original Model, , , ,Reduced Model\n
	             #name, #nodes, #edges, #k-cores, #vars, LB, UB, time, #vars, LB, UB, time\n''')

with open('../results/' + filename, 'a') as doc:
	for file in os.listdir(ext):
		#if file[-4:] == '.txt':
		if file[-6:] == '.graph':
			print('starting ' + file)
			for k in range(2,6):
				for b in range(0,5):

					#G = nx.readwrite.adjlist.read_adjlist(ext + file, nodetype = int)
					G = read.imp_dimacs(ext + file)

					time1 = time.time()
					og_vars, og_LB, og_UB = main.original_model(G, anchored, radius_bounded, heuristic_status, k, b, r, connectivity, 0)
					time2 = time.time()
					rm_vars, rm_LB, rm_UB, k_core_num = main.reduced_model(G, anchored, radius_bounded, heuristic_status, k, b, r, connectivity, 0)
					time3 = time.time()

					og_time = time2 - time1
					rm_time = time3 - time2


					doc.write(file[:-4] + str(k)+ '-' + str(b) + ', ' + str(len(G.nodes)) + ',' + str(len(G.edges)) +',' + str(k_core_num) + ',' + str(og_vars) + ','+ str(og_LB) + ',' + str(og_UB) + ',' + str(og_time) + ',' + str(rm_vars) + ',' + str(rm_LB) + ',' + str(rm_UB) + ',' + str(rm_time) + '\n')