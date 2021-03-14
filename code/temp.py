import model
import os
from datetime import datetime
import networkx as nx
import time
import heuristic


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



for file in os.listdir(ext):
	with open('../results/' + filename, 'a') as doc:
		if file[-4:] == '.txt':
		#if file[-6:] == '.graph':
			print('starting ' + file)
			for k in range(1,5):
				for b in range(1,5):


					G = nx.readwrite.adjlist.read_adjlist(ext + file, nodetype = int)

					#G1 = heuristic.k_core(G, k)
					time1= time.time()
					G2 = nx.algorithms.core.k_core(G, k)
					time2 = time.time()
					G3 = heuristic.new_code(G, k)
					time3 = time.time()
					print('aah')
					print(time2-time1)
					print(time3-time2)
					print('aah')
					#print(len(G1.nodes()))
