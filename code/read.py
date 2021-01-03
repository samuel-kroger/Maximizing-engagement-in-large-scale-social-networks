############
# Read Graph (by Logan Smith)
############
import networkx as nx

# Logan's code for reading Graphs
def imp_dimacs(fname) :
    with open(fname, "r") as f:
        n, m, _ = f.readline().strip().split()
        n = int(n)
        m = int(m)
        edges = [None for _ in range(m)]
        i = 0
        for index in range(n):
            line = f.readline().strip().split()
            for v in line :
                if index+1 < int(v) :
                    edges[i] = (index+1, int(v))
                    i += 1
    G = nx.empty_graph(n+1)
    G.remove_node(0)
    G.add_edges_from(edges)
    return G

# Sam's code for reading graphs
def read_graph(fname):
	with open(fname, "r") as f:
		m = int(f.readline().strip().split()[-1])
		edges = [None for _ in range(m)]
		for index in range(m):
			line = f.readline().strip().split()
			u, v = int(line[0]) - 1, int(line[1]) - 1
			edges[index] = (u, v)
		G = nx.Graph()
		G.add_edges_from(edges)
	return(G)