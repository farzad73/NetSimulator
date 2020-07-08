from buffer import Buffer
from collections import deque

HOP_COUNT_LIMITATION = 100


class OpenflowSwitch(object):
    """A SDN switch"""

    def __init__(self, name):
        self.name = name
        self.table = deque([])
        self.star_rule = dict()
        self.buffer = Buffer(name)
        self.counter = 0

    def add_rule(self, rule):
        self.table.appendleft(rule)

    def add_star_rule(self, rule):
        self.star_rule = rule

    @staticmethod
    def send_packet(packet, recipient):
        recipient.buffer.put(packet)

    def handle_packet(self, controller, net):
        """Update the routing table, and forward the routing packet over the proper links, if necessary."""

        if not self.buffer.is_empty():
            packet = self.buffer.get()

            flag = False

            for rule in self.table:
                src = rule['match']['src']
                dst = rule['match']['dst']

                if packet['source'] == src and packet['destination'] == dst:
                    OpenflowSwitch.send_packet(packet, rule['next_hop'])
                    flag = True
                    break

            if not flag:
                if self.star_rule and packet['hop_count'] < HOP_COUNT_LIMITATION:
                    packet['hop_count'] += 1
                    next_hop_info = net.g.node.get(self.star_rule['next_hop'].name)

                    if next_hop_info.get('isSwitch') is True:
                        OpenflowSwitch.send_packet(packet, self.star_rule['next_hop'])
                        flag = True

                    elif packet['destination'] == self.star_rule['next_hop'].ip:
                        OpenflowSwitch.send_packet(packet, self.star_rule['next_hop'])
                        flag = True

            if not flag:
                self.counter += 1
                controller.update_table(packet)

    def remove_rule(self):

        seq = [x['start_time'] for x in self.table]
        min_index = seq.index(min(seq))
        del self.table[min_index]


class Host(object):
    """A SDN switch"""

    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.buffer = Buffer(name)
