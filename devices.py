from buffer import Buffer
from collections import deque
import random

TABLE_SIZE = 10
HOP_COUNT_LIMITATION = 2


class OpenflowSwitch(object):
    """A SDN switch"""

    def __init__(self, name):
        self.name = name
        self.table_queue = deque([])
        self.buffer = Buffer(name)
        self.counter = 0

    def add_rule(self, rule):
        if len(self.table_queue) < TABLE_SIZE:
            self.table_queue.appendleft(rule)
        else:
            self.table_queue.pop()
            self.table_queue.appendleft(rule)

    @staticmethod
    def send_packet(packet, recipient):
        recipient.buffer.put(packet)

    def handle_packet(self, controller, net):
        """Update the routing table, and forward the routing packet over the proper links, if necessary."""

        if not self.buffer.is_empty():
            packet = self.buffer.get()

            flag = False

            for rule in self.table_queue:
                src = rule['match']['src']
                dst = rule['match']['dst']

                if packet['source'] == src and packet['destination'] == dst:
                    OpenflowSwitch.send_packet(packet, rule['next_hop'])
                    flag = True
                    break

            # When we do not send packets to the controller
            if not flag:
                if packet['hop_count'] < HOP_COUNT_LIMITATION:
                    packet['hop_count'] += 1
                    random_next = random.choice(list(net.sopts[self.name].values()))
                    next_hop_info = net.g.node.get(random_next[0])
                    next_hop_obj = next_hop_info.get('obj')
                    if next_hop_info.get('isSwitch') is True:
                        OpenflowSwitch.send_packet(packet, next_hop_obj)

                    elif packet['destination'] == next_hop_obj.ip:
                        OpenflowSwitch.send_packet(packet, next_hop_obj)

                else:
                    self.counter += 1
                    controller.update_table(packet)

            # if not flag:
            #     self.counter += 1
            #     controller.update_table(packet)


class Host(object):
    """A SDN switch"""

    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.buffer = Buffer(name)
