import networkx as nx
import matplotlib.pyplot as plt

ext = "../data/"
file = "continuous_counter_example"

G = nx.Graph()
G.add_node(0)
G.add_node(1)
G.add_node(2)
G.add_node(3)

G.add_edge(0,1)
G.add_edge(0,2)
G.add_edge(0,3)
G.add_edge(1,2)
G.add_edge(1,3)
G.add_edge(2,3)

G.add_node(4)
G.add_node(5)
G.add_node(6)
G.add_node(7)
G.add_node(8)
G.add_node(9)

G.add_edge(0,4)
G.add_edge(0,5)
G.add_edge(0,6)
G.add_edge(0,7)
G.add_edge(0,8)
G.add_edge(0,9)

G.add_edge(1,4)
G.add_edge(1,5)
G.add_edge(1,6)
G.add_edge(1,7)
G.add_edge(1,8)
G.add_edge(1,9)

G.add_node(10)
G.add_node(11)
G.add_node(12)
G.add_node(13)
G.add_node(14)
G.add_node(15)

G.add_edge(10,4)
G.add_edge(10,5)

G.add_edge(11,5)
G.add_edge(11,6)

G.add_edge(12,4)
G.add_edge(12,6)

G.add_edge(13,7)
G.add_edge(13,8)

G.add_edge(14,8)
G.add_edge(14,9)

G.add_edge(15,7)
G.add_edge(15,9)



nx.draw(G, with_labels = True, node_size = 500)
plt.show()

nx.readwrite.adjlist.write_adjlist(G, ext + file + '.txt')