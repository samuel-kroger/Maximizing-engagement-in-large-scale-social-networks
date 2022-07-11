import networkx as nx
import gurobipy as gp
import pretty_plot
#import matplotlib.pyplot as plt
import random
import fractional_callback
#import seperation
import os
import math
import rcm
import olak
import csv
import cut_formulation_callback
import extended_cut_formulation_callback
import itertools
import time

def read_graph(fname):
	if fname.endswith('mtx'):
		edges = []

		with open(fname, 'r') as f:
			reader = csv.reader(f, delimiter=' ')
			edges = [row for row in reader if len(row) == 2]
			f.close()

		graph = nx.Graph()
		graph.add_edges_from(edges, nodetype=int)

	else:
		graph = nx.read_edgelist(fname, nodetype=int, data=(("Type", str),))

	graph.remove_edges_from(nx.selfloop_edges(graph))
	graph.remove_nodes_from(list(nx.isolates(graph)))

	print(nx.info(graph))

	return graph

def output_sort(element_of_output):
	if element_of_output == "instance_name":
		return 1
	if element_of_output == "model_type":
		return 2
	if element_of_output == "n":
		return 3
	if element_of_output == "m":
		return 4
	if element_of_output == "k":
		return 5
	if element_of_output == "b":
		return 6
	if element_of_output == "r":
		return 7
	if element_of_output == "branch_and_bound_nodes":
		return 8
	if element_of_output == "LP":
		return 9
	if element_of_output == "BBnodes":
		return 10
	if element_of_output == "var_num":
		return 11
	if element_of_output == "num_k_core_nodes":
		return 12
	if element_of_output == "lower_bound":
		return 13
	if element_of_output == "upper_bound":
		return 14
	if element_of_output == "warm_start":
		return 11
	if element_of_output == "prop_8":
		return 18
	if element_of_output == "num_prop_8_inequalties_added":
		return 19
	if element_of_output == "prop_8_comp_time":
		return 20
	if element_of_output == "prop_9":
		return 21
	if element_of_output == "num_prop_9_inequalties_added":
		return 22
	if element_of_output == "prop_9_comp_time":
		return 23
	if element_of_output == "num_prop_10_fixings":
		return 24
	if element_of_output == "prop_10":
		return 25
	if element_of_output == "prop_10_comp_time":
		return 26
	if element_of_output == "prop_11_reduction":
		return 27
	if element_of_output == "prop_11_iterations":
		return 28
	if element_of_output == "prop_11_run_time":
		return 29
	if element_of_output == "time_for_warm_start":
		return 30
	if element_of_output == "warm_start":
		return 31
	if element_of_output == "num_additonal_constraints":
		return 32
	if element_of_output == "relax":
		return 33
	if element_of_output == "fractional_callback":
		return 34

def anchored_k_core (G, k, purchased_nodes):
	anchored_core_nodes = []
	anchored_k_core_decomp = olak.anchoredKCore(G, purchased_nodes)
	for key in anchored_k_core_decomp:
		if anchored_k_core_decomp[key] >= k:
			anchored_core_nodes.append(key)
	return (anchored_core_nodes)

