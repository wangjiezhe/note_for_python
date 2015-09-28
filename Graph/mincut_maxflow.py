#!/usr/bin/env python


import networkx as nx
from networkx.algorithms.flow import edmonds_karp


def main():
    g = nx.DiGraph()
    g.add_edge('s', 'v1', capacity=5)
    g.add_edge('s', 'v2', capacity=22)
    g.add_edge('s', 'v3', capacity=15)
    g.add_edge('v1', 'v4', capacity=10)
    g.add_edge('v2', 'v1', capacity=4)
    g.add_edge('v2', 'v3', capacity=5)
    g.add_edge('v2', 'v4', capacity=5)
    g.add_edge('v2', 'v5', capacity=9)
    g.add_edge('v3', 'v5', capacity=6)
    g.add_edge('v4', 'v5', capacity=15)
    g.add_edge('v4', 't', capacity=30)
    g.add_edge('v5', 'v4', capacity=18)
    g.add_edge('v5', 't', capacity=10)
    flow = nx.maximum_flow(g, 's', 't')
    print(flow)
    print(nx.minimum_cut(g, 's', 't'))
    F = edmonds_karp(g, 's', 't')
    for u, v in sorted(g.edges_iter()):
        print(('(%s, %s) %s' % (u, v, F[u][v])))


if __name__ == "__main__":
    main()
