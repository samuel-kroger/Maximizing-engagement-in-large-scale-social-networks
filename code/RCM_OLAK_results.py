import classes
import rcm
import olak
import time
import json
from datetime import datetime

ext = "../data/"
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M")
filename = dt_string + '.csv'
filename = filename.strip()

f = open('data.json')
data = json.load(f)

for request in data['single']:
	print("starting: ",
		'\n filename: ', request['filename'],
		'\n model_type: ', request['model_type'],
		'\n k: ', request['k'],
		'\n b: ', request['b'])

	G = classes.read_graph(ext + request['filename'])
	k = request['k']
	b = request['b']
	start_time = time.time()
	r = rcm.RCM(G, k, b)
	a, f = r.findAnchors()
	rcm_anchors = a
	rcm_followers = f
	k_core = classes.anchored_k_core(G, k, [])

	print(len(rcm_followers) + len(k_core))

	end_time = time.time()