class base_model(object):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11):
		self.model = gp.Model()
		self.model_type = model_type
		self.instance_name = instance_name
		#Gurobi paramater options
		self.model.setParam('OutputFlag', 1)
		self.model.setParam('MIPGap', 0)
		self.model.Params.timeLimit = 3600
		self.model.params.LogToConsole = 1
		self.model.params.LogFile = '../results/logs/log_' + instance_name +'_' + str(k) + '_' +  str(b) + "_"+ filename[:-4] + '.log'

		self.prop_8 = prop_8
		self.fractional_callback = fractional_callback
		self.relax = relax
		self.prop_9 = prop_9
		self.prop_10 = prop_10

		self.prop_11_reduction = 0
		self.prop_11_run_time = 0
		self.prop_11_iterations = 0
		#HHHHHHHHHHHHHHHHHHHH
		self.warm_start = warm_start

		#every member of class
		self.num_k_core_nodes = 0

		#Set up constants
		self.filename = filename
		self.k = k
		self.b = b
		self.r = r
		self.BBnodes = "NA"

		#Set up G
		self.G = G
		self.n = len(G.nodes())
		self.m = len(G.edges())

		self.var_num = 2 * self.n
		self.x_vals = []
		self.y_vals = []

		for node in self.G.nodes():
			if self.G.degree(node)>= self.k:
				self.x_vals.append(node)
			else:
				self.y_vals.append(node)

		if prop_9:
			if b < k:
				self.remove_all_y_saturated_nodes()

		#set up model
		self.model._G = G
		self.model._b = b
		self.model._k = k
		self.model._R = G.nodes()
		self.model._r = r

		if relax:
			self.model._X = self.model.addVars(self.G.nodes(), vtype=gp.GRB.CONTINUOUS, name="x", ub = 1, lb = 0)
			self.model._Y = self.model.addVars(self.G.nodes(), vtype=gp.GRB.CONTINUOUS, name="y", ub = 1, lb = 0)
		else:
			self.model._X = self.model.addVars(self.G.nodes(), vtype=gp.GRB.BINARY, name="x")
			self.model._Y = self.model.addVars(self.G.nodes(), vtype=gp.GRB.BINARY, name="y")


		if self.prop_10:
			time1 = time.time()
			counter = 0

			for v in self.G.nodes():
				self.G.nodes[v]["y_fixable"] = True

			for v in self.x_vals:
				for u in self.G.neighbors(v):
					self.G.nodes[u]["y_fixable"] = False

			for v in self.G:
				if self.G.nodes[v]["y_fixable"]:
					self.model._Y[v].ub = 0
					counter += 1
			time2 = time.time()

			self.num_prop_10_fixings = counter
			self.prop_10_comp_time = time2 - time1

		self.model.setObjective(gp.quicksum(self.model._X), sense=gp.GRB.MAXIMIZE)

		if self.model_type != "reduced_model":
			self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in self.G.nodes())

		if self.model_type != "reduced_model":
			self.model.addConstrs(self.model._X[i] + self.model._Y[i] <= 1 for i in G.nodes())

		if self.model_type != "reduced_model":
			self.model.addConstr(gp.quicksum(self.model._Y) <= self.b)

	def remove_all_y_saturated_nodes(self):

		loop = True
		while loop:
			old_tracker = self.prop_11_reduction
			self.y_saturated_iter()
			if old_tracker == self.prop_11_reduction:
				loop = False

	def y_saturated_iter(self):

		time1 = time.time()
		num_y_saturated_nodes = 0
		temp_graph = self.G.subgraph(self.x_vals)
		for v in temp_graph:
			if self.k - temp_graph.degree(v) > self.b:
				self.y_vals.append(v)
				self.x_vals.remove(v)

				num_y_saturated_nodes += 1
		time2 = time.time()

		self.prop_11_reduction += num_y_saturated_nodes
		self.prop_11_run_time += time2 - time1
		self.prop_11_iterations += 1

	def RCM_warm_start(self):

		self.warm_start = True
		r = rcm.RCM(self.G, self.k, self.b)
		a, f = r.findAnchors(False)

		r.findAnchors(False)
		a_list = list(a)

		anc_k_core = anchored_k_core(self.G, self.k, a_list)


		for v in a_list:
			self.model._Y[v].start = 1
		for v in anc_k_core:
			self.model._X[v].start = 1

	def OLAK_warm_start(self):

		self.warm_start = True
		k_core = list(nx.k_core(self.G, self.k))

		olak_time_start = time.time()
		olak_output = list(olak.olakAnchors(self.G, olak.anchoredKCore(self.G), self.k, self.b))

		olak_anchors = [element for element in olak_output if element not in k_core]

		anc_k_core = anchored_k_core(self.G, self.k, olak_anchors)

		olak_time_end = time.time()

		for v in olak_anchors:
			self.model._Y[v].start = 1
		for v in anc_k_core:
			self.model._X[v].start = 1

	def optimize(self):
		G = self.G
		k = self.k
		b = self.b
		m = self.model

		#HHHHHHHHHHHHHHHHHHHHHHHHHH
		if self.fractional_callback:
			m.Params.lazyConstraints = 1

			#m.optimize(seperation.conflict_callback)
			m.optimize(fractional_callback.fractional_callback)
		else:
			m.optimize()


		self.BBnodes = m.NodeCount

		#if not self.relax:
		#if self.relax != True:
		self.upper_bound = m.objBound
		self.lower_bound = m.objVal

	def print_model(self):

		G = self.G
		k = self.k
		b = self.b
		m = self.model

		display = True
		if display:
			if m.status == gp.GRB.OPTIMAL or m.status == gp.GRB.TIME_LIMIT:

				cluster = [i for i in G.nodes if m._X[i].x > 0.5 or m._Y[i].x > 0.5]
				SUB = G.subgraph(cluster)

				#HHHHHHHHHHHHHHHHHHH
				root = -1

				for i in G.nodes:
					if self.model_type != 'base_model' and self.model_type != 'reduced_model':
						if m._S[i].x > 0.5:
							print("Root is ", i)
							root = i
				#HHHHHHHHHHHHHHHHHHHH

				selected_nodes = []
				for i in G.nodes:
					if m._X[i].x > 0.5:
						print("selected node: ", i)
						selected_nodes.append(i)

				purchased_nodes = []
				for i in G.nodes:
					if m._Y[i].x > 0.5:
						purchased_nodes.append(i)
						print("purchased node: ", i)

				plot = 1
				if plot == 1:
					pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, True, k, b, self.r)
				if plot == 2:
					pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, False, k, b, self.r)

	def save_to_file(self, total_time):

		if not os.path.exists("../results/" + self.filename):
			with open("../results/" + self.filename, "w") as doc:
				string = ""
				for thing in self.return_output():
					string += thing + ", "
				string += 'total_time'
				doc.write(string)
				doc.close()

		with open("../results/" + self.filename, "a") as doc:
			string = "\n"
			for thing in self.return_output():
				if type(getattr(self, thing)) == float:
					string += str(round(getattr(self, thing), 2)) + ", "
				else:
					string += str(getattr(self, thing)) + ", "
			string += total_time
			doc.write(string)
			doc.close()

	def return_output(self):

		exceptions = ['G', 'R', 'model', 'x_vals', 'y_vals', 'time_for_warm_start', 'filename']
		output = [attribute for attribute in dir(self) if not attribute.startswith("__") and not callable(getattr(self, attribute)) and attribute not in exceptions]
		output.sort(key = output_sort)

		return output


