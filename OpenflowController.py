from buffer import Buffer

TABLE_SIZE = 10


class Controller:
    def __init__(self, net):
        self.network = net
        self.buffer = Buffer('controller')

    # Extract name of host from ip
    def get_name_from_ip(self, ip):
        for h in self.network.hopts:
            if self.network.hopts[h]['ip'] == ip:
                return h

    def create_rules(self):
        # Create an empty dictionary for all rules that should be put on the switches
        all_rules = {}
        for switch in self.network.switches():
            all_rules[switch] = []

        # Create rules based on the shortest path in the network
        for sp in self.network.shortestPath():
            src = sp[0]
            dst = sp[-1]

            for i in range(1, len(sp) - 1):

                rule = {
                    "actions": {'OutPort': None},
                    "match": {
                        "dst": self.network.hopts[dst]['ip'],
                        "src": self.network.hopts[src]['ip'],
                        "in_port": None
                    },
                    'next_hop': None
                }

                opts = self.network.sopts[sp[i]]
                before = sp[i - 1]
                after = sp[i + 1]
                for key in opts:
                    if opts[key][0] == before:
                        rule['match']['in_port'] = key
                    if opts[key][0] == after:
                        rule['actions'].update({'OutPort': key})

                        for node in self.network.nodes(data=True):
                            if node[0] == after:
                                rule['next_hop'] = node[1].get('obj')
                all_rules[sp[i]].append(rule)
        return all_rules

    def update_table(self, packet):

        src_name = self.get_name_from_ip(packet['source'])
        dst_name = self.get_name_from_ip(packet['destination'])

        for sp in self.network.shortestPath():
            if sp[0] == src_name and sp[-1] == dst_name:

                for i in range(1, len(sp) - 1):

                    rule = {
                        "actions": {'OutPort': None},
                        "match": {
                            "dst": packet['destination'],
                            "src": packet['source'],
                            "in_port": None
                        },
                        'next_hop': None
                    }

                    opts = self.network.sopts[sp[i]]
                    before = sp[i - 1]
                    after = sp[i + 1]

                    for key in opts:
                        if opts[key][0] == before:
                            rule['match']['in_port'] = key
                        if opts[key][0] == after:
                            rule['actions'].update({'OutPort': key})

                            for node in self.network.nodes(data=True):
                                if node[0] == after:
                                    rule['next_hop'] = node[1].get('obj')
                                    break

                    for node_info in self.network.nodes(data=True):
                        if node_info[0] == sp[i]:
                            switch_obj = node_info[1]['obj']
                            if rule not in switch_obj.table_queue:
                                switch_obj.add_rule(rule)
