import networkx as nx
import gurobipy as gp
import heuristic
import pretty_plot
import matplotlib.pyplot as plt
import time

class base_model( object ):
	def __init__(self, filename, G, model, k, b, r, radius_bounded, connectivity):
		#Gurobi paramater options
		model.setParam('OutputFlag', 1)
		model.Params.timeLimit= 60*60
		model.params.LogToConsole = 1
		model.params.LogFile='../results/logs/log_' + filename +'_' + str(k) + '_' +  str(b) + '.log'

		#model options
		self.print_to_console = True

		self.conflict_model = False

		#every member of class
		self.num_k_core_nodes = 0
		self.R = []
		self.weights = {}
		self.model = model
		self.var_sub = 0
		self.var_num = 0
		#self.relax = False

		#Set up constants
		self.filename = filename
		self.k = k
		self.b = b
		self.r = r

		#warm_start
		self.time_for_warm_start = 20

		self.radius_bounded = radius_bounded
		self.connectivity = connectivity


		#Set up G
		self.G = nx.relabel.convert_node_labels_to_integers(G)

		for vertex in self.G.nodes():
				self.G.nodes[vertex]['anchor'] = False

		'''
			for neighbor in self.G.neighbors(node):
				self.G.edges[node, neighbor]["edge_removed"] = False
		'''
		#set up x_vals and y_vals
		self.x_vals = []
		self.y_vals = []
		for node in self.G.nodes():
			if self.G.degree(node)>= k:
				self.x_vals.append(node)
			else:
				self.y_vals.append(node)

		#set up model
		self.model._X = self.model.addVars(self.G.nodes(), vtype=gp.GRB.BINARY, name="x")
		self.model._Y = self.model.addVars(self.G.nodes(), vtype=gp.GRB.BINARY, name="y")

		for y_val in self.y_vals:
			self.model._X[y_val].ub = 0

	def neighbor(self, node):
		#change to add node attribute wether or not it is y_val or x_val
		neighbors = list(self.G.neighbors(node))
		for vertex in neighbors:
			if self.G.edges[node, vertex]["edge_removed"] == True:
				neighbors.remove(vertex)

		return neighbors

	def remove_y_edges(self):

		#G = self.G
		x_vals = self.x_vals
		y_vals = self.y_vals



		for node in y_vals:

			for neighbor in self.G.neighbors(node):
			#for neighbor in G.neighbors(node):
				if neighbor in self.y_vals:

					#G.edges[node, neighbor]["edge_removed"] = True
					self.G.edges.remove(node, neighbor)

	def y_saturated(self):
		G = self.G
		x_vals = self.x_vals
		y_vals = self.y_vals

		if self.b < self.k:
			x_tracker = [0] * (len(G.nodes()))

			for y_val in y_vals:
				#for neighbor in sam_graph.neighbor(self, y_val):
				for neighbor in G.neighbors(y_val):
					x_tracker[neighbor] += 1

			for x_val in x_vals:
				if self.b < self.k - G.degree(x_val) + x_tracker[x_val]:
					self.y_vals.append(x_val)
					self.x_vals.remove(x_val)

	def relaxation(self):
		self.model.update()
		self.model = self.model.relax()




	def warm_start(self):
		initial_anchors = []
		tracker = []
		inital_time = time.time()
		timer = 0
		G = self.G
		k = self.k
		b = self.b
		y_vals = self.y_vals
		time_for_warm_start = self.time_for_warm_start
		#warm_start = heuristic.warm_start(self.G, self.k, self.b, self.time_for_warm_start)

		for node in y_vals:

			resulting_k_core = heuristic.anchored_k_core(G, k, [node])
			current = [node, resulting_k_core]
			tracker.append(current)
			timer += time.time() - inital_time
			if timer >= time_for_warm_start:
				break

		value_of_fixing = []
		anchors = []
		nodes_in_k_core = []

		for fixing in tracker:
			value_of_fixing.append(len(fixing[1]))
			anchors.append(fixing[0])
			nodes_in_k_core.append(fixing[1])

		b_best_fixings = sorted(zip(value_of_fixing, anchors, nodes_in_k_core), reverse = True)[:b]

		dead_y = []
		warm_start_y = []

		for fixing in b_best_fixings:

			warm_start_y.append(fixing[1])

		if self.b == 1:
			for fixing in tracker:
				if fixing[0] not in warm_start_y:
					self.model._Y[fixing[0]].ub = 0
					self.var_sub += 1

		warm_start_x = heuristic.anchored_k_core(G,k, warm_start_y)





		for v in warm_start_y:
			self.model._Y[v].start = 1
			initial_anchors.append(fixing[1])
		for v in warm_start_x:
			self.model._X[v].start = 1



	def set_up_model(self):
		G = self.G
		#m = self.model
		#R = self.R

		# objective function
		self.model.setObjective(gp.quicksum(self.model._X) + gp.quicksum(self.model._Y) + self.num_k_core_nodes, sense=gp.GRB.MAXIMIZE)

		# k degree constraints
		#self.model.addConstrs(gp.quicksum(weights[i,j] for j in R) + gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= k*self.model._X[i] for i in G.nodes if G.degree[i] >= k)
		#self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in self.x_vals)
		self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in G.nodes())



		self.model.addConstrs(self.model._X[i] + self.model._Y[i] <= 1 for i in self.x_vals)

		# budget constraints
		self.model.addConstr(gp.quicksum(self.model._Y) <= self.b)

	def optimize(self):
		G = self.G
		k = self.k
		b = self.b

		if self.conflict_model:
			self.model.optimize(seperation.conflict_callback)
		else:
			self.model.optimize()
		'''
		if self.relax:
			model = self.relaxed_model
			print('BBBBBBBBBBB')
		else:
			model = self.model
			print('AAAAAAAAAAAA')
		'''

		#model.optimize()
		var = self.model.getVars()
		print(var)

		self.var_num = len(var) - self.var_sub
		#if not self.relax:
		self.upper_bound = self.model.objBound
		self.lower_bound = self.model.objVal

		if self.model.status == gp.GRB.OPTIMAL or self.model.status == gp.GRB.TIME_LIMIT:
			if self.print_to_console:
				'''
				if self.relax:
					for node in G.nodes():
						#print('node: ', node, 'x_val: ', self.model._X[node].x, 'y_val: ', self.model._Y[node].x)
						plt.show()

				else:
				'''
				cluster = [i for i in G.nodes if self.model._X[i].x > 0.5 or self.model._Y[i].x > 0.5]
				SUB = G.subgraph(cluster)

				#for node in SUB.nodes():
				#	print("Degree is: ", SUB.degree[node])
				'''
				for i in G.nodes:
					if radius_bounded == True:
						if self.model._S[i].x > 0.5:
							#print("Root is ", i)
							root = i
				'''

				selected_nodes = []
				for i in G.nodes:
					if self.model._X[i].x > 0.5:
						#print("selected node: ", i)
						selected_nodes.append(i)

				purchased_nodes = []
				for i in G.nodes:
					if self.model._Y[i].x > 0.5:
						print("purchased node: ", i)
						purchased_nodes.append(i)

				#print("# of vertices in G: ", len(G.nodes))
				#print("Is it connected? ", nx.is_connected(SUB))
				#print("Diameter? ", nx.diameter(SUB))
				plot = 1
				if plot == 1:
					pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, -1, True, k, b, 0)
				if plot == 2:
					pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, -1, False, k, b, 0)

			#m.write("Lobster.lp")


	def output_results(self):
		return([self.var_num, self.upper_bound, self.lower_bound, self.num_k_core_nodes])

