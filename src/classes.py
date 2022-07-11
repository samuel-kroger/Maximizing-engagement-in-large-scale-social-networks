import networkx as nx
import gurobipy as gp
import pretty_plot
import random
import os
import math
import rcm
import olak
import csv
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
		self.relax = relax
		self.prop_9 = prop_9
		self.prop_10 = prop_10

		self.prop_11_reduction = 0
		self.prop_11_run_time = 0
		self.prop_11_iterations = 0
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