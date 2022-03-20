import networkx as nx
import gurobipy as gp
import heuristic
import pretty_plot
import matplotlib.pyplot as plt
import time
import random
import fractional_callback
import seperation
import os
import math
import rcm

def output_sort(element_of_output):
	if element_of_output == "instance_name":
		return 1
	if element_of_output == "model_type":
		return 2
	if element_of_output == "k":
		return 3
	if element_of_output == "b":
		return 4
	if element_of_output == "r":
		return 5
	if element_of_output == "var_num":
		return 5.5
	if element_of_output == "var_remaining":
		return 5.7
	if element_of_output == "num_k_core_nodes":
		return 6
	if element_of_output == "lower_bound":
		return 6.3
	if element_of_output == "upper_bound":
		return 6.6
	if element_of_output == "remove_y_edges_reduction":
		return 7
	if element_of_output == "remove_y_edges_time":
		return 8
	if element_of_output == "y_saturated_reduction":
		return 9
	if element_of_output == "y_saturated_iterations":
		return 10
	if element_of_output == "y_saturated_run_time":
		return 11
	if element_of_output == "time_for_warm_start":
		return 12
	if element_of_output == "y_continuous":
		return 13
	if element_of_output == "additonal_facet_defining":
		return 14
	if element_of_output == "y_val_fix":
		return 15
	if element_of_output == "fractional_callback":
		return 16