class reduced_model(base_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11):
		base_model.__init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11)

		for y_val in self.y_vals:
			self.model._X[y_val].ub = 0
			self.var_num -= 1

		k_core_G = nx.k_core(self.G, self.k)
		self.num_k_core_nodes = len(k_core_G.nodes())
		self.R = list(self.G.nodes() - k_core_G.nodes())
		non_k_core_subgraph = self.G.subgraph(self.R)

		if self.prop_8:

			time1 = time.time()
			counter = 0
			for v in self.x_vals:
				if self.G.degree(v) == self.k:
					for u in self.G.neighbors(v):
						if u in k_core_G.nodes():
							continue
						counter +=1
						facet_defining_constraint = self.model.addConstr(self.model._X[v] <= self.model._Y[u] + self.model._X[u])
						#facet_defining_constraint.lazy = 3
			time2 = time.time()

			self.num_prop_8_inequalties_added = counter
			self.prop_8_comp_time = time2 - time1

		if self.prop_9:

			time1 = time.time()
			counter = 0

			for u in self.y_vals:

				u_path_length_dict = nx.single_source_dijkstra_path_length(non_k_core_subgraph, u, 2)
				u_neigbors = set(non_k_core_subgraph.neighbors(u))

				for v in u_path_length_dict:

					v_neighbors = set(non_k_core_subgraph.neighbors(v)) - {u}

					if u_neigbors - {v} < v_neighbors:

						self.model.addConstr(self.model._X[v] + self.model._Y[v] >= self.model._Y[u])
						counter+=1

			time2 = time.time()
			self.num_prop_9_inequalties_added = counter
			self.prop_9_comp_time = time2 - time1

		constraint_index = list(self.x_vals - k_core_G.nodes())

		for node in k_core_G.nodes():

			self.model._X[node].lb = 1
			self.model._Y[node].ub = 0
			self.var_num -= 2

		deg_constraints = self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in constraint_index)

		self.model.addConstrs(self.model._X[i] + self.model._Y[i] <= 1 for i in constraint_index)

		self.model.addConstr(gp.quicksum(self.model._Y[i] for i in self.R) <= self.b )


