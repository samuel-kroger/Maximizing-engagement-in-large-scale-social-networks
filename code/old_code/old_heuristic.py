import networkx as nx
import read
import pretty_plot
import matplotlib.pyplot as plt
import time
import numpy as np


def new_code(graph, k):
	output = []
	n = len(graph.nodes())

	deg = [0] * n
	vert = [0] * n
	pos = [0] * n

	md = 0

	for v in range(0, n):
		d = graph.degree(v)
		deg[v] = d

		if d > md:
			md = d


	binn = [0] * (md + 1)


	for v in range(0, n):

		binn[deg[v]] += 1

	start = 0

	for d in range(0, md + 1):
		num = binn[d]
		binn[d] = start
		start += num


	for v in range(0, n):
		pos[v] = binn[deg[v]]
		vert[pos[v]] = v
		binn[deg[v]] += 1

	for d in range(md, 0, -1):
		binn[d] = binn[d-1]
	binn[0] = 1

	for i in range(0, n):
		v = vert[i]
		if not graph.nodes[v]['anchor']:


			for u in graph.neighbors(v):

				if not graph.nodes[u]['anchor']:

					if deg[u] > deg[v]:
						du = deg[u]
						pu = pos[u]
						pw = binn[du]

						w = vert[pw]
						if u != w:
							pos[u] = pw
							vert[pu] = w
							pos[w] = pu
							vert[pw] = u
						binn[du] += 1
						deg[u] -= 1

	for i in range(0, len(deg)):
		if deg[i] >= k:
			output.append(i)
	list_of_nodes = []
	for v in graph.subgraph(output).nodes():
		list_of_nodes.append(v)
	return(list_of_nodes)

def temp_idea(G,k):
	x_vals = []
	y_vals = []
	best = 0


	for i in G.nodes():
			if G.degree[i] < k:
				y_vals.append(i)
			else:
				x_vals.append(i)

	for node in y_vals:
		time1 = time.time()
		nx.algorithms.core.k_core(G, k)
		time2 = time.time()


def warm_start(G, k, b):

	x_vals = []
	y_vals = []
	best = []


	for i in G.nodes():
			if G.degree[i] < k:
				y_vals.append(i)
			else:
				x_vals.append(i)


	timer = 0
	for node in y_vals:
		if G.degree(node) <= 5:
			time1 = time.time()
			G.nodes[node]['anchor'] = True
			result = new_code(G, k)
			current = [node, result]
			G.nodes[node]['anchor'] = False
			time2 = time.time()
			timer += time2 - time1
			best.append(current)
			if timer >= 2*60:
				break

	value_of_anchor = []
	anchor = []
	nodes_in_k_core = []

	for fixing in best:
		value_of_anchor.append(len(fixing[1]))
		anchor.append(fixing[0])
		nodes_in_k_core.append(fixing[1])

	b_best_fixings = sorted(zip(value_of_anchor, anchor, nodes_in_k_core), reverse = True)[:b]

	dead_y = []
	anchors_in_b_best = []
	for fixing in b_best_fixings:

		anchors_in_b_best.append(fixing[1])
		print('Anchored: ', fixing[1])
		print('Number in the k_core: ',fixing[0])

	for fixing in best:
		if fixing[0] not in anchors_in_b_best:
			dead_y.append(fixing[0])
	print("dead y number: ", len(dead_y))
	return [b_best_fixings, dead_y]


def k_core_iter(graph, k, anchors = []):
	remove = []
	G = graph.copy()
	repeat = False
	for node in G.nodes:
		degree = G.degree
		if degree[node] < k and node not in anchors:
			remove.append(node)
			repeat = True
	G.remove_nodes_from(remove)
	return G, repeat

def k_core(graph, k, anchors = []):
	G = graph.copy()
	repeat = True
	while repeat == True:
		G, repeat = k_core_iter(G, k, anchors)
	return G

def eccen_heur(graph, k, r):
	G = graph.copy()
	G = k_core(graph, k)
	connected_components = nx.algorithms.components.connected_components(G)
	kcore = nx.empty_graph(0)
	s = 'fail'

	for connected_component in connected_components:
		subgraph = G.subgraph(connected_component)

		if len(subgraph.nodes()) > len(kcore):
			eccentricity_dict = nx.algorithms.distance_measures.eccentricity(subgraph)
			#if min(testing, key = testing.get) <= r:
			s_new = (min(eccentricity_dict, key=eccentricity_dict.get))
			s_new_val = eccentricity_dict[s_new]
			if s_new_val <= r:
				kcore = subgraph
				s = s_new
	return kcore, s

def brute_force_heur(graph, k, r):
	best = nx.empty_graph(0)
	s = 'fail'
	for v in graph.nodes():
		subgraph = nx.generators.ego.ego_graph(graph, v, radius = r)
		kcore = k_core(subgraph, k)
		if len(kcore.nodes()) >= len(best.nodes()):
			best = kcore
			s = v
	return best, s