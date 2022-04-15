import networkx as nx
import time

def preprocess(G, k, options):
	G = nx.relabel.convert_node_labels_to_integers(G)
	x_vals = []
	y_vals = []
	for node in G.nodes():
		if G.degree(node)>= k:
			x_vals.append(node)
		else:
			y_vals.append(node)
	#print(len(y_vals))
	for node in y_vals:
		time1 = time.time()
		remove = []
		#print(node)
		for neighbor in G.neighbors(node):
			if neighbor in y_vals:
				remove.append(neighbor)
		for thing in remove:
			G.remove_edge(node, thing)
		time2 = time.time()
	if options == 1:
		x_tracker = [0] * (len(G.nodes()))

		for y_val in y_vals:
			for neighbor in G.neighbors(y_val):
				x_tracker[neighbor] += 1
		for x_val in x_vals:
			x_tracker[x_val] += k - G.degree(x_val)

	return G, x_vals, y_vals