class radius_bounded_model(base_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11):
		base_model.__init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11)
		self.model._S = self.model.addVars(self.G.nodes, vtype=gp.GRB.BINARY, name="s")
		#radius_bounded_model.dominated_fixing_idea_power_graph_sam(self)
		self.model.addConstr(gp.quicksum(self.model._S) == 1)
		for i in self.G.nodes():
			self.model._S[i].BranchPriority = 1

	def warm_start_one(self):

		SUB = nx.k_core(self.G, self.k)

		list_of_connected_nodes = []
		for connected_nodes in nx.connected_components(SUB):
			list_of_connected_nodes.append(connected_nodes)

		list_of_connected_nodes.sort(key=len, reverse=True)

		for connected_nodes in list_of_connected_nodes:
			connected_component = SUB.subgraph(connected_nodes)
			#for node in connected_component:
			for node in connected_component:

				if nx.eccentricity(connected_component, node) <= self.r:

					for v in connected_component:
						self.model._X[v].start = 1
					self.model._S[node].start = 1
					return

	def center_fixing_idea(self):
		simplicials = []

		for vertex in self.G.nodes():
			neighbor_set = list(self.G.neighbors(vertex))
			induced_subgraph = self.G.subgraph(neighbor_set)
			n = induced_subgraph.number_of_nodes()
			m = induced_subgraph.number_of_edges()
			if m == n*(n-1)/2: simplicials.append(vertex)

		subgraph_of_simplicials = self.G.subgraph(simplicials)
		print("Number of independent simplicials: ", nx.number_connected_components(subgraph_of_simplicials))

	def center_fixing_idea_recursive(self):

		#self.G = nx.cycle_graph(4)
		for n in self.G.nodes():
			self.G.nodes[n]['can_be_center'] = 1
		#simplicials = []

		for i in range(self.r):
			fix = []
			print("iteration: ", i)

			sub_graph_nodes = [node for node in self.G.nodes() if self.G.nodes[node]['can_be_center'] == 1]
			SUB = self.G.subgraph(sub_graph_nodes)

			for vertex in SUB:
				#simplicial fix
				neighbor_set = list(SUB.neighbors(vertex))
				induced_subgraph = SUB.subgraph(neighbor_set)
				n = induced_subgraph.number_of_nodes()
				m = induced_subgraph.number_of_edges()
				if m == n*(n-1)/2:
					fix.append(vertex)
				'''
				#degree 2 fix
				if SUB.degree(vertex) == 2:
					neighbors = [vertex for vertex in SUB[vertex]]
					common_neigbors = [n for n in nx.common_neighbors(SUB, neighbors[0], neighbors[1])]
					if len(common_neigbors) > 1:
						fix.append(vertex)

				#degree 3 fix
				if SUB.degree(vertex) == 3:
					TINY_SUB = SUB.subgraph([vertex for vertex in SUB[vertex]])
					tiny_m = TINY_SUB.number_of_edges()
					#common_neigbors = [n for n in nx.common_neighbors(SUB, neighbors[0], neighbors[1])]
					if tiny_m == 2:
						fix.append(vertex)
				'''
			print(len(fix))

			for n in fix:
				self.G.nodes[n]['can_be_center'] = 0

			if len(fix) == 0:
				for n in [node for node in self.G.nodes if self.G.nodes[node]['can_be_center'] == 0]:
					self.model._S[n].ub = 0
				return

		for vertex in [node for node in self.G.nodes if self.G.nodes[node]['can_be_center'] == 0]:
			self.model._S[vertex].ub = 0
		return
		#subgraph_of_simplicials = G.subgraph(simplicials)
		#print("Number of independent simplicials: ", nx.number_connected_components(subgraph_of_simplicials))

	def dominated_fixing_idea(self):
		#DO FOR POWER GRAPH G_R
		power_graph = self.G
		counter = 0
		time1 = time.time()
		for node in power_graph.nodes():
			power_graph.nodes[node]["root_fixed"] = False
		for u,v in itertools.combinations(power_graph.nodes(), 2):
			common_neighbors = set(nx.common_neighbors(power_graph, u, v))
			if common_neighbors == [] or power_graph.nodes[u]["root_fixed"] == True or power_graph.nodes[v]["root_fixed"] == True:
				continue

			u_neigbors = set(power_graph.neighbors(u)) - {v}
			v_neighbors = set(power_graph.neighbors(v)) - {u}

			if u_neigbors == common_neighbors:
				power_graph.nodes[u]["root_fixed"] = True
				self.model._S[u].ub = 0
				#print("u is fixed")
				#print("vertex u: ",u)
				#print("vertex v: ",v)
				#print("u_neighbors: ",u_neigbors)
				#print("v_neighbors: ",v_neighbors)
				#print("common_neighbors: ",common_neighbors)
				counter+=1
			if v_neighbors == common_neighbors:
				power_graph.nodes[v]["root_fixed"] = True
				self.model._S[v].ub = 0
				#print("v is fixed")
				#print("vertex u: ",u)
				#print("vertex v: ",v)
				#print("u_neighbors: ",u_neigbors)
				#print("v_neighbors: ",v_neighbors)
				#print("common_neighbors: ",common_neighbors)
				counter+=1
		time2 = time.time()
		print("Number of centers fixed ", counter, " out of ", len(power_graph.nodes()), " nodes in ", time2  - time1, "seconds.")

		if not os.path.exists("../results/radius_bounded/" + self.filename):
			with open("../results/radius_bounded/" + self.filename, "w") as doc:
				string = "Instance, k, r, n, number fixed, fixing time"
				doc.write(string)
				doc.close()

		with open("../results/radius_bounded/" + self.filename, "a") as doc:
			string = "\n" + self.instance_name + ", " + str(self.k) + ", " + str(self.r) + ", " + str(self.n) + ", " + str(counter) + ", " + str(time2 - time1)
			doc.write(string)
			doc.close()

	def dominated_fixing_idea_power_graph(self):
		#DO FOR POWER GRAPH G_R
		power_graph = nx.power(self.G, self.r)
		common_neighbor_possiblity_power_graph = nx.power(power_graph, 2)
		counter = 0
		time1 = time.time()
		for node in power_graph.nodes():
			power_graph.nodes[node]["root_fixed"] = False
		for u,v in itertools.combinations(power_graph.nodes(), 2):
			if power_graph.nodes[u]["root_fixed"] == True or power_graph.nodes[v]["root_fixed"] == True:
				continue
			if (u,v) not in common_neighbor_possiblity_power_graph.edges():
				continue
			common_neighbors = set(nx.common_neighbors(power_graph, u, v))
			if common_neighbors == []:
				continue

			u_neigbors = set(power_graph.neighbors(u)) - {v}
			v_neighbors = set(power_graph.neighbors(v)) - {u}

			if u_neigbors == common_neighbors:
				power_graph.nodes[u]["root_fixed"] = True
				self.model._S[u].ub = 0
				#print("u is fixed")
				#print("vertex u: ",u)
				#print("vertex v: ",v)
				#print("u_neighbors: ",u_neigbors)
				#print("v_neighbors: ",v_neighbors)
				#print("common_neighbors: ",common_neighbors)
				counter+=1
			if v_neighbors == common_neighbors:
				power_graph.nodes[v]["root_fixed"] = True
				self.model._S[v].ub = 0
				#print("v is fixed")
				#print("vertex u: ",u)
				#print("vertex v: ",v)
				#print("u_neighbors: ",u_neigbors)
				#print("v_neighbors: ",v_neighbors)
				#print("common_neighbors: ",common_neighbors)
				counter+=1
		time2 = time.time()
		print("Number of centers fixed ", counter, " out of ", len(power_graph.nodes()), " nodes in ", time2  - time1, "seconds.")

		if not os.path.exists("../results/radius_bounded/" + self.filename):
			with open("../results/radius_bounded/" + self.filename, "w") as doc:
				string = "Instance, k, r, n, number fixed, fixing time"
				doc.write(string)
				doc.close()

		with open("../results/radius_bounded/" + self.filename, "a") as doc:
			string = "\n" + self.instance_name + ", " + str(self.k) + ", " + str(self.r) + ", " + str(self.n) + ", " + str(counter) + ", " + str(time2 - time1)
			doc.write(string)
			doc.close()

	def dominated_fixing_idea_power_graph_sam(self):
		#DO FOR POWER GRAPH G_R
		power_graph = nx.power(self.G, self.r)

		counter = 0
		time1 = time.time()
		for node in power_graph.nodes():
			power_graph.nodes[node]["root_fixed"] = False


		for node in power_graph:
			#print("node", node)
			if power_graph.nodes[node]["root_fixed"] == True:
				continue
			node_neighbors = set(power_graph.neighbors(node))
			for neighbor in self.G.neighbors(node):
				#print("neighbor_node", neighbor)
				if power_graph.nodes[neighbor]["root_fixed"] == True:
					continue
				neighbor_neighbors = set(power_graph.neighbors(neighbor)) - {node}

				if neighbor_neighbors.issubset(node_neighbors - {neighbor}):
					if power_graph.nodes[neighbor]["root_fixed"] == False:
						power_graph.nodes[neighbor]["root_fixed"] = True
						self.model._S[neighbor].ub = 0
						counter += 1
					else:
						#print("AHHHHHHHHHHHHHHHH")
						''

				if (node_neighbors - {neighbor}).issubset(neighbor_neighbors):
					if power_graph.nodes[node]["root_fixed"] == False:
						power_graph.nodes[node]["root_fixed"] = True
						self.model._S[node].ub = 0
						counter += 1
					else:
						#print("BBBBBBBBBBBBBBBBBBBBBBBBB")
						#print("node", node)
						#print("neighbor", neighbor)
						#print("node_neighbors", node_neighbors - {neighbor})
						#print("neighbor_neighbors", neighbor_neighbors)
						''
			#print(counter)
		time2 = time.time()
		print("Number of centers fixed ", counter, " out of ", len(power_graph.nodes()), " nodes in ", time2  - time1, "seconds.")
		'''
		if not os.path.exists("../results/radius_bounded/" + self.filename):
			with open("../results/radius_bounded/" + self.filename, "w") as doc:
				string = "Instance, k, r, n, number fixed, fixing time"
				doc.write(string)
				doc.close()

		with open("../results/radius_bounded/" + self.filename, "a") as doc:
			string = "\n" + self.instance_name + ", " + str(self.k) + ", " + str(self.r) + ", " + str(self.n) + ", " + str(counter) + ", " + str(time2 - time1)
			doc.write(string)
			doc.close()
		'''


