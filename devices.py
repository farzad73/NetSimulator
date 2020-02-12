from buffer import Buffer


class OpenflowSwitch(object):
    """A SDN switch"""
    def __init__(self, name):
        self.name = name
        self.table = []
        self.buffer = Buffer(name)
        self.counter = 0

    def handle_packet(self, packet):
        """Update the routing table, and forward the routing packet over the proper links, if necessary."""

        for rule in self.table:
            src = rule['match']['src']
            dst = rule['match']['dst']

            if packet['source'] == src and packet['destination'] == dst:
                OpenflowSwitch.send_packet(packet, rule['next_hop'])
                return
        self.counter += 1

    @staticmethod
    def send_packet(packet, recipient):
        recipient.buffer.put(packet)


class Host(object):
    """A SDN switch"""
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.buffer = Buffer(name)