class base_model(object):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated, y_continuous, additonal_facet_defining, y_val_fix, fractional_callback):

		self.model = gp.Model()
		self.model_type = model_type
		self.instance_name = instance_name
		#Gurobi paramater options
		self.model.setParam('OutputFlag', 1)
		self.model.Params.timeLimit = 3600
		self.model.params.LogToConsole = 1
		self.model.params.LogFile = '../results/logs/log_' + filename +'_' + str(k) + '_' +  str(b) + '.log'

		self.y_continuous = y_continuous
		self.additonal_facet_defining = additonal_facet_defining
		self.y_val_fix = y_val_fix
		self.fractional_callback = fractional_callback
		#REVISIT
		#self.model.params.method = 3
		#self.relax = False

		#every member of class
		self.num_k_core_nodes = 0
		self.R = []
		#self.weights = {}
		self.var_remaining = 0
		self.var_num = 0

		#y_saturated
		self.y_saturated_reduction = 0
		self.y_saturated_run_time = 0
		self.y_saturated_iterations = 0

		self.remove_y_edges_reduction = 'NA'
		self.remove_y_edges_time = 'NA'

		#Set up constants
		self.filename = filename
		self.k = k
		self.b = b
		self.r = r

		#warm_start
		#self.time_for_warm_start = 60

		#Set up G
		self.G = G

		self.x_vals = []
		self.y_vals = []

		for node in self.G.nodes():
			if self.G.degree(node)>= self.k:
				self.x_vals.append(node)
			else:
				self.y_vals.append(node)

		if y_saturated:
			if b < k:
				self.remove_all_y_saturated_nodes()

		#set up model
		self.model._G = G
		self.model._b = b
		self.model._k = k
		self.model._R = G.nodes()
		self.model._r = r

		self.model._X = self.model.addVars(self.G.nodes(), vtype=gp.GRB.BINARY, name="x")

		if y_continuous:
			self.model._Y = self.model.addVars(self.G.nodes(), vtype=gp.GRB.CONTINUOUS, name="y")
		else:
			self.model._Y = self.model.addVars(self.G.nodes(), vtype=gp.GRB.BINARY, name="y")


		# objective function 
		self.model.setObjective(gp.quicksum(self.model._X), sense=gp.GRB.MAXIMIZE)

		# k degree constraints
		'''
		if self.k == 2:

			for v in self.G.nodes():
				if self.G.degree(v) == 1:
					for u in G.neighbors(v):
						self.model.addConstr(self.model._Y[v] <= self.model._X[u])

				else:
					self.model._Y[v].ub = 0
						#self.model.addConstr(self.model._X[v] == self.model._Y[u])
						#self.model._X[u].lb = 1
				#if self.G.degree(v) == 1:
				#	for u in G.neighbors(v):
				#		self.model._X[u].lb = 1
			leaf_nodes = [x for x in self.G.nodes() if self.G.degree(x) == 1]
			#print(leaf_nodes)
			for i in leaf_nodes:
				for j in leaf_nodes:
					if i != j:
						paths = nx.all_simple_paths(self.G, i, j)
						for path in paths:
							print(path)
							#print(path[0])
							#print(path[1:-1])
							#print(path[-1])
							#self.model.addConstr(self.model._Y[path[0]] + self.model._Y[path[-1]] <= gp.quicksum(self.model._X[j] for j in path[1:-1]))


			#self.model._Z = self.model.addVars(self.G.nodes(), vtype=gp.GRB.CONTINUOUS, name="z")
			#self.model.addConstrs(self.model._Z[i] >= self.model._X[i] for i in self.G.nodes())
			#self.model.addConstrs(self.model._Z[i] <= self.model._X[i] + .999999 for i in self.G.nodes())
		'''

		if self.model_type == "base_model":
			self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in self.G.nodes())

		if self.model_type == "base_model":
			self.model.addConstrs(self.model._X[i] + self.model._Y[i] <= 1 for i in G.nodes())


		# budget constraints
		if self.model_type == "base_model":
			self.model.addConstr(gp.quicksum(self.model._Y) <= self.b)

		if additonal_facet_defining:
			for i in self.x_vals:
				if self.G.degree(i) == self.k:
					for u in self.G.neighbors(i):
						facet_defining_constraint = self.model.addConstr(self.model._X[i] <= self.model._Y[u] + self.model._X[u])
						facet_defining_constraint.lazy = 3


		if y_val_fix:
			for i in self.y_vals:
				fix = True
				for j in self.G.neighbors(i):
					if j in self.x_vals:
						fix = False 
						break
				if fix:
					self.model._Y[i].ub = 0
					self.var_remaining += 1
			#		couter += 1
			#for j in range(50):
			#	print(couter)

	def remove_all_y_saturated_nodes(self):
		loop = True
		while loop:
			old_tracker = self.y_saturated_reduction
			self.y_saturated_iter()
			if old_tracker == self.y_saturated_reduction:
				loop = False

	def remove_y_edges(self):
		time1 = time.time()
		num_edges_removed = 0
		x_vals = self.x_vals
		y_vals = self.y_vals


		pair_tracker = []
		sub_graph = self.G.subgraph(y_vals)
		for u, v in sub_graph.edges():
			pair_tracker.append((u,v))

		for edge in pair_tracker:
			self.G.remove_edge(edge[0], edge[1])
			num_edges_removed += 1
		time2 = time.time()

		self.remove_y_edges_reduction = num_edges_removed
		self.remove_y_edges_time = time2 - time1

	def y_saturated_iter(self):
		time1 = time.time()
		num_y_saturated_nodes = 0
		temp_graph = self.G.subgraph(self.x_vals)
		for v in temp_graph:
			if self.k - temp_graph.degree(v) > self.b:
				self.y_vals.append(v)
				self.x_vals.remove(v)
				#self.model._X[v].ub = 0

				num_y_saturated_nodes += 1
		time2 = time.time()
		#for i in range(100):
		#	print(num_y_saturated_nodes)
		self.y_saturated_reduction += num_y_saturated_nodes
		self.y_saturated_run_time += time2 - time1
		self.y_saturated_iterations += 1

	def relaxation(self):
		self.model.update()
		self.model = self.model.relax()

	def strength_constraint(self, induced_k_core, anchors):

		self.model.addConstrs(self.model._X[i] + gp.quicksum(self.model._Y[j] for j in anchors) <= self.b for i in self.x_vals if (i != anchors and i not in induced_k_core))

	def warm_start(self):
		initial_anchors = []
		fixings = []
		best_anchors = []
		best_fixing_value = 0

		timer = 0
		G = self.G
		k = self.k
		b = self.b
		y_vals = self.y_vals
		time_for_warm_start = self.time_for_warm_start
		#warm_start = heuristic.warm_start(self.G, self.k, self.b, self.time_for_warm_start)
		viable_nodes = list(G)
		iterations = 0


		first_iter = True
		inital_time = time.time()

		while timer < time_for_warm_start and len(viable_nodes) >= k:

			anchors = random.sample(viable_nodes, b)

			resulting_k_core = heuristic.anchored_k_core(G, k, anchors)

			self.strength_constraint(resulting_k_core, anchors)


			if first_iter:
				best_anchors = anchors
				best_fixing_value = len(resulting_k_core)
			else:
				if len(resulting_k_core) > best_fixing_value:
					if b == 1:
						self.model._Y[best_anchors[0]].ub = 0
					else:
						self.model.addConstr(gp.quicksum(self.model._Y[i] for i in best_anchors) <= b -1)
					best_anchors = anchors
					best_fixing_value = len(resulting_k_core)
				else:
					if b == 1:
						self.model._Y[anchors[0]].ub = 0
					else:
						self.model.addConstr(gp.quicksum(self.model._Y[i] for i in anchors) <= b -1)

			timer = time.time() - inital_time

		warm_start_x = heuristic.anchored_k_core(G, k, best_anchors)
		for anchor in best_anchors:
			if anchor in warm_start_x:
				warm_start_x.remove(anchor)

		for v in best_anchors:
			self.model._Y[v].start = 1

		for v in warm_start_x:
			self.model._X[v].start = 1

	def new_warm_start(self):
		anchors, x_nodes = heuristic.new_heur_idea(self.G, self.k, self.b)

		for v in anchors:
			self.model._Y[v].start = 1

		for v in x_nodes:
			self.model._X[v].start = 1

	def RCM_warm_start(self):

		r = rcm.RCM(self.G, self.k, self.b)
		a, f = r.findAnchors(False)

		a_list = list(a)
		their_sol = heuristic.anchored_k_core(self.G, self.k, a_list)

		k_core = heuristic.anchored_k_core(self.G, self.k, their_sol)

	def optimize(self):
		G = self.G
		k = self.k
		b = self.b
		m = self.model


		if self.fractional_callback:
			m.Params.lazyConstraints = 1

			#m.optimize(seperation.conflict_callback)
			m.optimize(fractional_callback.fractional_callback)
		else:
			m.optimize()



		#if not self.relax:
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

				#for node in SUB.nodes():
				#	print("Degree is: ", SUB.degree[node])

				root = -1

				#for i in G.nodes:
					#if self.model_type != 'naive' and self.model_type != 'strong':
					#	if m._S[i].x > 0.5:
					#		print("Root is ", i)
					#		root = i


				selected_nodes = []
				for i in G.nodes:
					if m._X[i].x > 0.5:
						print("selected node: ", i)
						selected_nodes.append(i)

				for i in G.nodes:
					print("selected node: ", i, " x_value: ", m._X[i].x)


				purchased_nodes = []
				for i in G.nodes:
					if m._Y[i].x > 0.5:
						print("purchased node: ", i)
						purchased_nodes.append(i)

				for i in G.nodes:
					print("purchased node: ", i, " y_value: ", m._Y[i].x)

				print("# of vertices in G: ", len(G.nodes))
				#print("Is it connected? ", nx.is_connected(SUB))
				#print("Diameter? ", nx.diameter(SUB))
				plot = 1
				if plot == 1:
					pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, True, k, b, self.r)
				if plot == 2:
					pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, False, k, b, self.r)

			#m.write("Lobster.lp")

	def save_to_file(self, total_time):
		self.var_num = len(self.model.getVars())
		#self.var_remaining = self.var_num - self.var_remaining

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
				string += str(getattr(self, thing)) + ", "
			string += total_time
			doc.write(string)
			doc.close()

	def return_output(self):
		exceptions = ['G', 'R', 'model', 'x_vals', 'y_vals', 'time_for_warm_start', 'filename', 'y_saturated']
		output = [attribute for attribute in dir(self) if not attribute.startswith("__") and not callable(getattr(self, attribute)) and attribute not in exceptions]
		output.sort(key = output_sort)
		return output


