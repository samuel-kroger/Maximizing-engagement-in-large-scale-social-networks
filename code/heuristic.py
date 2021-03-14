def anchored_k_core(graph, k, anchors):
	for anchor in anchors:
		graph.nodes[anchor]['anchor'] = True
	output = []
	n = len(graph.nodes())

	deg = [0] * n
	vert = [0] * n
	pos = [0] * n
	md = 0

	for v in range(0, n):
		d = graph.degree(v)
		deg[v] = d

		if d > md:
			md = d


	binn = [0] * (md + 1)


	for v in range(0, n):

		binn[deg[v]] += 1

	start = 0

	for d in range(0, md + 1):
		num = binn[d]
		binn[d] = start
		start += num


	for v in range(0, n):
		pos[v] = binn[deg[v]]
		vert[pos[v]] = v
		binn[deg[v]] += 1

	for d in range(md, 0, -1):
		binn[d] = binn[d-1]
	binn[0] = 1

	for i in range(0, n):
		v = vert[i]
		if not graph.nodes[v]['anchor']:


			for u in graph.neighbors(v):

				if not graph.nodes[u]['anchor']:

					if deg[u] > deg[v]:
						du = deg[u]
						pu = pos[u]
						pw = binn[du]

						w = vert[pw]
						if u != w:
							pos[u] = pw
							vert[pu] = w
							pos[w] = pu
							vert[pw] = u
						binn[du] += 1
						deg[u] -= 1

	for i in range(0, len(deg)):
		if deg[i] >= k:
			output.append(i)
	list_of_nodes = []
	for v in graph.subgraph(output).nodes():
		list_of_nodes.append(v)
	for anchor in anchors:
		graph.nodes[anchor]['anchor'] = False
	return(list_of_nodes)


def warm_start(G, k, b, time_for_warm_start):

	x_vals = []
	y_vals = []
	best = []


	for i in G.nodes():
			if G.degree[i] < k:
				y_vals.append(i)
			else:
				x_vals.append(i)


	timer = 0
	for node in y_vals:
		#if G.degree(node) <= 5:

		result = anchored_k_core(G, k, [node])
		current = [node, result]


		best.append(current)
		if timer >= time_for_warm_start:
			break

	value_of_anchor = []
	anchor = []
	nodes_in_k_core = []

	for fixing in best:
		value_of_anchor.append(len(fixing[1]))
		anchor.append(fixing[0])
		nodes_in_k_core.append(fixing[1])

	b_best_fixings = sorted(zip(value_of_anchor, anchor, nodes_in_k_core), reverse = True)[:b]

	dead_y = []
	anchors_in_b_best = []
	for fixing in b_best_fixings:

		anchors_in_b_best.append(fixing[1])


	for fixing in best:
		if fixing[0] not in anchors_in_b_best:
			dead_y.append(fixing[0])

	return [b_best_fixings, dead_y]