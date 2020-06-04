from buffer import Buffer
from collections import Counter

TABLE_SIZE = 81


class Controller:
    def __init__(self, net):
        self.network = net
        self.buffer = Buffer('controller')
        self.all_rules = dict()
        self.remaining_rules = dict()
        self.count_outputs = dict()
        for switch in self.network.switches():
            self.all_rules[switch] = []
            self.remaining_rules[switch] = []
            self.count_outputs[switch] = []

    def get_name_from_ip(self, ip):
        """Extract name of host from ip"""
        for h in self.network.hopts:
            if self.network.hopts[h]['ip'] == ip:
                return h

    def create_rules(self):
        """Create an empty dictionary for all rules that should be put on the switches"""

        # Create rules based on the shortest path in the network
        for sp in self.network.shortestPath():
            src = sp[0]
            dst = sp[-1]

            for i in range(1, len(sp) - 1):

                rule = {
                    'actions': {'OutPort': None},
                    'match': {
                        'dst': self.network.hopts[dst]['ip'],
                        'src': self.network.hopts[src]['ip'],
                        'in_port': None
                    },
                    'next_hop': None,
                    'match_count': 0
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

                self.all_rules[sp[i]].append(rule)

    @staticmethod
    def max_count_output(remaining_rules):
        count_outputs = {}
        max_outputs = {}
        for sw in remaining_rules:
            count_outputs[sw] = []
            for rule in remaining_rules[sw]:
                count_outputs[sw].append(rule.get('actions').get('OutPort'))

            try:
                max_outputs[sw] = max(k for k, v in Counter(count_outputs[sw]).items())
            except:
                continue

        return max_outputs

    def fill_table(self, switches):
        # Fill the table of each switch
        self.create_rules()
        for sw in switches:
            for rule in self.all_rules.get(sw):
                if len(switches[sw].table) < TABLE_SIZE - 1:
                    switches[sw].add_rule(rule)
                else:
                    self.remaining_rules[sw].append(rule)

        max_output = self.max_count_output(self.remaining_rules)
        for sw in switches:
            if max_output.get(sw):
                rule = {
                    'actions': {'OutPort': max_output[sw]},
                    'next_hop': None,
                    'match_count': 0
                }
                for node in self.network.nodes(data=True):
                    if node[0] == sw:
                        next_match = node[1].get('ports').get(max_output[sw])[0]

                        for item in self.network.nodes(data=True):
                            if item[0] == next_match:
                                rule['next_hop'] = item[1].get('obj')

                switches[sw].add_star_rule(rule)

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
                            if rule not in switch_obj.table:
                                switch_obj.add_rule(rule)
