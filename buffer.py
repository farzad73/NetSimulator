import queue


class Buffer:
    """A buffer that holds packets that are waiting to send.

    Attributes:
        name: the router buffer belongs to
        queue: the Queue of packets waiting in the buffer
    """

    def __init__(self, name):
        self.name = name
        self.queue = queue.Queue()

    """Places a packet in the buffer."""

    def put(self, packet):
        self.queue.put(packet)

    """Retrieves the next packet from the buffer in FIFO order."""

    def get(self):
        packet = self.queue.get_nowait()
        return packet

    def __len__(self):
        return self.queue.qsize()

    def is_empty(self):
        return self.queue.empty()
