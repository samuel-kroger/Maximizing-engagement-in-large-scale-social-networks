import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches

def pretty_plot(graph, nodes_in_k_core = [], anchored_nodes = [], center = -1, plot_now = True, k = 0, b  = 0, r = 0):
	color_dict = {i : 'indianred' for i in graph.nodes()}
	color_dict.update({i : 'royalblue' for i in nodes_in_k_core})
	color_dict.update({i : 'y' for i in anchored_nodes})
	if center != -1:
		color_dict.update({center : 'purple'})


	color_values = [color_dict.get(node) for node in graph.nodes()]

	plt.title('Radius {} Anchored {}-core with b = {}'.format(r,k,b))
	nx.draw(graph, with_labels = True,  node_color = color_values, node_size = 500)
	first_legend = mpatches.Patch(color='indianred', label='Nodes not in the {}-core'.format(k))
	second_legend = mpatches.Patch(color='royalblue', label='Nodes in the {}-core'.format(k))
	third_legend = mpatches.Patch(color='y', label='Anchored Nodes')
	fourth_legend = mpatches.Patch(color='purple', label='The chosen center')
	plt.legend(handles=[first_legend, second_legend, third_legend, fourth_legend])
	if plot_now == True:
		plt.show()