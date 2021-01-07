import gurobipy as gp
from gurobipy import GRB

def build_k_core(G, m, anchored, k, b):
        # fix y vars to zero if the k-core problem is not anchored
        if not anchored:
            for i in G.nodes: m._Y[i].ub = 0

        # fix x vars to zero if degree of a vertex is < k.
        for i in G.nodes:
            if G.degree[i] < k: m._X[i].ub = 0

        # objective function
        m.setObjective(gp.quicksum(m._X), sense=GRB.MAXIMIZE)

        # k degree constraints
        m.addConstrs(gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= k*m._X[i] for i in G.nodes if G.degree[i] >= k)

        # conflict constraints
        m.addConstrs(m._X[i] + m._Y[i] <= 1 for i in G.nodes if G.degree[i] >= k)

        # budget constraints
        if anchored:
            m.addConstr(gp.quicksum(m._Y) <= b)

def build_k_core_reduced(G, m, anchored, k, b, weights, k_core_nodes, s):
        # fix y vars to zero if the k-core problem is not anchored
        if not anchored:
            for i in G.nodes: m._Y[i].ub = 0

        # fix x vars to zero if degree of a vertex is < k.
        for i in G.nodes:
            if G.degree[i] < k: m._X[i].ub = 0

        # objective function
        m.setObjective(gp.quicksum(m._X) + s, sense=GRB.MAXIMIZE)

        # k degree constraints
        #m.addConstrs(gp.quicksum(weights[i,j] for j in G.nodes - k_core_nodes) + gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i)) >= k*m._X[i] for i in G.nodes if G.degree[i] >= k)

        m.addConstrs(gp.quicksum(weights[i,j] for j in G.nodes - k_core_nodes for i in k_core_nodes) + gp.quicksum(m._X[j] + m._Y[j] for j in G.neighbors(i) if j not in k_core_nodes) >= k*m._X[i] for i in G.nodes if i not in k_core_nodes)

        # conflict constraints
        m.addConstrs(m._X[i] + m._Y[i] <= 1 for i in G.nodes if i not in k_core_nodes)

        # budget constraints
        if anchored:
            m.addConstr(gp.quicksum(m._Y) <= b)




