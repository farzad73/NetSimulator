from buffer import Buffer


class OpenflowSwitch(object):
    """A SDN switch"""
    def __init__(self, name):
        self.name = name
        self.table = []
        self.buffer = Buffer(name)
        self.counter = 0

    @staticmethod
    def send_packet(packet, recipient):
        recipient.buffer.put(packet)

    def handle_packet(self):
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
                self.counter += 1


class Host(object):
    """A SDN switch"""
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.buffer = Buffer(name)
