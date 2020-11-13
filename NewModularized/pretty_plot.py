import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches

def pretty_plot(graph, nodes_in_k_core = [], anchored_nodes = [], center = [], plot_now = True, k = 0, b  = 0):

	color_dict = {i : 'indianred' for i in range(len(graph.nodes()))}
	color_dict.update({nodes_in_k_core[i] : 'royalblue' for i in range(len(nodes_in_k_core))})
	color_dict.update({anchored_nodes[i] : 'y' for i in range(len(anchored_nodes))})
	color_dict.update({center[i] : 'purple' for i in range(len(center))})


	color_values = [color_dict.get(node) for node in graph.nodes()]

	plt.title('Anchored {}-core with b = {}'.format(k,b))
	nx.draw(graph, with_labels = True,  node_color = color_values, node_size = 1000)
	first_legend = mpatches.Patch(color='indianred', label='Nodes not in the {}-core'.format(k))
	second_legend = mpatches.Patch(color='royalblue', label='Nodes in the {}-core'.format(k))
	third_legend = mpatches.Patch(color='y', label='Anchored Nodes')
	fourth_legend = mpatches.Patch(color='purple', label='The chosen center')
	plt.legend(handles=[first_legend, second_legend, third_legend, fourth_legend])
	if plot_now == True:
		plt.show()