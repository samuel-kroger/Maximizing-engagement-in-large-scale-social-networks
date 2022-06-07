from datetime import datetime
from classes import *
import json
import os
import time
import classes


#user = 'samuel_kroger'
ext = "../data/"
dt_string = datetime.now().strftime("%Y_%m_%d_%H_%M")
filename = dt_string + '.csv'
filename = filename.strip()

f = open('data.json')
data = json.load(f)

for request in data['reduced_model']:
	print("starting: ",
		'\n filename: ', request['filename'],
		'\n model_type: ', request['model_type'],
		'\n k: ', request['k'],
		'\n b: ', request['b'],
		'\n r: ', request['r'])

	G = classes.read_graph(ext + request['filename'])
	'''
	even_subgraph = []
	odd_subgraph = []
	for i in range(0, 59):
		even_subgraph.append(str(i))

	even_subgraph.remove('30')
	even_subgraph.remove('31')
	even_subgraph.remove('32')
	even_subgraph.remove('33')
	even_subgraph.remove('34')
	even_subgraph.remove('35')
	even_subgraph.remove('36')

	even_subgraph.remove('43')
	even_subgraph.remove('13')
	even_subgraph.remove('57')

	#even_subgraph.remove('5')
	even_subgraph.remove('12')
	even_subgraph.remove('42')
	even_subgraph.remove('55')

	#even_subgraph.remove('18')
	#even_subgraph.remove('23')


	#print(even_subgraph)
	#print(odd_subgraph)

	G = G.subgraph(even_subgraph)
	#print(G.nodes())
	'''
	'''
	G = nx.cycle_graph(15)
	G.add_edge(0,4)
	G.add_edge(9,12)
	G.add_edge(5,8)
	G.add_edge(9,10)
	G.add_edge(13,15)
	G.add_edge(12,5)
	G.add_edge(11,13)
	G.add_edge(11,3)
	G.add_edge(5,9)
	G.add_edge(3,14)
	G.add_edge(13,10)

	#G.add_node(6)
	#G.add_node(7)
	#G.add_node(8)
	#G.add_edge(6,7)
	#G.add_edge(7,8)
	#remove_nodes = []
	#remove_nodes = ['0','1','2','3','4','5']
	'''
	start_time = time.time()
	instance = globals()[request['model_type']](filename, request['filename'][:-4], G, request['model_type'], request['k'], request['b'], request['r'], request['y_saturated'], request['additonal_facet_defining'], request['y_val_fix'], request['fractional_callback'], request['relax'])
	if request['remove_y_edges']:
		instance.remove_y_edges()
		instance.RCM_warm_start()
	if instance.model_type == "cut_model":
		#instance.warm_start_one()
		#instance.center_fixing_idea_recursive()
		#instance.dominated_fixing_idea()
		#instance.dominated_fixing_idea_power_graph()
		#instance.dominated_fixing_idea_power_graph_sam()
		''

	instance.optimize()
	#instance.print_model()

	end_time = time.time()

	instance.save_to_file(str(round(end_time - start_time, 2)))
