import networkx as nx
import gurobipy as gp
import heuristic
import pretty_plot
import matplotlib.pyplot as plt
import time
import random
import fractional_callback
import cut_formulation_callback
import extended_cut_formulation_callback
import seperation

class base_model( object ):
	def __init__(self, filename, G, model, model_type, k, b, r):
		#Gurobi paramater options
		model.setParam('OutputFlag', 1)
		model.Params.timeLimit= 3600
		model.params.LogToConsole = 1
		model.params.LogFile='../results/logs/log_' + filename +'_' + str(k) + '_' +  str(b) + '.log'
		model.params.method = 3

		#model options

		self.model_type = model_type

		#to add later if not using callbacks do not edit


		#every member of class
		self.num_k_core_nodes = 0
		self.R = []
		self.weights = {}
		self.model = model
		self.var_sub = 0
		self.var_num = 0
		#self.relax = False
		self.y_saturated_reduction = 'NA'
		self.y_saturated_run_time = 'NA'
		self.remove_y_edges_reduction = 'NA'
		self.remove_y_edges_time = 'NA'

		#Set up constants
		self.filename = filename
		self.k = k
		self.b = b
		self.r = r

		#warm_start
		self.time_for_warm_start = 60

		#Set up G
		self.G = G

		self.x_vals = []
		self.y_vals = []
		for node in self.G.nodes():
			if self.G.degree(node)>= self.k:
				self.x_vals.append(node)
			else:
				self.y_vals.append(node)

		#set up model
		self.model._G = G
		self.model._b = b
		self.model._k = k
		self.model._R = G.nodes()
		self.model._r = r

		self.model._X = self.model.addVars(self.G.nodes(), vtype=gp.GRB.BINARY, name="x")
		self.model._Y = self.model.addVars(self.G.nodes(), vtype=gp.GRB.CONTINUOUS, name="y")


		for y_val in self.y_vals:
			self.model._X[y_val].ub = 0

		#R = self.R

		# objective function
		#m.setObjective(gp.quicksum(m._X) + gp.quicksum(m._Y) + self.num_k_core_nodes, sense=gp.GRB.MAXIMIZE)
		self.model.setObjective(gp.quicksum(self.model._X), sense=gp.GRB.MAXIMIZE)

		# k degree constraints
		if model_type != 'strong':
			self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in self.G.neighbors(i)) >= self.k * self.model._X[i] for i in self.x_vals)
		#m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= self.k * m._X[i] for i in G.nodes())
		self.model.addConstrs(self.model._X[i] + self.model._Y[i] <= 1 for i in self.x_vals)

		# budget constraints
		self.model.addConstr(gp.quicksum(self.model._Y) <= self.b)

		#valid facet defining
		#problem in strong form
		valid = False
		if valid:
			for i in self.x_vals:
				if self.G.degree(i) == self.k:
					self.model.addConstrs(self.model._X[i] <= self.model._Y[u] + self.model._X[u] for u in self.G.neighbors(i))

	def remove_y_edges(self):
		time1 = time.time()
		fixed_num = 0
		x_vals = self.x_vals
		y_vals = self.y_vals


		pair_tracker = []
		sub_graph = self.G.subgraph(y_vals)
		for u, v in sub_graph.edges():
			pair_tracker.append((u,v))

		for edge in pair_tracker:
			self.G.remove_edge(edge[0], edge[1])
			fixed_num += 1
		time2 = time.time()

		'''
		counter = 0
		for node in self.y_vals:
			if set([n for n in self.G.neighbors(node)]) <= set(self.y_vals):
				self.model._Y[node].ub = 0
				counter += 1
		'''

		self.remove_y_edges_reduction = fixed_num
		self.remove_y_edges_time = time2 - time1

	def y_saturated(self):
		time1 = time.time()
		G = self.G
		x_vals = self.x_vals
		y_vals = self.y_vals
		k = self.k
		b = self.b
		fixed_num = 0
		temp_graph = G.subgraph(x_vals)
		for v in temp_graph:
			if k - temp_graph.degree(v) > b:
				self.y_vals.append(v)
				self.x_vals.remove(v)
				self.model._X[v].ub = 0

				fixed_num += 1
		time2 = time.time()
		self.y_saturated_reduction = fixed_num
		self.y_saturated_run_time = time2 - time1

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

	#def set_up_model(self):
		G = self.G
		m = self.model
		#R = self.R

		# objective function
		#m.setObjective(gp.quicksum(m._X) + gp.quicksum(m._Y) + self.num_k_core_nodes, sense=gp.GRB.MAXIMIZE)
		m.setObjective(gp.quicksum(m._X) + self.num_k_core_nodes, sense=gp.GRB.MAXIMIZE)

		# k degree constraints
		m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= self.k * m._X[i] for i in G.nodes())
		#m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= self.k * m._X[i] for i in G.nodes())
		m.addConstrs(m._X[i] + m._Y[i] <= 1 for i in G.nodes())

		# budget constraints
		m.addConstr(gp.quicksum(m._Y) <= self.b)

		#valid facet defining
		for i in G.nodes:
			if G.degree(i) == self.k:
				m.addConstrs(m._X[i] <= m._Y[u] + m._X[u] for u in G.neighbors(i))

	def optimize(self):
		G = self.G
		k = self.k
		b = self.b
		m = self.model

		on_the_fly = True
		if on_the_fly:
			m.Params.lazyConstraints = 1

			#m.optimize(seperation.conflict_callback)
			m.optimize(fractional_callback.fractional_callback)
		else:
			m.optimize()

		#model.optimize()
		var = m.getVars()
		#print(var)


		self.var_num = len(var) - self.var_sub
		#if not self.relax:
		self.upper_bound = m.objBound
		self.lower_bound = m.objVal

	def print_model(self):
		G = self.G
		k = self.k
		b = self.b
		m = self.model


		display = False
		if display:
			if m.status == gp.GRB.OPTIMAL or m.status == gp.GRB.TIME_LIMIT:


				cluster = [i for i in G.nodes if m._X[i].x > 0.5 or m._Y[i].x > 0.5]
				SUB = G.subgraph(cluster)

				#for node in SUB.nodes():
				#	print("Degree is: ", SUB.degree[node])

				root = -1

				for i in G.nodes:
					if self.model_type != 'naive' and self.model_type != 'strong':
						if m._S[i].x > 0.5:
							print("Root is ", i)
							root = i


				selected_nodes = []
				for i in G.nodes:
					if m._X[i].x > 0.5:
						print("selected node: ", i)
						selected_nodes.append(i)

				purchased_nodes = []
				for i in G.nodes:
					if m._Y[i].x > 0.5:
						print("purchased node: ", i)
						purchased_nodes.append(i)

				print("# of vertices in G: ", len(G.nodes))
				#print("Is it connected? ", nx.is_connected(SUB))
				#print("Diameter? ", nx.diameter(SUB))
				plot = 1
				if plot == 1:
					pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, True, k, b, self.r)
				if plot == 2:
					pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, False, k, b, self.r)

			#m.write("Lobster.lp")

	def fix_k_core(self):
		G = self.G
		k = self.k

		k_core_G = heuristic.anchored_k_core(G, k, [])
		k_core_G = G.subgraph(k_core_G)

		#case if everynode is in the k-core
		if G == k_core_G:
			print('problem')
			#return('NA',  len(G.nodes()), len(G.nodes()),'1')

		#case if none of the nodes are in a k-core
		if len(k_core_G.nodes()) != 0:

			#Get each k-core
			components = nx.algorithms.components.connected_components(k_core_G)

			for comp in components:
				for node in comp:
					self.model._X[node].lb = 1

	def output_results(self):
		return([self.var_num, self.remove_y_edges_reduction, self.remove_y_edges_time, self.y_saturated_reduction, self.y_saturated_run_time, self.upper_bound, self.lower_bound, self.num_k_core_nodes])

	def free_model(self):
		self.model.dispose()