class vermyev_model(radius_bounded_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11):
		radius_bounded_model.__init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11)

		DG = nx.DiGraph(self.G) # bidirected version of G
		L = range(1, self.r + 1)
		self.model._w = self.model.addVars(DG.nodes,DG.nodes, L, vtype=gp.GRB.BINARY, name = "w")


		# coupling constarints
		self.model.addConstrs(self.model._S[i] <= self.model._X[i] + self.model._Y[i] for i in self.G.nodes())
		for i in self.G.nodes:
			for j in self.G.nodes:
				for l in L:
					if i == j:
						self.model._w[i,j,l].ub = 0

					if l < nx.shortest_path_length(self.G, i, j):
							self.model._w[i,j,l].ub = 0


		for i in self.G.nodes:
			for j in self.G.nodes:
				if i != j:
					possible_ls = range(nx.shortest_path_length(self.G, i, j), self.r + 1)

					self.model.addConstr(self.model._X[i] + self.model._Y[i] + self.model._S[j] <= 1 + gp.quicksum(self.model._w[i,j,l] for l in possible_ls))

					for l in possible_ls:
						#self.model.G.addConstr(self.model.G._w[i,j,l] <= self.model.G._S[j])
						if l > 1:
							self.model.addConstr(self.model._w[i,j,l] <= gp.quicksum(self.model._w[i,u, l-1] for u in self.G.neighbors(j)))

						#m.addConstr(m._X[i] + m._Y[i] + m._w[i,j, l] <= 1 + m._S[j])


