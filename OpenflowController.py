class Controller:
    def __init__(self, net):
        self.network = net

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
