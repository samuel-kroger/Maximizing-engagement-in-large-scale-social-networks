import gurobipy as gp
import networkx as nx
import time
import math
import read
import flow
import k_core
import pretty_plot
import heuristic
import vermyev

from gurobipy import GRB
from networkx.algorithms import approximation
from matplotlib import pylab as pl
import matplotlib.pyplot as plt

def k_core_iter(G_org, k, anchors = []):
	G = G_org.copy()
	repeat = False
	for node in G.nodes:
		degree = G.degree
		if degree[node] < k and node not in anchors:
			G.remove_node(node)
			repeat = True
			break
	return G, repeat

def k_core(G_org, k, anchors = []):
	G = G_org.copy()
	repeat = True
	while repeat == True:
		G, repeat = k_core_iter(G, k, anchors)
	return (G)

'''
n = 30
erdos_constant = .07
G = nx.erdos_renyi_graph(n, erdos_constant)
'''

instance = 'test_graph3'
ext = "../data/"


F = read.read_graph(ext + instance + ".txt")

G = nx.convert_node_labels_to_integers(F, first_label=0, ordering='default', label_attribute=None)

plt.figure(1)
nx.draw(G, with_labels = True, node_size = 1000)
'''x_vars, y_vars = anc_kcore(G, b, k, start_value = 'false')'''
G = k_core(G, 3)
plt.figure(2)
nx.draw(G, with_labels = True, node_size = 1000)
plt.show()
