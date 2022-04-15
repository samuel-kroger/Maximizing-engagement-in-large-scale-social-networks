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


	#k_core = list(nx.k_core(G, k))

	#print(len(k_core))





	olak_time_start = time.time()
	olak_output = list(olak.olakAnchors(G, olak.anchoredKCore(G), k, b))

	#olak_anchors = [element for element in olak_output if element not in k_core]

	#olak_k_core = classes.anchored_k_core(G, k, olak_anchors)

	olak_k_core = classes.anchored_k_core(G, k, olak_output)

	olak_time_end = time.time()

	print(len(olak_k_core))


	title = ['instance', 'k', 'b', 'olak', 'olak time']
	results = [request['filename'], str(k), str(b), str(len(olak_output) - b), str(round(olak_time_end - olak_time_start, 2))]

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
