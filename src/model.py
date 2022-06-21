import gurobipy as gp
import heuristic
import new_k_core
import networkx as nx
import pretty_plot
import new_heuristic
import seperation
import time

def sam_model(instance):
	G = instance.G
	k = instance.k
	b = instance.b

	best = []
	best_anchor = 0
	print('# of things to solve: ', len(G.nodes()))
	for node in G.nodes():
		print('node: ', node)
		time1 = time.time()
		current = new_heuristic.anchored_k_core(G,k,[node])
		time2 = time.time()
		current = nx.algorithms.core.k_core(G,k)
		time3 = time.time()
		print('sam code: ', time2 - time1)
		print('nx code: ', time3 - time2)

		if len(current) > len(best):
			best = current
			best_anchor = node
	return len(best) + 1, best, best_anchor

def model(instance):
	G = instance.G
	k = instance.k
	b = instance.b
	#init variables
	plot = 1
	R = []
	var_sub = 0

	#init model




	instance.model._X = instance.model.addVars(G.nodes(), vtype=gp.GRB.BINARY, name="x")
	instance.model._Y = instance.model.addVars(G.nodes(), vtype=gp.GRB.BINARY, name="y")
	print('here')

	#warm_start
	if instance.warm_start:
		initial_anchors = []
		warm_start = new_heuristic.warm_start(G, k, b)
		print('almost done')
		for fixing in warm_start[0]:
			#print(fixing)
			#start value for Y's
			instance.model._Y[fixing[1]].start = 1
			initial_anchors.append(fixing[1])
			for vertex in fixing[2]:
				#start value for X's
				instance.model._X[vertex].start = 1

		for u in warm_start[1]:
			#Fixing dead Y's to zero
			if b == 1:
				instance.model._Y[u].ub = 0

		b_best_fixings = warm_start[0]

	print('done')
	#if_reduction
	if instance.reduction:
		k_core_G = heuristic.new_code(G, k)
		k_core_G = G.subgraph(k_core_G)


		#case if everynode is in the k-core
		if G == k_core_G:

			return('NA',  len(G.nodes()), len(G.nodes()),'1')

		#case if none of the nodes are in a k-core
		if len(k_core_G.nodes()) != 0:

			#Get each k-core
			components = nx.algorithms.components.connected_components(k_core_G)

			for comp in components:
				for node in comp:
					instance.num_k_core_nodes += 1

			#R is the list of nodes not in the k-core
			instance.R = list(G.nodes() - k_core_G.nodes())

			#building the weights

			for node in instance.R:
				if node in instance.x_vals:
					instance.weights[node] = 0
					for neighbor in G.neighbors(node):

						if neighbor in k_core_G.nodes():
								instance.weights[node] += 1
			#Keeping track of the variable reduction
			var_sub = 0
			for node in k_core_G.nodes():
				instance.model._X[node].ub = 0
				instance.model._Y[node].ub = 0
				var_sub += 2

	if instance.conflict_model:
		new_k_core.build_k_core_conflict(instance, initial_anchors)
	else:
		new_k_core.build_k_core(instance)

	#HEURSITIC
	if instance.conflict_model:
		instance.model.optimize(seperation.conflict_callback)
	else:
		instance.model.optimize()

	if instance.model.status == gp.GRB.OPTIMAL or instance.model.status == gp.GRB.TIME_LIMIT:
		if instance.print_to_console:
			cluster = [i for i in G.nodes if instance.model._X[i].x > 0.5 or instance.model._Y[i].x > 0.5]
			SUB = G.subgraph(cluster)

			#for node in SUB.nodes():
			#	print("Degree is: ", SUB.degree[node])

			for i in G.nodes:
				if instance.radius_bounded == True:
					if instance.model._S[i].x > 0.5:
						#print("Root is ", i)
						root = i

			selected_nodes = []
			for i in G.nodes:
				if instance.model._X[i].x > 0.5:
					#print("selected node: ", i)
					selected_nodes.append(i)

			purchased_nodes = []
			for i in G.nodes:
				if instance.model._Y[i].x > 0.5:
					print("purchased node: ", i)
					purchased_nodes.append(i)

			#print("# of vertices in G: ", len(G.nodes))
			#print("Is it connected? ", nx.is_connected(SUB))
			#print("Diameter? ", nx.diameter(SUB))

			if plot == 1:
				pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, -1, True, k, b, 0)
			if plot == 2:
				pretty_plot.pretty_plot(G, selected_nodes, purchased_nodes, root, False, k, b, r)

		#m.write("Lobster.lp")
		var = instance.model.getVars()

		return len(var) - var_sub, instance.model.objBound, instance.model.objVal, instance.num_k_core_nodes