class reduced_model(base_model):

	def __init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated, y_continuous, additonal_facet_defining, y_val_fix, fractional_callback):
		base_model.__init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated, y_continuous, additonal_facet_defining, y_val_fix, fractional_callback)

		for y_val in self.y_vals:
			self.model._X[y_val].ub = 0
			self.var_remaining += 1

		k_core_G = heuristic.anchored_k_core(self.G, self.k, [])
		k_core_G = self.G.subgraph(k_core_G)

		self.num_k_core_nodes = len(k_core_G.nodes())

		#case if everynode is in the k-core
		if len(self.G.nodes()) == self.num_k_core_nodes:

			for v in self.x_vals:
				self.model._X[v].lb = 1
				self.model._Y[v].ub = 0
				self.var_remaining += 1
			for v in self.y_vals:
				self.model._Y[v].ub = 0
				self.var_remaining += 1

		#case if some of the nodes are in the $k$-core
		if self.num_k_core_nodes != 0 and self.num_k_core_nodes != len(self.G.nodes()):

			#R is the list of nodes not in the k-core

			self.R = list(self.G.nodes() - k_core_G.nodes())

			for node in k_core_G.nodes():

				self.model._X[node].lb = 1
				self.model._Y[node].ub = 0
				self.var_remaining += 2



		if self.R:
			deg_constraints = self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in self.R if i in self.x_vals)
			#self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in self.R if i in self.x_vals)
			#self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in self.x_vals)

			self.model.addConstrs(self.model._X[i] + self.model._Y[i] <= 1 for i in self.x_vals if i in self.R if i in self.x_vals)

			self.model.addConstr(gp.quicksum(self.model._Y[i] for i in self.R if i in self.y_vals) <= self.b )

		else:
			deg_constraints = self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in self.x_vals)

			if self.lazyconstraints:
				for v in self.x_vals:
					deg_constraints[v].lazy = 3


