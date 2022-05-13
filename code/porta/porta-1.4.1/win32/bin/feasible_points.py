import networkx as nx
import matplotlib.pyplot as plt
import os
from itertools import product
import numpy as np


filename = "prop_5.txt"


#G = nx.read_adjlist("../data/" + filename)
#G = nx.convert_node_labels_to_integers(G, ordering="sorted")

'''
#FOR PROP 3, 4, 6
G = nx.Graph()
G.add_node(0)
G.add_node(1)
G.add_node(2)
G.add_node(3)
G.add_node(4)
G.add_node(5)
G.add_node(6)
G.add_node(7)


G.add_edge(0,1)
G.add_edge(1,3)
G.add_edge(3,2)
G.add_edge(2,0)

G.add_edge(0,4)
G.add_edge(1,5)
G.add_edge(2,7)
G.add_edge(3,6)
#
'''
#FOR PROP 5
G = nx.Graph()


G.add_node(0)
G.add_node(1)
G.add_node(2)
G.add_node(3)
G.add_node(4)
G.add_node(5)


G.add_edge(0,1)
G.add_edge(0,2)
G.add_edge(1,2)

G.add_edge(0,3)
G.add_edge(1,4)
G.add_edge(2,5)



#G.add_edge(0,2)

'''
G = nx.Graph()

G.add_node(0)
G.add_node(1)
G.add_node(2)
G.add_node(3)
G.add_node(4)
G.add_node(5)

G.add_edge(0,2)
G.add_edge(0,3)
G.add_edge(0,1)
G.add_edge(1,4)
G.add_edge(1,5)
'''
#nx.write_adjlist(G, "../data/" + filename)


b = 4
k = 3

k_core = nx.k_core(G, k)

n = len(G.nodes())

feasible_points = []

print(G.nodes())

for point in product(range(2), repeat = 2 * n):

	x_point = point[:n]
	y_point = point[n:]

	fail = False



	if sum(y_point) <= b:
		graph_point = np.array(x_point) + np.array(y_point)

		for counter, node in enumerate(graph_point):
			if node == 2:
				graph_point[counter] = 1

		sub_nodes = []


		for counter, node in enumerate(graph_point):
			if node == 1:
				sub_nodes.append(counter)

		x_nodes = []
		for counter, node in enumerate(x_point):
			if node == 1:
				x_nodes.append(counter)

		sub = G.subgraph(sub_nodes)
		deg = sub.degree(x_nodes)

		for node in deg:
			if node[1] < k:
				fail = True

		for node in range(n):
			if x_point[node] == 0:
				if node in k_core.nodes():
					fail = True
			if x_point[node] == 1 and y_point[node] == 1:
				fail = True
			if y_point[node] == 1:
				if node in k_core.nodes():
					fail = True

		if not fail:
			print(point)
			feasible_points.append(point)




print(len(feasible_points))



with open(filename + '.poi', 'w') as doc:
	doc.write('DIM = ' + str(2 * n) + '\n\n' + 'CONV_SECTION')
with open(filename + '.poi', 'a') as doc:
	for point in feasible_points:
		line = '\n '
		for node in point:
			line += str(node) + ' '

		doc.write(line[:-1])
	doc.write('\n\nEND\nDIMENSION OF THE POLYHEDRON: ' + str(2 * n))

#plt.figure(1)
#nx.draw(G, with_labels = True, node_size = 500)
#G = nx.convert_node_labels_to_integers(G, 1)
#plt.figure(2)
#G = nx.convert_node_labels_to_integers(G, first_label=1, ordering="sorted")
nx.draw(G, with_labels = True, node_size = 500)
plt.show()