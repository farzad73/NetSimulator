from OpenflowNetwork import Topo
from OpenflowController import Controller
from FlowGenerator import FlowGenerator
import random
import threading


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


print("===================== lopts =======================")
print(net.lopts)

print("===================== sopts =======================")
print(net.sopts)

print("===================== hopts =======================")
print(net.hopts)

print("===================== Show graph =======================")
# net.showGraph()

# Create all rules for the network switches
controller = Controller(net)
rules = controller.create_rules()


# Fill the table of each switch
for sw in switches:
    switches[sw].table = rules.get(sw)

for sw in switches:
    print(switches[sw].name)
    print(switches[sw].table)
    print(len(switches[sw].table))

# Create list of host ips
hosts_ips = []
for host in net.hopts:
    hosts_ips.append(net.hopts[host]['ip'])

# Generate random flows
flows = FlowGenerator.generate_flow(100, 0.8, hosts_ips)


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

for sw in switches:
    print(sw, " -> ", switches[sw].counter, " - ", switches[sw].buffer.__len__())

print('==========================')

print(switches['s1'].buffer.queue.queue)


def check_all_switches_is_empy():
    for switch in switches:
        if not switches[switch].buffer.is_empty():
            return False
    return True

while not check_all_switches_is_empy():
    for switch in switches:
        switches[switch].handle_packet()


# for sw in switches:
#     switches[sw].handle_packet()

# t1 = threading.Thread(target=switches['s1'].handle_packet)
# t2 = threading.Thread(target=switches['s2'].handle_packet)
# t3 = threading.Thread(target=switches['s3'].handle_packet)
# t4 = threading.Thread(target=switches['s4'].handle_packet)
# t5 = threading.Thread(target=switches['s5'].handle_packet)
#
# t1.start()
# t2.start()
# t3.start()
# t4.start()
# t5.start()

for sw in switches:
    print(sw, " -> ", switches[sw].counter, " - ", switches[sw].buffer.__len__())

for host in hosts:
    print(host, " -> ", hosts[host].buffer.__len__())

# for sw in switches:
#     switches[sw].table = all_rules.get(sw)
#
# print(switches['s1'].table)
