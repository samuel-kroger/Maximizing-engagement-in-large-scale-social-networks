import gurobipy as gp
from gurobipy import GRB
import networkx as nx
from networkx.algorithms import approximation
from matplotlib import pylab as pl
import matplotlib.pyplot as plt

import read
import time
import main
import os


instances = {
	'karate', 'chesapeake', 'dolphins', 'lesmis', 'polbooks',
	'adjnoun', 'football', 'jazz', 'cn', 'cm',
	'netscience', 'polblogs', 'email', 'data'
	}

##########################
# Get parameters from user
##########################
k = 2
anchored = True
b = 1
radius_bounded = True
r = 1
#eptions 	'no_heur', 'brute_force', 'eccentricity'
heuristic_status = 'eccentricity'
connectivity = 'flow'


#instance to run
instance = 'les_miserables'
ext = "../data/"


#F = read.read_graph(ext + instance + ".txt")

#G = nx.convert_node_labels_to_integers(F, first_label=0, ordering='default', label_attribute=None)

for i in range(1,6):
	num_nodes = 150 * i
	file =  'erdos_renyi_nodes' + str(num_nodes)
	G = nx.erdos_renyi_graph(num_nodes, 3/num_nodes)

	nx.readwrite.adjlist.write_adjlist(G, ext + file + '.txt')

#G = nx.les_miserables_graph()

#G = nx.readwrite.adjlist.read_adjlist(ext + instance +'.txt', nodetype = int)

#G = nx.erdos_renyi_graph(350, .025)


# Start solving model
######################
'''
plt.figure(1)
time1 = time.time()
first = main.main(G, anchored, radius_bounded, heuristic_status, k, b, r, connectivity, 0)
time2 = time.time()


plt.figure(2)
connectivity = 'vermyev'
time3 = time.time()
second = main.main(G, anchored, radius_bounded, heuristic_status, k, b, r, connectivity, 0)
time4 = time.time()


if len(first) == len(second):
	print("objectives are the same")

if len(first) != len(second):
	print("not the same")
	print(i)
'''
#nx.readwrite.adjlist.write_adjlist(G, ext + instance + '.txt')

#plt.show()

#print('flow_based: ', time2 - time1)
#print('vermyev: ', time4 - time3)