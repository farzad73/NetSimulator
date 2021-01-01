import time

from buffer import Buffer
from collections import deque


"""
In this module, we modeled the network equipment, which is divided into two categories: SDN switches and hosts.
"""

HOP_COUNT_LIMITATION = 4


class OpenflowSwitch(object):
    """A SDN switch"""

    def __init__(self, name):
        self.name = name
        self.table = deque([])
        self.switch_star_rule = dict()
        self.host_star_rule = dict()
        self.buffer = Buffer(name)
        self.counter = 0

    def add_rule(self, rule):
        self.table.appendleft(rule)

    def add_switch_star_rule(self, rule):
        self.switch_star_rule = rule

    def add_host_star_rule(self, rule):
        self.host_star_rule = rule

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
                    rule['match_count'] += 1
                    rule['start_time'] = time.time()

                    OpenflowSwitch.send_packet(packet, rule['next_hop'])
                    flag = True
                    break

            if not flag:
                if self.switch_star_rule and packet['hop_count'] < HOP_COUNT_LIMITATION:
                    packet['hop_count'] += 1
                    OpenflowSwitch.send_packet(packet, self.switch_star_rule['next_hop'])

                elif self.host_star_rule and packet['destination'] == self.host_star_rule['next_hop'].ip:
                    OpenflowSwitch.send_packet(packet, self.switch_star_rule['next_hop'])

                else:
                    self.counter += 1
                    # controller.update_table(packet)

    def remove_rule(self):
        seq = [x['start_time'] for x in self.table]
        min_index = seq.index(min(seq))
        del self.table[min_index]


class Host(object):

    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.buffer = Buffer(name)
