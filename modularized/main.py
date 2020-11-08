import gurobipy as gp
from gurobipy import GRB 
import networkx as nx
from networkx.algorithms import approximation
from matplotlib import pylab as pl
import time

import math

import read
import flow
import k_core
#import ordering

#################
# Instances
#################
instances = {
    'karate', 'chesapeake', 'dolphins', 'lesmis', 'polbooks',
    'adjnoun', 'football', 'jazz', 'cn', 'cm',
    'netscience', 'polblogs', 'email', 'data'
    }
##########################
# Get parameters from user
##########################
# what is k?
k = 3

# Is the k-core problem anchored?
anchored = True 

# If the k-core problem is anchored k-core, then what is the budget b?
b = 20

# Is the k-core problem radius bounded?
radius_bounded = True

# If the k-core problem is radius bounded, then what is the radius bound r?
r = 2

# Connectivity formulation?
connectivity = 'flow'

# What is the instance?
instance = 'dolphins'

######################
# Start solving model
######################

ext = "C:/s_club_data/"

F = read.imp_dimacs(ext + instance + ".graph")

G = nx.convert_node_labels_to_integers(F, first_label=0, ordering='default', label_attribute=None)

m = gp.Model()

m._X = m.addVars(G.nodes, vtype=GRB.BINARY, name="x")
        
m._Y = m.addVars(G.nodes, vtype=GRB.BINARY, name="y")

k_core.build_k_core(G, m, anchored, k, b)

if radius_bounded and connectivity == 'flow':
    flow.build_flow(G, m, r)

m.optimize()

if m.status == GRB.OPTIMAL or m.status==GRB.TIME_LIMIT:
    cluster = [i for i in G.nodes if m._X[i].x > 0.5 or m._Y[i].x > 0.5]
    SUB = G.subgraph(cluster)
    for i in G.nodes:
        if m._S[i].x > 0.5: 
            print("Root is ", i)    
    print("# of vertices in G: ", len(G.nodes))
    print("Is it connected? ", nx.is_connected(SUB))
    print("Diameter? ", nx.diameter(SUB))
    pl.figure()
    nx.draw_networkx(SUB)
    pl.show()

        