class reduced_model(base_model):

	def __init__(self, filename, G, model, k, b, r, radius_bounded, connectivity):
		base_model.__init__(self, filename, G, model, k, b, r, radius_bounded, connectivity)

	def set_up_model(self):
		G = self.G
		k = self.k
		b = self.b
		x_vals = self.x_vals
		y_vals = self.y_vals
		R = self.R
		weights = self.weights


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
					self.num_k_core_nodes += 1

			#R is the list of nodes not in the k-core
			R = list(G.nodes() - k_core_G.nodes())
			self.R = R

			#building the weights
			for node in R:
				if node in self.x_vals:
					self.weights[node] = 0
					for neighbor in G.neighbors(node):
						if neighbor in k_core_G.nodes():
								self.weights[node] += 1

			#Keeping track of the variable reduction

			for node in k_core_G.nodes():
				self.model._X[node].ub = 0
				self.model._Y[node].ub = 0
				self.var_sub += 2





		# objective function
		self.model.setObjective(gp.quicksum(self.model._X) +
		gp.quicksum(self.model._Y) + self.num_k_core_nodes, sense=gp.GRB.MAXIMIZE)

		# k degree constraints
		#m.addConstrs(gp.quicksum(weights[i,j] for j in R) + gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= k*m._X[i] for i in G.nodes if G.degree[i] >= k)

		if R:
			self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= (k - weights[i]) * self.model._X[i] for i in R if i in x_vals)
			self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= (k) * self.model._X[i] for i in R if i in y_vals)
		else:
			self.model.addConstrs(gp.quicksum(self.model._X[j] + self.model._Y[j] for j in G.neighbors(i)) >= self.k * self.model._X[i] for i in G.nodes())






		# conflict constraints
		self.model.addConstrs(self.model._X[i] + self.model._Y[i] <= 1 for i in x_vals)




		# budget constraints
		self.model.addConstr(gp.quicksum(self.model._Y) <= b)







#conflict
'''
if instance.conflict_model:
		new_k_core.build_k_core_conflict(instance, initial_anchors)
'''