class cut_model(radius_bounded_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11):
		radius_bounded_model.__init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11)


		#allow lazy constraints
		self.model.Params.lazyConstraints = 1

		#Add center variable

		#Center must be active constraint
		self.model.addConstrs(self.model._S[i] <= self.model._Y[i] + self.model._X[i] for i in self.G.nodes())


		#temp_idea
		#self.model.addConstr(gp.quicksum(self.model._X[i] for i in self.G.nodes())<= 2533 )

		#initial constraint
		for i in self.G.nodes():
			shortest_paths = nx.shortest_path_length(self.G, i)
			for j in self.G.nodes():
				if j not in shortest_paths.keys():
					self.model.addConstr(self.model._X[j] + self.model._Y[j] + self.model._S[i] <= 1)
					self.model.addConstr(self.model._X[i] + self.model._Y[i] + self.model._S[j] <= 1)

			for key, value in shortest_paths.items():
				if value > r:
					self.model.addConstr(self.model._X[i] + self.model._Y[i] + self.model._S[key] <= 1)
					self.model.addConstr(self.model._X[key] + self.model._Y[key] + self.model._S[i] <= 1)


	def optimize(self):
		G = self.G
		k = self.k
		b = self.b


		self.model.optimize(cut_formulation_callback.cut_callback)

		#model.optimize()
		var = self.model.getVars()
		#print(var)


		#if not self.relax:
		self.upper_bound = self.model.objBound
		self.lower_bound = self.model.objVal

