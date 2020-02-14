from buffer import Buffer
from collections import deque

TABLE_SIZE = 10


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

    def handle_packet(self, controller):
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

            if not flag:
                self.counter += 1
                controller.update_table(packet)


class Host(object):
    """A SDN switch"""
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.buffer = Buffer(name)
