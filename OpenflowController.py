import time

from buffer import Buffer
import networkx as nx

TABLE_SIZE = 81


class Controller():
    def __init__(self, net):
        self.network = net
        self.copy_graph = self.network.g.convertTo(nx.MultiGraph)

        self.buffer = Buffer('controller')
        self.all_rules = dict()
        self.remaining_rules = dict()
        self.count_outputs = dict()
        self.dontFit = 0
        self.allRulesNumber = 0
        self.embedRules = 0

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
        for sp in self.network.all_shortest_path():
            src = sp[0]
            dst = sp[-1]

            for i in range(1, len(sp) - 1):
                self.allRulesNumber += 1
                rule = {
                    'actions': {'OutPort': None},
                    'match': {
                        'dst': self.network.hopts[dst]['ip'],
                        'src': self.network.hopts[src]['ip'],
                        'in_port': None
                    },
                    'next_hop': None,
                    'match_count': 0,
                    'start_time': time.time()
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
    def most_frequent(list):
        """find most frequent element in a list"""
        counter = 0
        num = list[0]

        for i in list:
            curr_frequency = list.count(i)
            if curr_frequency > counter:
                counter = curr_frequency
                num = i

        return num

    def most_output_ports(self, remaining_rules):
        """Calculate the maximum frequency of output ports and the list of remaining destinations"""
        output_ports = {}
        max_outputs = {}
        for sw in remaining_rules:
            output_ports[sw] = []

            for rule in remaining_rules[sw]:
                output_ports[sw].append(rule.get('actions').get('OutPort'))
            try:
                max_outputs[sw] = {'max_output': self.most_frequent(output_ports[sw])}
            except:
                continue

        return max_outputs

    def endpoints(self, remaining_rules):
        """Calculating the source and destination of the remaining rules"""

        endpoints = []
        for sw in remaining_rules:
            for rule in remaining_rules[sw]:
                endpoints.append((self.get_name_from_ip(rule.get('match', {}).get('src')), self.get_name_from_ip(rule.get('match', {}).get('dst'))))

        endpoints = list(dict.fromkeys(endpoints))
        return endpoints

    def fill_table(self, switches):
        """
            Fill the table of each switch
            This function enters the rules as long as the table has capacity, otherwise it enters the remaining_rules.
        """

        self.create_rules()
        for sw in switches:
            for rule in self.all_rules.get(sw):
                if len(switches[sw].table) < TABLE_SIZE - 1:
                    switches[sw].add_rule(rule)
                else:
                    self.dontFit += 1
                    self.remaining_rules[sw].append(rule)

        print('Number of all rules ->', self.allRulesNumber)
        print('Rules that does not fit in flow tables ->', self.dontFit)

        max_output = self.most_output_ports(remaining_rules=self.remaining_rules)

        """Add Star Star rule to switch tables"""
        for sw in switches:
            if max_output.get(sw):
                rule = {
                    'actions': {'OutPort': max_output[sw].get('max_output')},
                    'next_hop': None,
                    'match_count': 0
                }
                for node in self.network.nodes(data=True):
                    if node[0] == sw:
                        next_match = node[1].get('ports').get(max_output[sw].get('max_output'))[0]
                        for item in self.network.nodes(data=True):
                            if item[0] == next_match:
                                rule['next_hop'] = item[1].get('obj')

                switches[sw].add_star_rule(rule)

        """Remove nodes where table is full"""
        self.remove_node(switches)

        """Add the remaining rules"""
        for endpoint in self.endpoints(self.remaining_rules):
            new_rule = self.create_rule(endpoint)
            if new_rule is not None:
                if Controller.check_all_switches_table(switches, new_rule.get('shortest_path', [])):
                    for sw in new_rule.get('shortest_path', []):
                        self.embedRules += 1
                        if len(switches[sw].table) < TABLE_SIZE - 1:
                            switches[sw].add_rule(new_rule.get('rules', {}).get(sw))

        print('Rules embedded with the new algorithm ->', self.embedRules)

    def create_rule(self, endpoint):
        """Creating a rule based on the given source and destination"""

        try:
            rules = {}
            sp = nx.shortest_path(self.copy_graph, source=endpoint[0], target=endpoint[1])
            sp_origin = nx.shortest_path(self.network.g.convertTo(nx.MultiGraph), source=endpoint[0], target=endpoint[1])

            print('==================== new rule computation ================')

            print(sp_origin)
            print(sp)

            # Create rules based on the shortest path in the network
            src = endpoint[0]
            dst = endpoint[1]

            for i in range(1, len(sp) - 1):

                rule = {
                    'actions': {'OutPort': None},
                    'match': {
                        'dst': self.network.hopts[dst]['ip'],
                        'src': self.network.hopts[src]['ip'],
                        'in_port': None
                    },
                    'next_hop': None,
                    'match_count': 0,
                    'start_time': time.time()
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

                rules[sp[i]] = rule

            return {'shortest_path': sp[1:len(sp) - 1],
                    'rules': rules}
        except:
            pass

    def update_table(self, packet):
        """Add a new rule when a packet reaches the controller"""

        src_name = self.get_name_from_ip(packet['source'])
        dst_name = self.get_name_from_ip(packet['destination'])

        for sp in self.network.all_shortest_path():
            if sp[0] == src_name and sp[-1] == dst_name:
                # print(sp)
                for i in range(1, len(sp) - 1):

                    rule = {
                        "actions": {'OutPort': None},
                        "match": {
                            "dst": packet['destination'],
                            "src": packet['source'],
                            "in_port": None
                        },
                        'next_hop': None,
                        'match_count': 0,
                        'start_time': time.time()
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
                            # print(sp[i])
                            switch_obj = node_info[1]['obj']
                            if rule not in switch_obj.table and len(switch_obj.table) < TABLE_SIZE - 1:
                                # print(rule)
                                switch_obj.add_rule(rule)
                            elif rule not in switch_obj.table and len(switch_obj.table) == TABLE_SIZE - 1:
                                switch_obj.remove_rule()
                                switch_obj.add_rule(rule)

    @staticmethod
    def check_all_switches_table(all_switches_list, switches):
        """check the table is full or not"""
        for sw in switches:
            if len(all_switches_list[sw].table) < TABLE_SIZE - 1:
                return True
        return False

    def remove_node(self, switches):
        """Remove nodes where table is full"""
        for sw in switches:
            if len(switches[sw].table) == TABLE_SIZE - 1:
                self.copy_graph.remove_node(sw)
