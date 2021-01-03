import networkx as nx

import gurobipy as gp
from gurobipy import GRB

def build_flow(G, m, r):
    DG = nx.DiGraph(G) # bidirected version of G

    m._F = m.addVars(DG.nodes,DG.edges,vtype=GRB.CONTINUOUS, name = "f")

    #m._Gen = m.addVars(DG.nodes,DG.nodes,vtype=GRB.CONTINUOUS, name = "g")

    m._S = m.addVars(G.nodes, vtype=GRB.BINARY, name="s")

    P = nx.power(G,r)

    DP = nx.DiGraph(P)

    # exactly one center should be selected
    m.addConstr(gp.quicksum(m._S) == 1)

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

