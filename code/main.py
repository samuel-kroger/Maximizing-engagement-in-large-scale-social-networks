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

def main(G, anchored, radius_bounded, heuristic_status, k, b, r, connectivity, plot):

	m = gp.Model()

	m._X = m.addVars(G.nodes, vtype=GRB.BINARY, name="x")
	m._Y = m.addVars(G.nodes, vtype=GRB.BINARY, name="y")
	k_core.build_k_core(G, m, anchored, k, b)
	if radius_bounded and connectivity == 'flow':
		flow.build_flow(G, m, r)
	if radius_bounded and connectivity == 'vermyev':
		vermyev.build_vermyev(G, m, r)

	time1 = time.time()
	if heuristic_status != 'no_heur':
		if heuristic_status == 'brute_force':
			heur_graph, heur_source = heuristic.brute_force_heur(G,k,r)
		if heuristic_status == 'eccentricity':
			heur_graph, heur_source = heuristic.eccen_heur(G,k,r)
		m._S.start = 1
		for i in heur_graph.nodes():
			m._X[i].start = 1
	time2 = time.time()
	print(time2 - time1)

	m.optimize()

	#m.computeIIS()

	m.write("out.lp")

	if m.status == GRB.OPTIMAL or m.status==GRB.TIME_LIMIT:
		cluster = [i for i in G.nodes if m._X[i].x > 0.5 or m._Y[i].x > 0.5]
		SUB = G.subgraph(cluster)

		for i in G.nodes:
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





		print("# of vertices in G: ", len(G.nodes))
		print("Is it connected? ", nx.is_connected(SUB))
		print("Diameter? ", nx.diameter(SUB))

		if plot == 1:
			pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, True, k, b, r)
		if plot == 2:
			pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, False, k, b, r)
		m.write("sam.lp")
		return selected_nodes








