from OpenflowNetwork import Topo
from OpenflowController import Controller
from FlowGenerator import FlowGenerator
import random

net = Topo()

# Add switches to topology
switches = {'s1': net.addSwitch('s1'),
            's4': net.addSwitch('s4'),
            's5': net.addSwitch('s5'),
            's2': net.addSwitch('s2'),
            's3': net.addSwitch('s3')}

# Add hosts to topology
hosts = {'h2': net.addHost('h2', ip='10.0.0.2'),
         'h5': net.addHost('h5', ip='10.0.0.5'),
         'h1': net.addHost('h1', ip='10.0.0.1'),
         'h4': net.addHost('h4', ip='10.0.0.4'),
         'h3': net.addHost('h3', ip='10.0.0.3')}

# Add links to topology
net.addLink('s1', 's2')
net.addLink('s2', 's4')
net.addLink('s2', 's5')
net.addLink('s5', 's3')
net.addLink('h4', 's1')
net.addLink('s2', 'h5')
net.addLink('s3', 'h3')
net.addLink('s5', 'h2')
net.addLink('s4', 'h1')

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
controller = Controller(net)
rules = controller.create_rules()

# Fill the table of each switch
for sw in switches:
    for rule in rules.get(sw):
        switches[sw].add_rule(rule)

# Print table information of each switches
print('================ Table information of each switches ================')
for sw in switches:
    print(switches[sw].name, ' -> ', len(switches[sw].table_queue), ' -> ', switches[sw].table_queue)

# Create list of host ips
hosts_ips = []
for host in net.hopts:
    hosts_ips.append(net.hopts[host]['ip'])

# Generate random flows
flows = FlowGenerator.generate_flow(1000, 0.8, hosts_ips)
print(flows)


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

print('================ Buffer information of each switch ================')
for sw in switches:
    print(sw, " -> ", 'The number of packets sent to the controller:', switches[sw].counter, ' buffer size: ',
          switches[sw].buffer.__len__())


def check_all_switches_is_empy():
    for sw in switches:
        if not switches[sw].buffer.is_empty():
            return False
    return True


while not check_all_switches_is_empy():
    for switch in switches:
        switches[switch].handle_packet(controller, net)
        print('============ Buffer information of each switch after simulation ===========')
        for sw in switches:
            print(sw, " -> ", switches[sw].counter, " - ", switches[sw].buffer.__len__())
        print('============ Buffer information of each host after simulation ===========')
        for host in hosts:
            print(host, " -> ", hosts[host].buffer.__len__())

controller_packets = 0
print('============ Buffer information of each switch after simulation ===========')
for sw in switches:
    print(sw, " -> ", switches[sw].counter, " - ", switches[sw].buffer.__len__())
    controller_packets += switches[sw].counter

successful_packets = 0
print('============ Buffer information of each host after simulation ===========')
for host in hosts:
    print(host, " -> ", hosts[host].buffer.__len__())
    successful_packets += hosts[host].buffer.__len__()

print('The total number of packets sent to the controller: ', controller_packets)
print('The total number of packets that successfully reached their destination: ', successful_packets)