class extended_cut_model(cut_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11):
		cut_model.__init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11)

		self.model._Z = self.model.addVars(self.G.nodes(), self.G.nodes, vtype = gp.GRB.BINARY, name = 'z')

		self.model.addConstrs(self.model._X[i] + self.model._Y[i] + self.model._S[j] <= 1 + self.model._Z[i,j] for i in G.nodes() for j in G.nodes())

		self.model.addConstrs(self.model._Z[i,j] <= self.model._X[i] + self.model._Y[i] for i in G.nodes() for j in G.nodes())

	def optimize(self):
		G = self.G
		k = self.k
		b = self.b
		m = self.model

		m.optimize(extended_cut_formulation_callback.extended_cut_callback)

		#model.optimize()
		#print(var)


		#if not self.relax:
		self.upper_bound = m.objBound
		self.lower_bound = m.objVal

class flow_model(radius_bounded_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11):
		radius_bounded_model.__init__(self, filename, instance_name, G, model_type, k, b, r, relax, warm_start, prop_8, prop_9, prop_10, prop_11)
		m = self.model
		DG = nx.DiGraph(G) # bidirected version of G

		m._F = m.addVars(DG.nodes,DG.edges,vtype=gp.GRB.CONTINUOUS, name = "f")

		#m._Gen = m.addVars(DG.nodes,DG.nodes,vtype=GRB.CONTINUOUS, name = "g")
		P = nx.power(G,r)

		DP = nx.DiGraph(P)

		# coupling constarints
		m.addConstrs(m._S[i] <= m._X[i] + m._Y[i] for i in G.nodes)

		# flow conservation
		for i in G.nodes:
			for j in G.nodes:
				if i != j:
					m.addConstr(gp.quicksum(m._F[j,i,u] for u in G.neighbors(i)) <= r * (m._X[i] + m._Y[i] - m._S[i]))
					#m.addConstr(gp.quicksum(m._F[j,u,i] for u in G.neighbors(i)) <= (r) * (m._X[i] + m._Y[i] - m._S[i]))
					if nx.shortest_path_length(G, i,j) <= r:
						m.addConstr( gp.quicksum(m._F[j,u,i] for u in G.neighbors(i)) - gp.quicksum(m._F[j,i,u] for u in G.neighbors(i)) <= m._X[i] + m._Y[i])
						m.addConstr( gp.quicksum(m._F[j,u,i] for u in G.neighbors(i)) - gp.quicksum(m._F[j,i,u] for u in G.neighbors(i)) >= m._S[i])


					#m.addConstr( gp.quicksum(F[j,u,i] for u in DG.neighbors(i)) <= r * (1 - m._S[i]))
					#m.addConstr( gp.quicksum(m._F[j,i,u] for u in G.neighbors(j)) <= r * (m._X[i] + m._Y[i] - m._S[i]))
			#m.addConstr( gp.quicksum(m._F[j,j,u] for u in G.neighbors(j)) >= m._X[j] + m._Y[j] - m._S[j])
			#m.addConstr( gp.quicksum(m._F[j,u,i] for u in G.neighbors(i)) == 0)

		# valid inequalities

		for i in G.nodes:
			for j in G.nodes:
				if i!=j and (i,j) not in DP.edges:
					m.addConstr(m._X[i] + m._Y[i] + m._S[j] <= 1)




	    #m.addConstrs( m._Gen[i,j] + gp.quicksum(F[i,u,j] for u in DG.neighbors(j)) - gp.quicksum(F[i,j,u] for u in DG.neighbors(j)) == m._X[j] - m._S[j] for (i,j) in DP.edges)

