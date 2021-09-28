import networkx as nx
import rcm
import sys
import time
import csv

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
	time1 = time.time()
	#fname = sys.argv[1]
	fname = 'C:/Users/sakroger/Desktop/k-core/git_code/code/RCM-master/dataset/soc-twitter-higgs.edges'

	#theta = int(sys.argv[2])
	theta = 17
	#budget = int(sys.argv[3])
	budget = 250

	graph = readGraph(fname)

	r = rcm.RCM(graph, theta, budget)
	a, f = r.findAnchors()
	time2 = time.time()

	
	print(len(a) + len(f))
	print(len(a))
	print(len(f) + 250)
	print(time2 - time1)