class reduced_model(base_model):

	def __init__(self, filename, G, model, model_type, k, b, r):
		base_model.__init__(self, filename, G, model, model_type, k, b, r)

		G = self.G
		k = self.k
		b = self.b
		m = self.model
		x_vals = self.x_vals
		y_vals = self.y_vals
		R = self.R
		weights = self.weights


		k_core_G = heuristic.anchored_k_core(self.G, self.k, [])
		k_core_G = self.G.subgraph(k_core_G)

		#case if everynode is in the k-core
		if self.G == k_core_G:
			print('problem')
			#return('NA',  len(G.nodes()), len(G.nodes()),'1')

		#case if none of the nodes are in a k-core
		if len(k_core_G.nodes()) != 0:

			#Get each k-core
			components = nx.algorithms.components.connected_components(k_core_G)

			for comp in components:
				for node in comp:
					self.num_k_core_nodes += 1

			#R is the list of nodes not in the k-core
			R = list(self.G.nodes() - k_core_G.nodes())
			self.R = R
			m._R = R


			'''
			#TEMPHERE
			#building the weights
			for node in R:

				if node in self.x_vals:
					self.weights[node] = 0
					for neighbor in self.G.neighbors(node):
						if neighbor in k_core_G.nodes():
								self.weights[node] += 1
			'''

			#Keeping track of the variable reduction

			for node in k_core_G.nodes():
				#TEMP HERE
				'''
				self.model._X[node].ub = 0
				self.model._Y[node].ub = 0
				'''
				self.model._X[node].lb = 1
				self.model._Y[node].ub = 0
				self.var_sub += 2

		if R:
			#TEMP HERE
			'''
			m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= (k - weights[i]) * m._X[i] for i in R if i in x_vals)
			'''

			deg_constraints = m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= self.k * m._X[i] for i in R if i in x_vals)


		else:
			deg_constraints = m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= self.k * m._X[i] for i in x_vals)
			for v in x_vals:
				deg_constraints[v].lazy = 3

class radius_bounded_model(base_model):
	def __init__(self, filename, G, model, model_type, k, b, r):
		base_model.__init__(self, filename, G, model, model_type, k, b, r)
		model._S = model.addVars(self.G.nodes, vtype=gp.GRB.BINARY, name="s")
		model.addConstr(gp.quicksum(model._S) == 1)

class vermyev_model(radius_bounded_model):
	def __init__(self, filename, G, model, model_type, k, b, r):
		radius_bounded_model.__init__(self, filename, G, model, model_type, k, b, r)

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
	def __init__(self, filename, G, model, model_type, k, b, r):
		radius_bounded_model.__init__(self, filename, G, model, model_type, k, b, r)

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


		self.var_num = len(var) - self.var_sub
		#if not self.relax:
		self.upper_bound = m.objBound
		self.lower_bound = m.objVal

class extended_cut_model(cut_model):
	def __init__(self, filename, G, model, model_type, k, b, r):
		cut_model.__init__(self, filename, G, model, model_type, k, b, r)
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
		var = m.getVars()
		#print(var)


		self.var_num = len(var) - self.var_sub
		#if not self.relax:
		self.upper_bound = m.objBound
		self.lower_bound = m.objVal