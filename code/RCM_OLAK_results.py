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

for request in data['below_the_line']:
	print("starting: ",
		'\n filename: ', request['filename'],
		'\n k: ', request['k'],
		'\n b: ', request['b'])

	G = classes.read_graph(ext + request['filename'])
	k = request['k']
	b = request['b']

	#k_core = nx.k_core(G, k)

	#k_core_decomposition = olak.anchoredKCore(G)
	#tracker = []
	#for node in k_core_decomposition:
	#	tracker.append(k_core_decomposition[node])

	#print("median k: " + str(median(tracker)))
	#print("cardinality of med k_core: " + str((len(k_core))))

	k_core = list(nx.k_core(G, k))
	#print(len(G.nodes()))
	#print(len(G.edges()))
	#print(len(k_core))




	rcm_time_start = time.time()
	r = rcm.RCM(G, k, b)
	a, f = r.findAnchors()
	rcm_k_core = classes.anchored_k_core(G, k, a)
	print(len(rcm_k_core))
	rcm_time_end = time.time()

	olak_time_start = time.time()
	olak_output = list(olak.olakAnchors(G, olak.anchoredKCore(G), k, b))
	olak_anchors = [element for element in olak_output if element not in k_core]
	olak_k_core = classes.anchored_k_core(G, k, olak_anchors)
	olak_time_end = time.time()

	print(len(olak_k_core))

	title = ['instance', 'k', 'b', 'olak', 'olak time', 'rcm', 'rcmtime']
	results = [request['filename'], str(k), str(b), str(len(rcm_k_core)), str(round(rcm_time_end - rcm_time_start, 2)), str(len(olak_k_core)), str(round(olak_time_end - olak_time_start, 2))]
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
