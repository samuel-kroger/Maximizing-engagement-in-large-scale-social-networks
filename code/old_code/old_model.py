import gurobipy as gp
import networkx as nx
import numpy as np
import time
import math
import read
import flow
import k_core
import pretty_plot
import heuristic
import vermyev
from datetime import datetime
from gurobipy import GRB
from networkx.algorithms import approximation
import matplotlib.pyplot as plt

user = 'samuel_kroger'
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = user + '_' + dt_string + '.csv'
filename = filename.strip()

def model(G, filename, anchored, radius_bounded, reduced_model, heuristic_status, k, b, r, connectivity, plot, print_to_console, temp, warm_start):

	#init variables
	num_k_core_nodes = 0
	R = []
	weights = {}
	var_sub = 0

	#init model
	m = gp.Model()
	m._X = m.addVars(G.nodes(), vtype=GRB.BINARY, name="x")
	m._Y = m.addVars(G.nodes(), vtype=GRB.BINARY, name="y")

	#warm_start
	for fixing in warm_start[0]:
		m._Y[fixing[1]].start = 1
		for vertex in fixing[2]:
			m._X[vertex].start = 1
	for u in warm_start[1]:
		m._Y[u].ub = 0

	#set params
	m.setParam('OutputFlag', 1)
	m.Params.timeLimit= 120*60
	m.params.LogToConsole = 0
	m.params.LogFile='../results/logs/log_' + filename +'_' + str(k) + '_' +  str(b) + '.log'

	if reduced_model:
		#G_temp = heuristic.k_core(G, k)
		#nx.algorithms.core.k_core(G, k)
		G_temp = heuristic.new_code(G, k)
		G_temp = G.subgraph(G_temp)


		#case if everynode is in the k-core
		if G == G_temp:
			return('NA',  len(G.nodes()), len(G.nodes()),'1')

		#case if none of the nodes are in a k-core
		if len(G_temp.nodes()) == 0:
			var_num, LB, UB, num_k_core_nodes = model(G, filename, anchored, radius_bounded, False, heuristic_status, k, b, r, connectivity, plot, print_to_console, temp, [[],[]])
			return(var_num, LB, UB, 0)

		#Get each k-core
		components = nx.algorithms.components.connected_components(G_temp)

		for comp in components:
			for node in comp:
				num_k_core_nodes += 1

		#R is the list of nodes not in the k-core
		R = list(G.nodes() - G_temp.nodes())

		#building the weights
		for node in R:
			weights[node] = 0
			for neighbor in G.neighbors(node):

				if neighbor in G_temp.nodes():
						weights[node] += 1
		#Keeping track of the variable reduction
		var_sub = 0
		for node in G_temp.nodes():
			m._X[node].ub = 0
			m._Y[node].ub = 0
			var_sub += 2

	#Add all contraints and Objective function

	k_core.build_k_core(G, m, anchored, radius_bounded, connectivity, reduced_model, k, b, weights, R, num_k_core_nodes, temp)

	#Manages the heuristics
	if heuristic_status != 'no_heur':
		if heuristic_status == 'brute_force':
			heur_graph, heur_source = heuristic.brute_force_heur(G,k,r)
		if heuristic_status == 'eccentricity':
			heur_graph, heur_source = heuristic.eccen_heur(G,k,r)
		m._S.start = 1
		for i in heur_graph.nodes():
			m._X[i].start = 1

	m.optimize()
	print_to_console = False

	if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
		if print_to_console:
			cluster = [i for i in G.nodes if m._X[i].x > 0.5 or m._Y[i].x > 0.5]
			SUB = G.subgraph(cluster)

			#for node in SUB.nodes():
			#	print("Degree is: ", SUB.degree[node])

			for i in G.nodes:
				if radius_bounded == True:
					if m._S[i].x > 0.5:
						print("Root is ", i)
						root = i

			selected_nodes = []
			for i in G.nodes:
				if m._X[i].x > 0.5:
					print("selected node: ", i)
					selected_nodes.append(i)

			purchased_nodes = []
			for i in G.nodes:
				if m._Y[i].x > 0.5:
					print("purchased node: ", i)
					purchased_nodes.append(i)

			#print("# of vertices in G: ", len(G.nodes))
			#print("Is it connected? ", nx.is_connected(SUB))
			#print("Diameter? ", nx.diameter(SUB))
			plot = 1
			if plot == 1:
				pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, -1, True, k, b, 0)
			if plot == 2:
				pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, False, k, b, r)

		#m.write("Lobster.lp")
		var = m.getVars()

		return len(var) - var_sub, m.objBound, m.objVal, num_k_core_nodes
