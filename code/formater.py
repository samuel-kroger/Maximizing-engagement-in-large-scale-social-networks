import heuristic
import read
import networkx as nx
import matplotlib.pyplot as plt
import os

#instance = 'cnr-2000.graph'
ext = "../data/"
'''
for file in os.listdir(ext):
	#if file[-4:] == '.txt':
	if file[-6:] == '.graph':
		with open(ext + file, 'r') as fin:
			data = fin.read().splitlines(True)
		with open(ext + file, 'w') as fout:
			fout.writelines(data[1:])
		fout.close()

for file in os.listdir(ext):
	if file[-4:] == '.txt':
	#if file[-6:] == '.graph':
'''
		#G = nx.readwrite.adjlist.read_adjlist(ext + file, nodetype = int)

		#nx.readwrite.adjlist.write_adjlist(G, ext + file[:-4] + '_formated.txt')
		#nx.readwrite.adjlist.write_adjlist(G, ext + file[:-6] + '_formated.graph')
G = nx.Graph()
G.add_nodes_from([0, 6])
G.add_edge(0,1)
G.add_edge(0,2)
G.add_edge(0,3)
G.add_edge(1,2)
G.add_edge(1,3)
G.add_edge(2,3)
G.add_edge(2,4)
G.add_edge(4,5)
G.add_edge(4,6)

nx.readwrite.adjlist.write_adjlist(G, ext + 'example_three' + '_formated.txt')
#instance to run
#instance = 'hamid_test_graph1'
#ext = "../data/"


#G = read.imp_dimacs(ext + instance + ".txt")


#G = nx.convert_node_labels_to_integers(F, first_label=1, ordering='default', label_attribute=None)
'''
for i in range(1,3):
	num_nodes = 150 * i
	file =  'erdos_renyi_nodes' + str(num_nodes)
	G = nx.erdos_renyi_graph(num_nodes, 8/num_nodes)

	nx.readwrite.adjlist.write_adjlist(G, ext + file + '.txt')
'''
#nx.readwrite.adjlist.write_adjlist(G, ext + instance + '.txt')
#G = nx.les_miserables_graph()

#G = nx.readwrite.adjlist.read_adjlist(ext + instance +'.txt', nodetype = int)

#G = nx.erdos_renyi_graph(350, .025)