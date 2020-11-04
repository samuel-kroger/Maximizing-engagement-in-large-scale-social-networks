import networkx as nx
import matplotlib.pyplot as plt
import gurobipy as grb
import numpy as np
import time

fname = "test_graph4.txt"
n = 100
erdos_constant = .01
b = 5
k = 3
iter_num = 1



def radius_bounded_anchored_k_core(graph, b, k, r, start_value):
	n = len(graph.nodes)
	model = grb.Model()
	model.setParam('OutputFlag', 1)

	# variables
	x = model.addVars(graph.nodes, vtype=grb.GRB.BINARY, name="x")
	if start_value != 'false':
		for i in range(len(start_value)):
			x[i].start = start_value[i]

	y = model.addVars(graph.nodes, vtype=grb.GRB.BINARY, name="y")
	s = model.addVars(graph.nodes, vtype=grb.GRB.BINARY, name="s")
	# objective function

	obj = grb.quicksum(x)
	model.setObjective(obj, sense=grb.GRB.MAXIMIZE)
	# constraints
	model.addConstr(grb.quicksum(y) <= b)
	for i in range(n):
		neighbors = [a for a in G.neighbors(i)]
		model.addConstr(grb.quicksum(x[i] for i in neighbors) + k * y[i] >= x[i] * k)

	model.addConstr(grb.quicksum(y) <= b)
	model.addConstr(grb.quicksum(s) == 1)
	for i in range(n):
		#model.addConstr(y[i] <= x[i])
		model.addConstr(s[i] <= x[i])
		for j in range(n):
			cuts = ab_seperators(graph, r, j, i)
			if G.has_edge(i,j) == False:
				model.addConstr(x[i] + s[j] <= 1 + grb.quicksum(x[c] for c in cuts))



	model.optimize()

	model.printAttr('x')
	tracker = []
	for v in model.getVars():
		if v.x == 1:
			tracker.append(int(v.varName[2:-1]))
	res = []
	[res.append(x) for x in tracker if x not in res]
	return(res)

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

def anc_kcore(graph, b, k, start_value):
	n = len(graph.nodes)
	model = grb.Model()
	model.setParam('OutputFlag', 0)

	# variables
	x = model.addVars(graph.nodes, vtype=grb.GRB.BINARY, name="x")
	if start_value != 'false':
		for i in range(len(start_value)):
			x[i].start = start_value[i]

	y = model.addVars(graph.nodes, vtype=grb.GRB.BINARY, name="y")
	# objective function

	obj = grb.quicksum(x)
	model.setObjective(obj, sense=grb.GRB.MAXIMIZE)
	# constraints
	model.addConstr(grb.quicksum(y) <= b)
	for i in range(n):
		neighbors = [a for a in G.neighbors(i)]

		model.addConstr(grb.quicksum(x[i] for i in neighbors) + k * y[i] >= x[i] * k)

	model.optimize()

	model.printAttr('x')
	tracker = []
	for v in model.getVars():
		if v.x == 1:
			tracker.append(int(v.varName[2:-1]))
	res = []
	[res.append(x) for x in tracker if x not in res]
	return(res)

def k_core_iter(G_org, k, anchors):
	G = G_org.copy()
	repeat = False
	for node in G.nodes:
		degree = G.degree
		if degree[node] < k and node not in anchors:
			G.remove_node(node)
			repeat = True
			break
	return G, repeat

def k_core(G_org, k, anchors = []):
	G = G_org.copy()
	repeat = True
	while repeat == True:
		G, repeat = k_core_iter(G, k, anchors)
	return (G)

def remove_core(G, k, anchors = []):
	G1 = G.copy()
	G2 = G.copy()
	G1 = k_core(G1, k, anchors)
	good_vert = G1.nodes
	for edge in G1.edges():
		G2.remove_edge(edge[0],edge[1])
	good_vert = list(good_vert)
	return G2, good_vert

def partition_into_R_and_S(G_org, ancored_verticies):
	G = G_org.copy()
	test = nx.algorithms.components.connected_components(G)
	R = []
	S = []
	for comp in test:
		if bool(comp.intersection(ancored_verticies)) == True:
			R.append(comp)
		else:
			S.append(comp)
	return [R, S]

def paper_algo(G_org, b):
	G = G_org.copy()
	G, anchored_verticies = remove_core(G, 2, [])
	anchor_tracker = anchored_verticies
	while b > 0:
		[R, S] = partition_into_R_and_S(G, anchored_verticies)
		v_1, v_1_value, path_1 = find_vertex_furthest_from_root(G, R, anchored_verticies)
		[G2, anchored_verticies] = remove_core(G_org, 2, [v_1])
		v_2, v_2_value, path_2 = find_vertex_furthest_from_root(G2, R, anchored_verticies)
		v_3, v_4, v_34_value, v_34_path = find_longest_path_over_trees(G2, S)
		if v_1_value + v_2_value > v_34_value or b == 1:
			if v_1 == None or v_1 in anchor_tracker:
				anchor_tracker.append(choose_unanchored_node_in_S(S, anchor_tracker))
			else:
				anchor_tracker.append(v_1)
				for vertex in path_1:
					anchor_tracker.append(vertex)

			b = b - 1
		else:
			if len(v_34_path) != 1:
				for vertex in v_34_path:
					anchor_tracker.append(vertex)
			else:
				anchor_tracker.append(v_3)
				anchor_tracker.append(v_4)
			b = b - 2
		G, anchored_verticies = remove_core(G, 2, anchor_tracker)
	G = k_core(G, 2, anchor_tracker)
	return G.nodes()

