import gurobipy as gp
import new_heuristic
def build_k_core(instance):
		# fix y vars to zero if the k-core problem is not anchored
		#print(G.nodes)
		G = instance.G
		x_vals = instance.x_vals
		y_vals = instance.y_vals
		k = instance.k
		b = instance.b
		R = instance.R


		if not instance.anchored:
			for i in G.nodes:
				instance.model._Y[i].ub = 0

		# fix x vars to zero if degree of a vertex is < k.
		for i in y_vals:
			instance.model._X[i].ub = 0




		# objective function
		instance.model.setObjective(gp.quicksum(instance.model._X) +
		gp.quicksum(instance.model._Y) + instance.num_k_core_nodes, sense=gp.GRB.MAXIMIZE)

		# k degree constraints
		#m.addConstrs(gp.quicksum(weights[i,j] for j in R) + gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= k*m._X[i] for i in G.nodes if G.degree[i] >= k)

		if instance.reduction and R != []:
			instance.model.addConstrs(gp.quicksum(instance.model._X[j] + instance.model._Y[j] for j in G.neighbors(i)) >= (k - instance.weights[i]) * instance.model._X[i] for i in R if i in x_vals)
		else:
			instance.model.addConstrs(gp.quicksum(instance.model._X[j] + instance.model._Y[j] for j in G.neighbors(i)) >= k * instance.model._X[i] for i in G.nodes if i in x_vals)

		#instance.model.addConstrs(gp.quicksum(instance.model._X[j] + instance.model._Y[j] for j in G.neighbors(i)) >= k*instance.model._X[i] for i in G.nodes if i in x_vals)
		instance.model.addConstrs(instance.model._X[i] + instance.model._Y[i] <= 1 for i in x_vals)


		# conflict constraints
		if instance.radius_bounded:
			instance.model.addConstrs(m._X[i] + instance.model._Y[i] <= 1 for i in R)

		# budget constraints
		if instance.anchored:
			instance.model.addConstr(gp.quicksum(instance.model._Y) <= b)

		if instance.radius_bounded and connectivity == 'flow':
			flow.build_flow(G, m, r)
		if instance.radius_bounded and connectivity == 'vermyev':
			vermyev.build_vermyev(G, m, r)

def build_k_core_conflict(instance, initial_anchors):
	instance.model.Params.lazyConstraints = 1

	G = instance.G
	x_vals = instance.x_vals
	y_vals = instance.y_vals
	k = instance.k
	b = instance.b
	R = instance.R

	instance.model._G = G
	instance.model._k = k
	instance.model._b = b
	# objective function
	instance.model.setObjective(gp.quicksum(instance.model._X) +
	gp.quicksum(instance.model._Y) + instance.num_k_core_nodes, sense=gp.GRB.MAXIMIZE)

	# fix x vars to zero if degree of a vertex is < k.
	for i in y_vals:
		instance.model._X[i].ub = 0

	#budget constraint
	if instance.anchored:
			instance.model.addConstr(gp.quicksum(instance.model._Y) == b)

	#no double counting constraint
	instance.model.addConstrs(instance.model._X[i] + instance.model._Y[i] <= 1 for i in x_vals)

	#Initial conflict constraints
	selected_nodes = new_heuristic.anchored_k_core(G, k, initial_anchors)
	#print("selecetd nodes: ", selected_nodes)
	#print("inital anchors: ", initial_anchors)
	for j in G.nodes - selected_nodes:
		#print('vertex_j: ', j)
		instance.model.addConstr(gp.quicksum(instance.model._Y[i] for i in initial_anchors) + instance.model._X[j] <= b)