import networkx as nx

G = nx.Graph()

G.add_node(0)
G.add_node(1)
G.add_node(2)
G.add_node(3)

G.add_edge(0,1)
G.add_edge(2,3)


print(nx.shortest_path_length(G, 0))
for node in [vertex for vertex in self.G.nodes() if vertex not in shortest_paths.key]