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

def original_model(G, anchored, radius_bounded, heuristic_status, k, b, r, connectivity, plot):

	m = gp.Model()
	m.setParam('OutputFlag', 0)
	m.Params.timeLimit=1800

	m._X = m.addVars(G.nodes, vtype=GRB.BINARY, name="x")
	m._Y = m.addVars(G.nodes, vtype=GRB.BINARY, name="y")
	k_core.build_k_core(G, m, anchored, k, b)
	if radius_bounded and connectivity == 'flow':
		flow.build_flow(G, m, r)
	if radius_bounded and connectivity == 'vermyev':
		vermyev.build_vermyev(G, m, r)

	if heuristic_status != 'no_heur':
		if heuristic_status == 'brute_force':
			heur_graph, heur_source = heuristic.brute_force_heur(G,k,r)
		if heuristic_status == 'eccentricity':
			heur_graph, heur_source = heuristic.eccen_heur(G,k,r)
		m._S.start = 1
		for i in heur_graph.nodes():
			m._X[i].start = 1


	m.optimize()

	#m.computeIIS()

	m.write("out.lp")


	if m.status == GRB.OPTIMAL or m.status==GRB.TIME_LIMIT:
		cluster = [i for i in G.nodes if m._X[i].x > 0.5 or m._Y[i].x > 0.5]
		SUB = G.subgraph(cluster)

		for i in G.nodes:
			if radius_bounded == True:
				if m._S[i].x > 0.5:
					#print("Root is ", i)
					root = i

		selected_nodes = []
		for i in G.nodes:
			if m._X[i].x > 0.5:
				#print("selected node: ", i)
				selected_nodes.append(i)

		purchased_nodes = []
		for i in G.nodes:
			if m._Y[i].x > 0.5:
				#print("purchased node: ", i)
				purchased_nodes.append(i)

		if connectivity == 'flow':
			for n in G.nodes:
				for j in G.nodes:
					for i in G.neighbors(j):
						if m._F[n,j,i].x > 0.5:
							#print(n, j, i, m._F[n,j,i].x)
							''





		#print("# of vertices in G: ", len(G.nodes))
		#print("Is it connected? ", nx.is_connected(SUB))
		#print("Diameter? ", nx.diameter(SUB))

		if plot == 1:
			pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, True, k, b, r)
		if plot == 2:
			pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, False, k, b, r)


		#m.write("sam.lp")

		vars = m.getVars()
		'''
		plt.figure(1)
		pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, center = -1, plot_now = False, k = k, b = b)
		'''
		return len(vars), m.objBound, m.objVal

def reduced_model(G, anchored, radius_bounded, heuristic_status, k, b, r, connectivity, plot):
	k_core_nodes = []
	thing = len(G.nodes())
	s = 0
	m = gp.Model()
	weights = {}

	G_temp = heuristic.k_core(G,k)

	if G == G_temp:
		return(original_model(G, anchored, radius_bounded, heuristic_status, k, b, r, connectivity, plot), 0)

	if not nx.is_empty(G_temp):
		components = nx.algorithms.components.connected_components(G_temp)

		for comp in components:
			comp = list(comp)
			k_core_node = comp[0]
			k_core_nodes.append(k_core_node)

			for node in comp:
				for i in G.neighbors(node):
					if i not in comp:
						if (k_core_node, i) in weights:
							weights[(k_core_node, i)] = weights[(k_core_node, i)] + 1
						else:
							weights[(k_core_node, i)] = 1
			for node in comp:
				G = nx.contracted_nodes(G, k_core_node, node)
				s += 1;

			comp.pop(0)

			if len(G.nodes()) == 1:
				return('none', thing, thing,'1')
		'''
		print(k)
		print(k_core_nodes)
		print(s)
		'''
		for i in k_core_nodes:
			for j in G.nodes():
				if (i,j) not in weights:
					weights[(i,j)] = 0

	m.setParam('OutputFlag', 0)
	m.Params.timeLimit=1800

	reduced = G.nodes -k_core_nodes

	m._X = m.addVars(reduced, vtype=GRB.BINARY, name="x")
	m._Y = m.addVars(reduced, vtype=GRB.BINARY, name="y")

	k_core.build_k_core_reduced(G, m, anchored, k, b, weights, k_core_nodes, s)
	if radius_bounded and connectivity == 'flow':
		flow.build_flow(G, m, r)
	if radius_bounded and connectivity == 'vermyev':
		vermyev.build_vermyev(G, m, r)

	if heuristic_status != 'no_heur':
		if heuristic_status == 'brute_force':
			heur_graph, heur_source = heuristic.brute_force_heur(G,k,r)
		if heuristic_status == 'eccentricity':
			heur_graph, heur_source = heuristic.eccen_heur(G,k,r)
		m._S.start = 1
		for i in heur_graph.nodes():
			m._X[i].start = 1


	m.optimize()

	#m.computeIIS()

	m.write("out.lp")


	if m.status == GRB.OPTIMAL or m.status==GRB.TIME_LIMIT:
		cluster = [i for i in reduced if m._X[i].x > 0.5 or m._Y[i].x > 0.5]
		SUB = G.subgraph(cluster)

		for i in G.nodes:
			if radius_bounded == True:
				if m._S[i].x > 0.5:
					#print("Root is ", i)
					root = i

		selected_nodes = []
		for i in reduced:
			if m._X[i].x > 0.5:
				#print("selected node: ", i)
				selected_nodes.append(i)

		purchased_nodes = []
		for i in reduced:
			if m._Y[i].x > 0.5:
				#print("purchased node: ", i)
				purchased_nodes.append(i)

		if connectivity == 'flow':
			for n in G.nodes:
				for j in G.nodes:
					for i in G.neighbors(j):
						if m._F[n,j,i].x > 0.5:
							#print(n, j, i, m._F[n,j,i].x)
							''
		vars = m.getVars()
		'''
		plt.figure(2)
		pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, center = -1, plot_now = True, k = k, b = b)
		'''
		return len(vars), m.objBound, m.objVal, len(k_core_nodes)