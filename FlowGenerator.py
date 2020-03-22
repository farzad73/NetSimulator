import random
import ipaddress


class FlowGenerator:
    @staticmethod
    def generate_flow(count, percentage, host_ips):
        flows = []

        for _ in range(int(count * percentage)):
            src, dst = random.sample(host_ips, 2)
            flows.append({'source': src, 'destination': dst, 'hop_count': 0})

        for _ in range(int(count * (1 - percentage) + 1)):
            bits = random.getrandbits(32)
            s = str(ipaddress.IPv4Address(bits))
            bits = random.getrandbits(32)
            d = str(ipaddress.IPv4Address(bits))
            flows.append({"source": s, "destination": d, 'hop_count': 0})

        random.shuffle(flows)

        return flows
