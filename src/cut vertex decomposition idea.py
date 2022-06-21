import gurobipy as gp
import networkx as nx
from datetime import datetime
import matplotlib.pyplot

import heuristic
import json
import os
#import read
import time
import csv
import classes
import misc
import test

user = 'samuel_kroger'
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = user + '_' + dt_string
filename = filename.strip()

ext = "../data/"

file_out = open("cut_vertex_decomposition_idea.txt", 'w')
file_out.write("This is a test")
file_out.close()




for filename in os.listdir(ext):
	file_out1 = open("cut_vertex_decomposition_idea.txt", 'a')
	if filename[-12:] == 'formated.txt':
		G = nx.readwrite.adjlist.read_adjlist(ext + filename, nodetype = int)
		art_points = nx.algorithms.components.articulation_points(G)

		for k in range(2, 50):
			print(filename, k)

			k_core = heuristic.anchored_k_core(G, k, [])

			if len(k_core) == 0:
				break
			i = 0
			num_art_points = 0

			for point in art_points:
				num_art_points += 1
				if point in k_core:
					i += 1

			thing_to_write = str("Filename: " +  filename+ "with k = "+ str(k) + "\n|V| = "+ str(len(G.nodes())) + "\n nodes in k_core: " + str(len(k_core)) + "\n art_points: "+ str(num_art_points) + "\n interseciton: "+ str(i) + "\n -------------------------- \n")
			file_out1.write(thing_to_write)

			if i == 0:
				break

	file_out1.close()