class radius_bounded_model(base_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated):
		base_model.__init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated)
		model._S = model.addVars(self.G.nodes, vtype=gp.GRB.BINARY, name="s")
		model.addConstr(gp.quicksum(model._S) == 1)


class vermyev_model(radius_bounded_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated):
		radius_bounded_model.__init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated)

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
	def __init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated):
		radius_bounded_model.__init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated)

		#allow lazy constraints
		model.Params.lazyConstraints = 1

		#Add center variable

		#Center must be active constraint
		model.addConstrs(model._S[i] <= model._Y[i] + model._X[i] for i in self.G.nodes())


		#initial constraint
		for i in self.G.nodes():
			shortest_paths = nx.shortest_path_length(self.G, i)
			for key, value in shortest_paths.items():
				if value > r:
					model.addConstr(model._X[i] + model._Y[i] + model._S[key] <= 1)


	def optimize(self):
		G = self.G
		k = self.k
		b = self.b
		m = self.model

		m.optimize(cut_formulation_callback.cut_callback)

		#model.optimize()
		var = m.getVars()
		#print(var)


		#if not self.relax:
		self.upper_bound = m.objBound
		self.lower_bound = m.objVal


class extended_cut_model(cut_model):
	def __init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated):
		cut_model.__init__(self, filename, instance_name, G, model_type, k, b, r, y_saturated)
		self.model._Z = model.addVars(self.G.nodes(), self.G.nodes, vtype = gp.GRB.BINARY, name = 'z')

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