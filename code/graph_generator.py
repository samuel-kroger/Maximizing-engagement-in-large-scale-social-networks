import networkx as nx
import matplotlib.pyplot as plt

ext = "../data/"
file = "test_instance_1"

G = nx.Graph()
G.add_node(0)
G.add_node(1)
G.add_node(2)
G.add_node(3)
#G.add_node(4)
#G.add_node(5)
#G.add_node(6)
#G.add_node(7)
#G.add_node(8)

G.add_edge(0,1)
G.add_edge(1,2)
G.add_edge(2,3)
#G.add_edge(3,4)

#G.add_edge(5,6)
#G.add_edge(6,7)
#G.add_edge(7,5)
#G.add_edge(5,4)
#G.add_edge(8,5)

nx.draw(G, with_labels = True, node_size = 500)
plt.show()

nx.readwrite.adjlist.write_adjlist(G, ext + file + '.txt')