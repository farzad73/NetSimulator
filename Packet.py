class StandardPacket:
    """A packet for sending information between hosts on the network.

    Attributes:
        identifier: the packet ID that a pair of Payload and ACK packets share
        flow_id: The flow that sent the packet
        source: The host that sent the packet
        destination: The host to which the packet was sent
    """

    def __init__(self, identifier, flow_id, source, destination):
        self.identifier = identifier
        self.flow_id = flow_id
        self.source = source
        self.destination = destination

    def __str__(self):
        return ("PayloadPacket #" + str(self.identifier) + "\n"
                "flowID:        " + self.flow_id + "\n"
                "source:        " + self.source.identifier + "\n"
                "destination:   " + self.destination.identifier )
