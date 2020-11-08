import networkx as nx

import gurobipy as gp
from gurobipy import GRB

def build_flow(G, m, r):
    DG = nx.DiGraph(G) # bidirected version of G
    
    F = m.addVars(DG.nodes,DG.edges,vtype=GRB.CONTINUOUS)
    
    Gen = m.addVars(DG.nodes,DG.nodes,vtype=GRB.CONTINUOUS)
    
    m._S = m.addVars(G.nodes, vtype=GRB.BINARY, name="s")
    
    P = nx.power(G,r)
    
    DP = nx.DiGraph(P)
    
    for i in G.nodes:
        for j in G.nodes:
            if (i,j) not in DP.edges:
                Gen[i,j].ub = 0
                
    m.addConstr(gp.quicksum(m._S) == 1)
    
    m.addConstrs(m._S[i] <= m._X[i] + m._Y[i] for i in G.nodes)

    m.addConstrs(Gen[i,j] <= r*m._S[i] for (i,j) in DP.edges)
        
    m.addConstrs( Gen[i,j] + gp.quicksum(F[i,u,j] for u in DG.neighbors(j)) - gp.quicksum(F[i,j,u] for u in DG.neighbors(j)) == m._X[j] + m._S[j] for (i,j) in DP.edges)             
        
    m.addConstrs( gp.quicksum(F[i,u,j] for u in DG.neighbors(j)) <= r * (m._X[j] + m._S[j]) for (i,j) in DP.edges)