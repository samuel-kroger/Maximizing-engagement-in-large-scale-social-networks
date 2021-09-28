import networkx as nx
import rcm
import sys
import csv
import heuristic

def readGraph(fname):
	if fname.endswith('mtx'):
		edges = []
		with open(fname, 'r') as f:
			reader = csv.reader(f, delimiter=' ')
			edges = [row for row in reader if len(row) == 2]
			f.close()
		graph = nx.Graph()
		graph.add_edges_from(edges, nodetype=int)
	else:
		graph = nx.read_edgelist(fname)

	graph.remove_edges_from(nx.selfloop_edges(graph))
	graph.remove_nodes_from(list(nx.isolates(graph)))

	print(nx.info(graph))

	return graph

def new_heuristic(graph, k, b):
	r = rcm.RCM(graph, k, b)
	anchors, followers = r.findAnchors()

	return anchors


if __name__ == '__main__':
	#fname = sys.argv[1]
	fname = 'C:/Users/sakroger/Desktop/k-core/git_code/code/RCM-master/dataset/facebook_combined.txt'
	#theta = int(sys.argv[2])
	theta = 46
	#budget = int(sys.argv[3])
	budget = 250

	#graph = readGraph(fname)
	G = readGraph(fname)
	#G = nx.readwrite.adjlist.read_adjlist(fname, nodetype = int)
	G = nx.relabel.convert_node_labels_to_integers(G, first_label = 0)

	r = rcm.RCM(G, theta, budget)
	a, f = r.findAnchors()

	print(len(a) + len(f))
	print(len(a))
	print(len(f))

	a_list = list(a)


	their_sol = heuristic.anchored_k_core(G, theta, a_list)
	k_core = heuristic.anchored_k_core(G, theta, [])

	print(len(their_sol) - len(k_core))
	print(len(their_sol) - len(a))