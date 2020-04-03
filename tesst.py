import networkx as nx
import matplotlib.pyplot as plt
import operator

# Initialize graph from internet topology zoo
sdn_switch_num = 4
topology = 'gml-files/AttMpls.gml'
graph = nx.read_gml(topology)


# Draw graph according to the longitude and latitude of each node
positions = {}
for node in graph.nodes():
    positions[node] = (graph._node[node]['Latitude'], graph._node[node]['Longitude'])
nx.draw(graph, positions, with_labels=True)
plt.show()
# print(graph.nodes)

# Find minimum spanning edges by Kruskal’s algorithm
stg = nx.minimum_spanning_tree(graph)
positions = {}
for node in stg.nodes():
    positions[node] = (stg._node[node]['Latitude'], stg._node[node]['Longitude'])
nx.draw(stg, positions, with_labels=True)
plt.show()

print(stg.nodes)
print(stg.edges)


""" Find the shortest paths """
shortest_pathes = nx.shortest_path(stg)
shortest_paths = []
for source in shortest_pathes:
    for destination in shortest_pathes[source]:
        if destination != source:
            shortest_paths.append(shortest_pathes[source][destination])
print(shortest_paths)
#
# # Add rules to table of switches according to shortest paths of graph
# for sp in shortest_paths:
#     for switch in sp:
#
#         pass
#         # switches[switch].table_dict += {'src': ip_address(''), 'dst': ip_address(''), 'action': ''}

# max_bc = []
# upgrade_to_sdn = []
# bc = nx.betweenness_centrality(graph)
# sorted_bc = sorted(bc.items(), key=operator.itemgetter(1))
# print(sorted_bc)
#
# count = 1
# while count <= sdn_switch_num:
#     max_bc.append(sorted_bc[-count])
#     count += 1
# print(max_bc)

# while BUDGET > 0:
#     bc = nx.betweenness_centrality(g)
#     max_bc = max(bc, key = bc.get)
#     sdn_nodes.append(max_bc)
#     g.remove_node(max_bc)
#     BUDGET -= 1
#
#     # nx.draw(g, positions, with_labels=True)
#     # plt.show()

# upgrade_to_sdn = list(dict(max_bc).keys())
# print(upgrade_to_sdn)
#
# graph = nx.read_gml(topology)
# shortest_pathes = nx.shortest_path(graph)
#
# sps = []
# for source in shortest_pathes:
#     for destination in shortest_pathes[source]:
#         sps.append(shortest_pathes[source][destination])
#
# counter = 0
# for sp in sps:
#     for node in upgrade_to_sdn:
#         if node in sp:
#             counter += 1
#             break
#
# shortest_path_coverage = counter / len(sps)
# print("The shortest path coverage is: " + str(shortest_path_coverage))
#
# sdn_positions = []
# for sdn_node in upgrade_to_sdn:
#     sdn_positions.append((graph._node[sdn_node]['Latitude'], graph._node[sdn_node]['Longitude']))
#
# controller_position = [sum(x) / count for x in zip(*sdn_positions)]
# print('controller position is: ' + controller_position.__str__())
