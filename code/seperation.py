import gurobipy as gp
import networkx as nx
import heuristic
import time

def conflict_callback(m, where):
	time1 = time.time()
	if where == gp.GRB.Callback.MIPSOL:
		xvals = m.cbGetSolution(m._X)
		yvals = m.cbGetSolution(m._Y)
		anchors = []
		core_nodes = []
		G = m._G
		k = m._k
		b = m._b

		for y in yvals.keys():
			if yvals[y] > 0.5:
				anchors.append(y)
		for x in xvals.keys():
			if xvals[x] > 0.5:
				core_nodes.append(x)

		induced_k_core = heuristic.anchored_k_core(G, k, anchors)



		for j in G.nodes() - induced_k_core:
			if j in core_nodes and len(anchors) != 0:
				#print('anchors: ', anchors)
				#print('core_nodes: ', core_nodes)
				#print('induced_k_core: ', induced_k_core)
				#print('j: ', j)
				m.cbLazy(gp.quicksum(m._Y[i] for i in anchors) + m._X[j] <= len(anchors))
				time2 = time.time()

				print('callback time: ', time2 - time1)


