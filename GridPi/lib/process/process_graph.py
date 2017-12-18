#!/usr/bin/env python3

""" This module defines all operations that take place on system.process objects.

"""

import logging

from GridPi.lib.process import process_core


class Edgenode(object):
    def __init__(self):
        self.name = None
        self.next = None


class Graph(object):
    """ Defines a Graph Object

    """

    def __init__(self):
        self.edges = dict()
        self.degree = dict()
        self.nverticies = 0
        self.nedges = 0
        self.directed = True

        self.edge_data_input = None

    def build_adj_list(self):
        logging.debug('GRAPH PROCESS: input graph edges: %s', self.edge_data_input)

        self.nedges = len(self.edge_data_input)  # Find the number of edges, by halving the input data

        vertex_set = dict()
        for edge in self.edge_data_input:  # Find the number of verticies by hashing a set
            vertex_set[edge[0]] = 1
            vertex_set[edge[1]] = 1
        self.nverticies = len(vertex_set)

        for edge in self.edge_data_input:  # Insert Edge
            self.insert_edge(edge[0], edge[1], True)

    def insert_edge(self, start_node, end_node, directed):

        edge = Edgenode()
        edge.name = end_node.name
        edge.next = self.edges.get(start_node.name, None)

        self.edges[start_node.name] = edge
        self.degree[start_node.name] = 1

        # Test to see if destination node has been added to the adjacency list
        if not self.edges.get(edge.name, None):
            self.edges[edge.name] = None

        if not directed:
            self.insert_edge(end_node, start_node, True)
        else:
            self.nedges += 1

    def topological_sort(self):
        dfs = DFS(self)
        return dfs.topological_sort

    def print_adj_list(self):
        for start_node, edge in self.edges.items():
            print(start_node, end=': ')

            node = edge
            while node:
                print(node.name, end=' ')
                node = node.next
            print()


class GraphProcess(Graph):
    """ Interfaces a standard graph object with a system object

    """

    def __init__(self, process_container):
        super(GraphProcess, self).__init__()

        self.GD = GraphDependencies()
        self.GD.find_input_sinks(process_container.process_list)
        self.GD.find_output_sources(process_container.process_list)
        self.GD.resolve_duplicate_sources(process_container.process_dict)

        self.edge_data_input = self.GD.edge_list()


class DFS(object):
    """ Performs depth-first search on a Graph object

    """

    @property
    def topological_sort(self):
        return self._topological_sort

    def __init__(self, graph):

        self.processed = dict()
        self.discovered = dict()
        self.parent = dict()
        for node in graph.edges.keys():
            self.processed[node] = self.discovered[node] = False
            self.parent[node] = -1

        self.entry_time = dict()
        self.exit_time = dict()
        self.time = 0

        self.finished = 0
        self._topological_sort = list()

        for node in graph.edges.keys():
            if not self.processed[node]:
                self.dfs(graph, node)

        self._topological_sort.reverse()
        logging.debug('GRAPH PROCESS: dfs(): Topological Sort %s', self._topological_sort)

    def dfs(self, graph, start_node):

        if self.finished:
            return

        self.discovered[start_node] = True
        self.time += 1
        self.entry_time[start_node] = self.time
        # process vertex early(node)

        end_node = graph.edges.get(start_node, None)
        while end_node:
            if not self.discovered.get(end_node.name, None):
                self.parent[end_node.name] = start_node
                # process_edge(start_node, end_node.name)
                self.dfs(graph, end_node.name)
            elif not self.processed.get(end_node.name, None) or graph.directed:
                pass
                # process_edge(start_node, end_node.name)
            if self.finished:
                return
            end_node = end_node.next

        self.process_vertex_late(start_node)
        self.time += 1
        self.exit_time[start_node] = self.time
        self.processed[start_node] = True
        # print('{} processed'.format(start_node))

    def process_vertex_late(self, node):
        self._topological_sort.append(node)


class GraphDependencies(object):
    """ Finds dependencies and creates an dependency edge list. edge lists are comma separated nodes, pairs of which
     define and edge. This is input to Graph object.

    """

    def __init__(self):

        self.sink = dict()  # Dict('input' : list(process1, process2...))
        self.source = dict()
        self.aggregate = dict()

    def find_input_sinks(self, process_list):
        """ For an input in any process, log that process as a 'dependent' of that input in the dependent dictionary

        """
        for process in process_list:
            for inpt in process.input.keys():
                try:
                    self.sink[inpt].append(process)
                except KeyError:
                    self.sink[inpt] = [process]

        logging.debug('GRAPH PROCESS: pre-process self.sink: %s', self.sink)

    def find_output_sources(self, process_list):
        """ For an output in any process, log that process as an 'indenpendent source' of that output in the
        indenpendent dictonary.
        """
        for process in process_list:
            for output in process.output.keys():
                try:
                    self.source[output].append(process)
                except KeyError:
                    self.source[output] = [process]

        logging.debug('GRAPH PROCESS: pre-process self.source: %s', self.source)

    def resolve_duplicate_sources(self, process_dict):
        for process_list in self.source.values():
            if len(process_list) > 1:

                """ An aggregate object is created whihc holds the processes that combine the same output
                The output of the aggregate object is the output of the processes it contains"""
                agg_process = process_core.AggregateProcess(process_list)
                process_dict.update({agg_process.name: agg_process})  # Update the process dictionary with agg process

                for process in process_list:
                    self.aggregate[process] = [agg_process]  # Log what processes are being replaced by the Agg process

        for output, process_list in self.source.items():  # Replace processes now contained in the Aggregate process
            for process in process_list:  # in the source dict with the Aggregate process
                if self.aggregate.get(process, None):
                    self.source[output] = self.aggregate[process]

        logging.debug('GRAPH PROCESS: post-process self.source: %s', self.source)

        for inpt, process_list in self.sink.items():  # Replace processes now contained in the Aggregate process
            for process in process_list:  # in the sink dict with the Aggregate process
                if self.aggregate.get(process, None):
                    self.sink[inpt] = self.aggregate[process]

        logging.debug('GRAPH PROCESS: post-process self.sink: %s', self.sink)

    def edge_list(self):

        edges = []

        for inpt, sink_process_list in self.sink.items():
            for output, source_process_list in self.source.items():
                if inpt == output:
                    for sink_process in sink_process_list:
                        for source_process in source_process_list:
                            edge = [source_process, sink_process]
                            edges.append(edge)
        return edges


if __name__ == '__main__':
    pass
