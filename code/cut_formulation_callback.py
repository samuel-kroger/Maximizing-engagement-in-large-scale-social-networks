import networkx as nx
import gurobipy as gp
import matplotlib.pyplot as plt

def cut_callback(m, where):

	if where == gp.GRB.Callback.MIPSOL:
		xvals = m.cbGetSolution(m._X)
		yvals = m.cbGetSolution(m._Y)
		svals = m.cbGetSolution(m._S)
		r = m._r
		G = m._G

		vbar = []
		vbar_complement = []
		not_in_min_cut = []

		for v in G.nodes():

			#find center j
			if svals[v] > 0.5:
				j = v

			#create v_bar
			if xvals[v] > 0.5 or yvals[v] > 0.5:
				vbar.append(v)
			else:
				vbar_complement.append(v)

		feasable = True
		shortest_paths = nx.shortest_path_length(G.subgraph(vbar), j)
		#print(shortest_paths)
		#print(shortest_paths.values())
		for value in shortest_paths.values():
			if value > r:
				feasable = False


		if feasable == False:
			for i in vbar:
				selected = vbar.copy()
				for c in vbar_complement:
					selected.append(c)
					sub_graph = G.subgraph(selected)



					try:
						if nx.shortest_path_length(sub_graph, j, i) > r:
							not_in_min_cut.append(c)

					except nx.NetworkXNoPath:
						not_in_min_cut.append(c)
					selected.remove(c)


				min_C = [c for c in vbar_complement if c not in not_in_min_cut]
				if i != j:
					m.cbLazy(m._S[j] + m._X[i] + m._Y[i] <= 1 + gp.quicksum(m._X[c] for c in min_C))
					#print('center: ', j)
					#print('vbar: ', vbar)
					#print('node: ', i)
					#print('RHS: ', min_C)
