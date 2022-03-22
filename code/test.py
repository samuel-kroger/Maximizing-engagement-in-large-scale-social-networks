import networkx as nx
import rcm
import sys
import csv
import time
import heuristic
from datetime import datetime
import json

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
	user = 'samuel_kroger'
	ext = "../data/"
	dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
	filename = "RCM heuristic" + user + '_' + dt_string + '.csv'
	filename = filename.strip()

	with open('../results/' + filename, 'w') as doc:
		doc.write('dataset, k, b, number of anchors, number of followers, run time')

		f = open('data.json')
		data = json.load(f)


	for request in data['single']:
		print("starting: ",
			'\n filename: ', request['filename'],
			'\n model_type: ', request['model_type'],
			'\n k: ', request['k'],
			'\n b: ', request['b'],
			'\n r: ', request['r'])
		with open('../results/' + filename, 'a') as doc:

			#theta = int(sys.argv[2])
			theta = request['k']
			#budget = int(sys.argv[3])
			budget = request['b']

			G = nx.readwrite.adjlist.read_adjlist(ext + request['filename'], nodetype = int)
			G.remove_edges_from(nx.selfloop_edges(G))
			G = nx.relabel.convert_node_labels_to_integers(G, first_label = 0)

			time1 = time.time()
			r = rcm.RCM(G, theta, budget)
			a, f = r.findAnchors()
			time2 = time.time()

			print(len(a) + len(f))
			print(len(a))
			print(len(f))

			a_list = list(a)

			their_sol = heuristic.anchored_k_core(G, theta, a_list)
			k_core = heuristic.anchored_k_core(G, theta, [])

			doc.write("\n" + request["filename"] + "," + str(theta) + ',' + str(budget) + ',' + str(len(a)) + ',' + str(len(f)) + ',' + str(time2 - time1))
