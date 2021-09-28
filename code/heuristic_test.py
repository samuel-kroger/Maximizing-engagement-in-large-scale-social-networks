import networkx as nx
import matplotlib.pyplot
import heuristic

import random
import json
import os
#import read
import time
import csv

user = 'samuel_kroger'
ext = "../data/"


f = open('data.json')
data = json.load(f)

def local_heuristic(G, k, b, solution, anchors, core_nodes):
	swap_num = 10
	new_anchors = []
	switch_anchors = random.sample(anchors, swap_num)
	for anchor in switch_anchors:
		new_anchors.append(random.sample([neighbor for neighbor in G[anchor]], 1)[0])

	new_anchor_set = [node for node in anchors if node not in switch_anchors]
	for new_anchor in new_anchors:
		new_anchor_set.append(new_anchor)

	potential_sol = heuristic.anchored_k_core(G, k, core_nodes + new_anchor_set)

	if len(potential_sol) > len(solution):
		return potential_sol, new_anchor_set

	return solution, anchors




for request in data['heuristic']:
	G = nx.readwrite.adjlist.read_adjlist(ext + request['filename'], nodetype = int)
	G = nx.relabel.convert_node_labels_to_integers(G, first_label = 0)
	print("starting: ",
	'\n filename: ', request['filename'],
	'\n k: ', request['k'],
	'\n b: ', request['b'],
	'\n r: ', request['r'])

	start_time = time.time()

	k = request['k']
	b = request['b']

	
	core_nodes = heuristic.anchored_k_core(G, k, [])
	remaining = [node for node in G.nodes if node not in core_nodes]

	x_vals = []
	y_vals = []

	'''
	for node in remaning:
		if G.degree(node) >= k:
			x_vals.append(node)
		else:
			y_vals.append(node)
	'''

	best_sol = []
	best_anchors = []

	for i in range(1, 100):
		anchors = random.sample(remaining, b)

		result = heuristic.anchored_k_core(G, k, core_nodes + anchors)

		if len(result) > len(best_sol):
			best_sol = result
			best_anchors = anchors
			print('iteraiton ', i, ': ', len(result) - len(core_nodes))
	print('here')
	for i in range(1, 1000):
		best_sol, best_anchors = local_heuristic(G, k, b, best_sol, best_anchors, core_nodes)
		print('iteration, ', i, ': ', len(best_sol) - len(core_nodes))







