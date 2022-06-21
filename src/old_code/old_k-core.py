import gurobipy as gp
from gurobipy import GRB
import networkx as nx

def build_k_core(G, m, anchored, radius_bounded, connectivity, reduced_model, k, b, weights, R, num_k_core_nodes, temp):
		# fix y vars to zero if the k-core problem is not anchored
		#print(G.nodes)
		x_vals = []
		y_vals = []

		if not anchored:
			for i in G.nodes: m._Y[i].ub = 0

		# fix x vars to zero if degree of a vertex is < k.
		for i in G.nodes():
			if G.degree[i] < k:
				y_vals.append(i)
				m._X[i].ub = 0
			else:
				if not radius_bounded:
					x_vals.append(i)
					#m._Y[i].ub = 0



		# objective function
		m.setObjective(gp.quicksum(m._X) + gp.quicksum(m._Y) - gp.quicksum(m._X[i] * m._Y[i] for i in G.nodes()) + num_k_core_nodes, sense=GRB.MAXIMIZE)

		# k degree constraints
		#m.addConstrs(gp.quicksum(weights[i,j] for j in R) + gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= k*m._X[i] for i in G.nodes if G.degree[i] >= k)
		if reduced_model and R != []:
			m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= (k - weights[i]) * m._X[i] for i in R if i in x_vals)
		else:
			m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= k*m._X[i] for i in G.nodes if G.degree[i] >= k)




		# conflict constraints
		if radius_bounded == True:
			m.addConstrs(m._X[i] + m._Y[i] <= 1 for i in R)

		# budget constraints
		if anchored:
			m.addConstr(gp.quicksum(m._Y) <= b)

		if radius_bounded and connectivity == 'flow':
			flow.build_flow(G, m, r)
		if radius_bounded and connectivity == 'vermyev':
			vermyev.build_vermyev(G, m, r)

