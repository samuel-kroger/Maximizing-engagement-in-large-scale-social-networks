import classes
import rcm
import olak
import time
import json
from datetime import datetime
import networkx as nx
import os
from statistics import median

ext = "../data/"
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M")
filename = dt_string + '.csv'
filename = filename.strip()

f = open('data.json')
data = json.load(f)

for request in data['graph_info']:
	print("starting: ",
		'\n filename: ', request['filename'],
		'\n k: ', request['k'])

	G = classes.read_graph(ext + request['filename'])
	k = request['k']

	degree_list = []
	for node in G.nodes():
		degree_list.append(G.degree(node))

	max_degree = max(degree_list)
	median_degree = median(degree_list)

	k_core_decomposition = olak.anchoredKCore(G)
	tracker = []
	for node in k_core_decomposition:
		tracker.append(k_core_decomposition[node])

	median_k_core = median(tracker)
	max_k_core = max(tracker)


	k_core = list(nx.k_core(G, median_k_core))
	n = len(G.nodes())
	m = len(G.edges())
	print(len(k_core))




	#title = ['instance', 'k', 'b', 'olak', 'olak time', 'rcm', 'rcmtime']
	#results = [request['filename'], str(k), str(b), str(len(rcm_k_core)), str(round(rcm_time_end - rcm_time_start, 2)), str(len(olak_k_core)), str(round(olak_time_end - olak_time_start, 2))]

	title = ['instance', 'n', 'm', 'average_degree', 'max_degree', 'max_k_core', 'median_k_core', 'k', 'k_core']
	results = [request['filename'], str(n), str(m), str(median_degree), str(max_degree), str(max_k_core), str(median_k_core), str(k), str(len(k_core))]


	if not os.path.exists("../results/" + filename):
			with open("../results/" + filename, "w") as doc:
				string = ""
				for thing in title:
					string += thing + ", "
				string += 'total_time'
				doc.write(string)
				doc.close()

	with open("../results/" + filename, "a") as doc:
		string = "\n"
		for thing in results:
			string += thing + ", "
		doc.write(string)
		doc.close()
