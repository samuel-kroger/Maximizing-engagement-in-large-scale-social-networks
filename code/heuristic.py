import networkx as nx
import read
import pretty_plot
import matplotlib.pyplot as plt
import time

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