import gurobipy as grb
import operator
#import heuristic
import classes
import time

def fractional_callback(m, where):

	if where != grb.GRB.Callback.MIPNODE:
		return
	if m.cbGet(grb.GRB.Callback.MIPNODE_STATUS) != grb.GRB.OPTIMAL:
		return

	#Get current fractional solution
	x_sol = m.cbGetNodeRel(m._X)
	y_sol = m.cbGetNodeRel(m._Y)

	#print('x_sol: ', x_sol)
	#print('y_sol: ', y_sol)

	G = m._G

	k = m._k
	b = m._b
	R = m._R

	b_best_anchors = list(dict(sorted(y_sol.iteritems(), key=operator.itemgetter(1), reverse=True)[:10*b]).keys())

	#THESE NEEDS TO BE UPDATED
	resulting_k_core = heuristic.anchored_k_core(G, k, b_best_anchors)
	'''
	outside_k_core = [vertex for vertex in R if vertex not in resulting_k_core]

	best_out = 0
	best_vertex = -1

	for i in outside_k_core:
		if x_sol[i] + y_sol[i] > best_out:
			best_out = x_sol[i] + y_sol[i]
			best_vertex = i
	'''
	threshold = b - sum(y_sol[i] for i in b_best_anchors)

	for vertex in R:
		if vertex not in resulting_k_core:
			if x_sol[vertex] + y_sol[vertex] > threshold:
				print('VIOLATION: ', sum(y_sol[i] for i in b_best_anchors) + x_sol[vertex] + y_sol[vertex] - b)

				m.cbLazy(grb.quicksum(m._Y[i] for i in b_best_anchors) + m._X[vertex] +m._Y[vertex] <= b)
				break







	'''
	if sum(y_sol[i] for i in b_best_anchors) + x_sol[best_vertex] + y_sol[best_vertex] > b:
		print('VIOLATION: ', sum(y_sol[i] for i in b_best_anchors) + x_sol[best_vertex] + y_sol[best_vertex] - b)

		m.cbLazy(grb.quicksum(m._Y[i] for i in b_best_anchors) + m._X[best_vertex] +m._Y[best_vertex] <= b)
	'''



