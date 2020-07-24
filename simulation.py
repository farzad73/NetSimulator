from OpenflowNetwork import Topo
from OpenflowController import Controller
from FlowGenerator import FlowGenerator
import random
import networkx as nx

# Initialize graph from internet topology zoo
sdn_switch_num = 4
topology = 'gml-files/AttMpls.gml'
graph = nx.read_gml(topology)

# Draw graph according to the longitude and latitude of each node
positions = {}
for node in graph.nodes():
    positions[node] = (graph._node[node]['Latitude'], graph._node[node]['Longitude'])

net = Topo()

# Add switches to topology
switches = {}
for node in graph.nodes:
    if graph._node[node]['type'] == 'switch':
        switches.update({node: net.addSwitch(node)})

hosts = {}
# Add hosts to topology
for node in graph.nodes:
    if graph._node[node]['type'] == 'host':
        hosts.update({node: net.addHost(node, ip=graph._node[node]['ip'])})

# Add links to topology
for edge in graph.edges:
    net.addLink(edge[0], edge[1])

# net = Topo()
#
# switches = {'s1': net.addSwitch('s1'),
#             's4': net.addSwitch('s4'),
#             's5': net.addSwitch('s5'),
#             's2': net.addSwitch('s2'),
#             's3': net.addSwitch('s3')}
#
# # Add hosts to topology
# hosts = {'h2': net.addHost('h2', ip='10.0.0.2'),
#          'h5': net.addHost('h5', ip='10.0.0.5'),
#          'h1': net.addHost('h1', ip='10.0.0.1'),
#          'h4': net.addHost('h4', ip='10.0.0.4'),
#          'h3': net.addHost('h3', ip='10.0.0.3')}
#
# # Add links to topology
# net.addLink('s1', 's2')
# net.addLink('s2', 's4')
# net.addLink('s2', 's5')
# net.addLink('s5', 's3')
# net.addLink('s1', 's3')
# net.addLink('s3', 's4')
# net.addLink('s4', 's5')
# net.addLink('h4', 's1')
# net.addLink('s2', 'h5')
# net.addLink('s3', 'h3')
# net.addLink('s4', 'h1')
# net.addLink('s5', 'h2')

# net.showGraph()

# net.showGraph()
# print("===================== lopts =======================")
# print(net.lopts)
#
# print("===================== sopts =======================")
# print(net.sopts)
#
# print("===================== hopts =======================")
# print(net.hopts)
#
# print("=================== Show graph =====================")
# net.showGraph()


# Create all rules for the network switches
controller = Controller(net=net, switches=switches)
controller.fill_table()

print(net.sopts)

for sw in switches:
    print(switches[sw].name, ' -> ', switches[sw].switch_star_rule, switches[sw].host_star_rule)

# Print table information of each switches
print('================ Table information of each switches ================')
for sw in switches:
    print(switches[sw].name, ' -> ', len(switches[sw].table) + 1, ' -> ', switches[sw].table)

# sum_of_shortest_path_length = 0
# print('#### number of shortest path --------> ', len(net.all_shortest_path()))
#
# for sh in net.all_shortest_path():
#     sum_of_shortest_path_length += len(sh)
# print('#### sum of shortest length --------> ', sum_of_shortest_path_length)

# Create list of host ips
hosts_ips = []
for host in net.hopts:
    hosts_ips.append(net.hopts[host]['ip'])

# Generate random flows
flows = FlowGenerator.generate_flow(10000, 1, hosts_ips)


def get_name_from_ip(ip):
    for h in hosts:
        if hosts[h].ip == ip:
            return hosts[h].name


def find_connected_switch(host_name):
    return net.hopts[host_name]['ports'][0][0]


for packet in flows:
    src_host = get_name_from_ip(packet['source'])
    if src_host:
        src_switch = find_connected_switch(src_host)
        switches[src_switch].buffer.put(packet)
    else:
        random_switch = random.choice(net.switches())
        switches[random_switch].buffer.put(packet)


# print('================ Buffer information of each switch ================')
# for sw in switches:
#     print(sw, " -> ", 'The number of packets sent to the controller:', switches[sw].counter, ' buffer size: ',
#           switches[sw].buffer.__len__())


def check_all_switches_is_empy():
    """check the buffer is empty or not"""
    for sw in switches:
        if not switches[sw].buffer.is_empty():
            return False
    return True


while not check_all_switches_is_empy():
    for switch in switches:
        switches[switch].handle_packet(controller, net)

controller_packets = 0
print('============ Buffer information of each switch after simulation ===========')
for sw in switches:
    print(sw, " -> ", switches[sw].counter, " - ", switches[sw].buffer.__len__())
    controller_packets += switches[sw].counter

successful_packets = 0
# print('============ Buffer information of each host after simulation ===========')
for host in hosts:
    # print(host, " -> ", hosts[host].buffer.__len__())
    successful_packets += hosts[host].buffer.__len__()

print('The total number of packets sent to the controller: ', controller_packets)
print('The total number of packets that successfully reached their destination: ', successful_packets)

# Print table information of each switches
print('================ Table information of each switches ================')
for sw in switches:
    print(switches[sw].name, ' -> ', len(switches[sw].table) + 1, ' -> ', switches[sw].table)
