import gurobipy as gp
from gurobipy import GRB
import networkx as nx
from networkx.algorithms import approximation
from matplotlib import pylab as pl
import matplotlib.pyplot as plt

import read
import time
import main

##########################
# Get parameters from user
##########################
# what is k?
k = 2

# Is the k-core problem anchored?
anchored = True

# If the k-core problem is anchored k-core, then what is the budget b?
b = 1

# Is the k-core problem radius bounded?
radius_bounded = True

# If the k-core problem is radius bounded, then what is the radius bound r?
r = 1

#Do you want to use the heuristic?
use_heur = False

# Connectivity formulation?
connectivity = 'flow'

# What is the instance?
instance = 'test_graph'

# Start solving model
######################

ext = "../data/"

heuristic_num = 1

#F = read.read_graph(ext + instance + ".txt")

#G = nx.convert_node_labels_to_integers(F, first_label=0, ordering='default', label_attribute=None)



G = nx.readwrite.adjlist.read_adjlist(ext + 'generated_graph2.txt', nodetype = int)

for i in range(100):
	G = nx.erdos_renyi_graph(175, .05)
	while not nx.is_connected(G):
		G = nx.erdos_renyi_graph(175, .05)

	plt.figure(1)
	time1 = time.time()
	first = main.main(G, anchored, radius_bounded, use_heur, k, b, r, connectivity, heuristic_num, 0)
	time2 = time.time()


	plt.figure(2)
	connectivity = 'vermyev'
	time3 = time.time()
	second = main.main(G, anchored, radius_bounded, use_heur, k, b, r, connectivity, heuristic_num, 0)
	time4 = time.time()


	if len(first) == len(second):
		print("objectives are the same")

	if len(first) != len(second):
		print("not the same")
		print(i)
		nx.readwrite.adjlist.write_adjlist(G, ext + 'generated_graph3.txt')

#plt.show()

print('flow_based: ', time2 - time1)
print('vermyev: ', time4 - time3)