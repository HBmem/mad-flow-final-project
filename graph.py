class Graph:
    def __init__(self, file_path):
        # The graph is represented as an adjacency list using a dictionary of dictionaries
        # Example structure:
        # {
        #   'A': {'B': 10, 'C': 5}, node A has edges to B and C with weights 10 and 5 respectively
        #   'B': {'C': 15}, node B has an edge to C with weight 15
        #   'C': {}, node C has no outgoing edges
        # }
        self.graph = {}
        self.load_graph(file_path)

    def load_graph(self, file_path):
        with open(file_path, "r") as f:
            for line in f:
                fields = line.strip().split()
                u = fields[0]  # source node
                v = fields[1]  # destination node
                w = fields[2]  # weight
                self.add_edge(u, v, w)

    def add_edge(self, u, v, w):
        if u not in self.graph:
            self.graph[u] = {}
        if v not in self.graph:
            self.graph[v] = {}
        self.graph[u][v] = w  # edge from u to v with weight w

    # BFS performs a breadth-first search to find an augmenting path
    # It returns True if there is a path from source 's' to sink 't', otherwise False
    def BFS(self, s, t, parent):
        visited = {key: False for key in self.graph}
        queue = []
        queue.append(s)
        visited[s] = True

        # Perform BFS to find an augmenting path
        while queue:
            u = queue.pop(0)

            # Explore all adjacent vertices of u
            for v in self.graph[u]:
                # If not visited and there is a positive capacity
                if not visited[v] and int(self.graph[u][v]) > 0:
                    queue.append(v)
                    visited[v] = True
                    parent[v] = u  # node u is the parent of v

                    if v == t:
                        return True
        return False

    # Utility function to print the graph
    # Each edge is printed in the format: u -weight-> v
    # or just the vertex if it has no outgoing edges
    def print_graph(self):
        for vertex in self.graph:
            u = vertex
            if not self.graph[u]:
                print("%s" % (u))
                continue
            for v in self.graph[u]:
                w = self.graph[u][v]
                print("%s\t-%s->\t%s" % (u, w, v))
