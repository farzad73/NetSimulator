import networkx as nx
import matplotlib.pyplot as plt
from devices import Host, OpenflowSwitch


class MultiGraph(nx.MultiGraph):

    def __init__(self, **attr):
        super().__init__(**attr)
        self.node = {}
        self.edge = {}

    def add_node(self, node, attr_dict=None, **attrs):
        attr_dict = {'ports': {}} if attr_dict is None else attr_dict
        attr_dict.update(attrs)
        self.node[node] = attr_dict
        return self.node[node]

    def add_edge(self, src, dst, key=None, attr_dict=None, **attrs):
        attr_dict = {} if attr_dict is None else attr_dict
        attr_dict.update(attrs)
        self.node.setdefault(src, {})
        self.node.setdefault(dst, {})
        self.edge.setdefault(src, {})
        self.edge.setdefault(dst, {})
        self.edge[src].setdefault(dst, {})
        entry = self.edge[dst][src] = self.edge[src][dst]
        # If no key, pick next ordinal number
        if key is None:
            keys = [k for k in entry.keys() if isinstance(k, int)]
            key = max([0] + keys) + 1
        entry[key] = attr_dict
        return key

    def nodes(self, data=False):
        """Return list of graph nodes"""
        return list(self.node.items()) if data else list(self.node.keys())

    def edges_iter(self, data=False, keys=False):
        """Iterator: return graph edges"""
        for src, entry in self.edge.items():
            for dst, keys in entry.items():
                if src > dst:
                    # Skip duplicate edges
                    continue
                for k, attrs in keys.items():
                    if data:
                        if keys:
                            yield src, dst, k, attrs
                        else:
                            yield src, dst, attrs
                    else:
                        if keys:
                            yield src, dst, k
                        else:
                            yield src, dst

    def edges(self, data=False, keys=False):
        """Return list of graph edges"""
        return list(self.edges_iter(data=data, keys=keys))

    def __getitem__(self, node):
        """Return link dict for given src node"""
        return self.edge[node]

    def __len__(self):
        """Return the number of nodes"""
        return len(self.node)

    def convertTo(self, cls, data=False, keys=False):
        """Convert to networkx.MultiGraph"""
        g = cls()
        g.add_nodes_from(self.nodes(data=data))
        g.add_edges_from(self.edges(data=(data or keys), keys=keys))
        return g


class Topo(object):

    def __init__(self):
        self.g = MultiGraph()
        self.hopts = {}
        self.sopts = {}
        self.lopts = []
        # ports[src][dst][sport] is port on dst that connects to src
        self.ports = {}

    def showGraph(self, position=None):
        """Drawing graph"""
        g = self.g.convertTo(nx.MultiGraph)
        nx.draw(g, position, with_labels=True)
        plt.show()

    def all_shortest_path(self):
        """Compute the shortest paths of graph"""
        sps = nx.shortest_path(self.g.convertTo(nx.MultiGraph))
        shortest_paths = []
        for source in sps:
            if source in self.hosts():
                for destination in sps[source]:
                    if destination != source and destination in self.hosts():
                        shortest_paths.append(sps[source][destination])
        return shortest_paths

    def shortest_path(self, src, dst):
        sps = nx.shortest_path(self.g.convertTo(nx.MultiGraph), source=src, target=dst)
        return sps

    def addNode(self, name, **opts):
        return self.g.add_node(name, **opts)

    def addHost(self, name, **opts):
        self.hopts[name] = opts
        self.hopts[name]['ports'] = {}
        result = self.addNode(name, obj=Host(name=name, ip=opts['ip']))
        return result['obj']

    def addSwitch(self, name):
        self.sopts[name] = {}
        result = self.addNode(name, isSwitch=True, obj=OpenflowSwitch(name))
        return result['obj']

    def addLink(self, node1, node2, port1=None, port2=None, key=None, **opts):
        port1, port2 = self.addPort(node1, node2, port1, port2)
        opts = dict()
        opts.update(node1=node1, node2=node2, port1=port1, port2=port2)
        self.g.add_edge(node1, node2, key, **opts)
        self.lopts.append(opts)
        return key

    def addPort(self, src, dst, sport=None, dport=None):
        # Initialize if necessary
        ports = self.ports
        ports.setdefault(src, {})
        ports.setdefault(dst, {})
        # New port: number of outlinks + base
        if sport is None:
            src_base = 1 if self.isSwitch(src) else 0
            sport = len(ports[src]) + src_base
        if dport is None:
            dst_base = 1 if self.isSwitch(dst) else 0
            dport = len(ports[dst]) + dst_base
        ports[src][sport] = (dst, dport)
        ports[dst][dport] = (src, sport)

        self.sopts[src].update(ports[src]) if self.isSwitch(src) else self.hopts[src]['ports'].update(ports[src])
        self.g.node[src]['ports'].update(ports[src])
        self.sopts[dst].update(ports[dst]) if self.isSwitch(dst) else self.hopts[dst]['ports'].update(ports[dst])
        self.g.node[dst]['ports'].update(ports[dst])

        return sport, dport

    def isSwitch(self, n):
        """Returns true if node is a switch."""
        return self.g.node[n].get('isSwitch', False)

    def nodes(self, data=False):
        """Return nodes in graph"""
        return self.g.nodes(data)

    def switches(self):
        """Return switches"""
        return [n for n in self.nodes() if self.isSwitch(n)]

    def hosts(self):
        """Return hosts"""
        return [n for n in self.nodes() if not self.isSwitch(n)]

    def copy(self):
        return self.g.copy()

    def links( self):
        """Return links"""
        links = self.g.edges()
        return links