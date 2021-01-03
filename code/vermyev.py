import networkx as nx

import gurobipy as gp
from gurobipy import GRB

def build_vermyev(G, m, r):
    DG = nx.DiGraph(G) # bidirected version of G
    L = range(1, r + 1)
    m._w = m.addVars(DG.nodes,DG.nodes, L, vtype=GRB.BINARY, name = "w")
    m._S = m.addVars(G.nodes, vtype=GRB.BINARY, name="s")


    # exactly one center should be selected
    m.addConstr(gp.quicksum(m._S) == 1)

    # coupling constarints
    m.addConstrs(m._S[i] <= m._X[i] + m._Y[i] for i in G.nodes)
    for i in G.nodes:
        for j in G.nodes:
            for l in L:
                if i == j:
                    m._w[i,j,l].ub = 0

                if l < nx.shortest_path_length(G, i,j):
                        m._w[i,j,l].ub = 0


    for i in G.nodes:
        for j in G.nodes:
            if i != j:
                possible_ls = range(nx.shortest_path_length(G, i,j), r+1)

                m.addConstr(m._X[i] + m._Y[i] + m._S[j] <= 1 + gp.quicksum(m._w[i,j,l] for l in possible_ls))

                for l in possible_ls:
                    #m.addConstr(m._w[i,j,l] <= m._S[j])
                    if l > 1:
                        m.addConstr(m._w[i,j,l] <= gp.quicksum(m._w[i,u, l-1] for u in G.neighbors(j)))

                    #m.addConstr(m._X[i] + m._Y[i] + m._w[i,j, l] <= 1 + m._S[j])