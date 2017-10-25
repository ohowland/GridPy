import time

class Edgenode(object):
  def __init__(self):
    self.name = None
    self.weight = None
    self.next = None

class Graph(object):
  def __init__(self):
    self.edges = dict()
    self.degree = dict()
    self.nverticies = 0
    self.nedges = 0
    self.directed = True

  def read_graph(self, path):
    with open(path, 'r') as f:
      graph_data = f.read()

    # Find the number of edges, by halving the input data
    graph_data_split = graph_data.split()
    self.nedges = len(graph_data_split)/2

    # Find the number of verticies by hashing a set
    vertex_set = dict()
    for x in graph_data_split:
      vertex_set[x] = 1
    self.nverticies = len(vertex_set)

    for i in range(0, len(graph_data_split), 2):
      chunk = graph_data_split[i:i + 2]
      self.insert_edge(chunk[0], chunk[1], True)

  def insert_edge(self, start_node, end_node, directed):

    edge = Edgenode()
    edge.name = end_node
    edge.next = self.edges.get(start_node, None)

    self.edges[start_node] = edge
    self.degree[start_node] = 1

    try:
      x = self.edges[edge.name]
    except KeyError:
      self.edges[edge.name] = None

    if not directed:
      self.insert_edge(end_node, start_node, True)
    else:
      self.nedges += 1

    #print('inserted ({},{})'.format(x, y))

  def print_adjlist(self):
    for start_node, edge in self.edges.items():
      print(start_node, end=': ')

      node = edge
      while node:
        print(node.name, end=' ')
        node = node.next
      print()

class DFS(object):
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
    self.topo_list = list()

    for node in graph.edges.keys():
      if not self.processed[node]:
        self.dfs(graph, node)

    self.topo_list.reverse()
    print(self.topo_list)

  def dfs(self, graph, start_node):

    if self.finished:
      return

    self.discovered[start_node] = True
    self.time += 1
    self.entry_time[start_node] = self.time
    #process vertex early(node)

    end_node = graph.edges.get(start_node, None)
    while end_node:
      if not self.discovered.get(end_node.name, None):
        self.parent[end_node.name] = start_node
        #process_edge(start_node, end_node.name)
        self.dfs(graph, end_node.name)
      elif not self.processed.get(end_node.name, None) or graph.directed:
        pass
        #process_edge(start_node, end_node.name)
      if self.finished:
        return
      end_node = end_node.next

    self.process_vertex_late(start_node)
    self.time += 1
    self.exit_time[start_node] = self.time
    self.processed[start_node] = True
    #print('{} processed'.format(start_node))

  def process_vertex_late(self, node):
    self.topo_list.append(node)

if __name__ == '__main__':
  g = Graph()
  g.read_graph('test.txt')
  g.print_adjlist()

  s = DFS(g)