def choose_unanchored_node_in_S(S, anchored_list):
	for grouping in S:
		for node in grouping:
			if node not in anchored_list:
				return node

def find_vertex_furthest_from_root(G, R, anchores):
	i = 0
	opt_val = 0
	anchor = None
	path = []
	for set_of_verticies in R:
		subgraph = G.subgraph(set_of_verticies)
		for anc in anchores:
			if anc in set_of_verticies:
				d = nx.algorithms.shortest_paths.generic.shortest_path(subgraph, source = anc, weight = -1)
				for value in d.items():
					if len(value[1]) > opt_val:
						opt_val = len(value[1]) - 1
						anchor = value[1][-1]
						path = value[1]
				i = i+1
	return anchor, opt_val, path

def find_longest_path_over_trees(G, S):
	i = 0
	opt_val = 0
	v_34_path = []

	v_3 = None
	v_4 = None

	for set_of_verticies in S:
		subgraph = G.subgraph(set_of_verticies)
		d = nx.algorithms.shortest_paths.generic.shortest_path(subgraph, None, None, weight = -1)
		for key, value in d.items():
			for key_2, value_2 in value.items():
				if len(value_2) > opt_val:
					opt_val = len(value_2)
					v_3 = value_2[0]
					v_4 = value_2[-1]
					v_34_path = value_2
	return v_3, v_4, opt_val, v_34_path

def hamid_form(graph, b, k, start_value):
	n = len(graph.nodes)
	model = grb.Model()
	model.setParam('OutputFlag', 0)

	# variables
	x = model.addVars(graph.nodes, vtype=grb.GRB.BINARY, name="x")
	if start_value != 'false':
		for i in range(len(start_value)):
			x[i].start = start_value[i]

	y = model.addVars(graph.nodes, vtype=grb.GRB.BINARY, name="y")
	#z = model.addVars(graph.nodes, vtype = grb.GRB.BINARY, name = "z", lb = 0, ub = 1)
	# objective function

	obj = grb.quicksum(x)
	model.setObjective(obj, sense=grb.GRB.MAXIMIZE)
	# constraints
	model.addConstr(grb.quicksum(y) <= b)
	for i in range(n):
		neighbors = [a for a in G.neighbors(i)]

		model.addConstr(grb.quicksum(x[i] + y[i] for i in neighbors) >= x[i] * k)
		model.addConstr(x[i] >= y[i])

	model.optimize()

	model.printAttr('x')
	tracker = []
	for v in model.getVars():
		if v.X == 1:
			tracker.append(int(v.varName[2:-1]))
	res = []
	[res.append(x) for x in tracker if x not in res]
	return res

def ab_seperators(graph, radius, a, b):
	subgraph = nx.generators.ego.ego_graph(graph, a, radius = radius, center = True)
	cuts = set()
	if a in subgraph and b in subgraph:
		cuts = nx.algorithms.connectivity.cuts.minimum_node_cut(subgraph, s = a, t = b)
	return cuts









MIP_heur_time = 0
MIP_naive_time = 0
paper_time = 0
hamid_time = 0
hamid_heur_time = 0
time_inbetween = 0

for i in range(iter_num):
	G = nx.erdos_renyi_graph(n, erdos_constant)
	#G = read_graph(fname)
	time_1 = time.time()
	test = k_core(G, k)

	x = np.zeros(len(G))
	for i in range(len(x)):
		if i in test.nodes:
			x[i] = 1
	time_inbetween = time.time()
	MIP_heur = (anc_kcore(G, b, k, x))
	time_2 = time.time()

	time_3 = time.time()
	MIP_naive = (anc_kcore(G,b,k, 'false'))
	time_4 = time.time()
	time_5 = time.time()
	paper = list(paper_algo(G, b))
	time_6 = time.time()

	time_7 = time.time()
	hamid_solve = hamid_form(G, b, k, 'false')
	time_8 = time.time()
	time_9 = time.time()
	test = k_core(G, k)
	x = np.zeros(len(G))
	for i in range(len(x)):
		if i in test.nodes:
			x[i] = 1
	hamid_solve_heur = hamid_form(G, b, k, x)
	time_10 = time.time()






	MIP_heur_time += time_2 - time_1
	MIP_naive_time += time_4 - time_3
	paper_time += time_6 - time_5
	hamid_time += time_8 - time_7
	hamid_heur_time += time_10 - time_9

	if len(MIP_heur) != len(paper):
		print("PROBLEM1")

	if len(MIP_heur) != len(MIP_naive):
		print("problem2")

	if len(MIP_heur) != len(hamid_solve):
		print("problem3")
		print(len(MIP_heur))
		print(len(hamid_solve))


	if len(MIP_heur) != len(hamid_solve_heur):
		print("problem4")



MIP_heur_time = MIP_heur_time/iter_num
MIP_naive_time = MIP_naive_time/iter_num
paper_time = paper_time/iter_num
hamid_time = hamid_time/iter_num
hamid_heur_time = hamid_heur_time/iter_num


print('Sam_heur')
print(MIP_heur_time)
print('Sam_naive')
print(MIP_naive_time)
print('paper')
print(paper_time)
print(time_inbetween - time_1)
print('hamid_naive')
print(hamid_time)
print('hamid_heur')
print(hamid_heur_time)




