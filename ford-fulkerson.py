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
    # It retruns True if there is a path from source 's' to sink 't', otherwise False
    def BFS(self, s, t, parent):
        visited = {key: False for key in self.graph}
        queue = []
        queue.append(s)
        visited[s] = True

        #  Perform BFS to find an augmenting path
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

    def ford_fulkerson(self, source, sink):
        parent = {}
        max_flow = 0

        # Augment the flow while there is a path from source to sink
        while self.BFS(source, sink, parent):
            path_flow = float("Inf")
            s = sink

            # Find minimum residual capacity of the edges along the path filled by BFS
            while s != source:
                # Update path_flow to the minimum capacity found (i.e. bottleneck value)
                path_flow = min(path_flow, int(self.graph[parent[s]][s]))
                s = parent[s]

            max_flow += path_flow  # increase overall flow by the bottleneck value

            v = sink

            # Update residual capacities of the edges and reverse edges along the path
            while v != source:
                u = parent[v]

                # Decrease capacity of forward edge because we pushed that much additional flow through it. This is the leftover capacity.
                self.graph[u][v] = str(int(self.graph[u][v]) - path_flow)

                # Ensure reverse edge exists
                if v not in self.graph:
                    self.graph[v] = {}

                # Add reverse edge if it doesn't exist, with initial capacity 0
                if u not in self.graph[v]:
                    self.graph[v][u] = "0"

                # Set capacity of the backward edge to the bottleneck value because we have pushed that much flow through the forward edge
                self.graph[v][u] = str(int(self.graph[v][u]) + path_flow)
                v = parent[v]

        return max_flow

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


bipartite_g1 = Graph("./graphs/Bipartite/g1.txt")
print("Bipartite graph g1:")
bipartite_g1.print_graph()
print("")
bipartite_g2 = Graph("./graphs/Bipartite/g2.txt")

print("Bipartite graphs:")
print("g1: The maximum possible flow is:", bipartite_g1.ford_fulkerson("s", "t"))
print("g2: The maximum possible flow is:", bipartite_g2.ford_fulkerson("s", "t"))

#################################################

print("")
fixedDegree_g1 = Graph("./graphs/FixedDegree/20v-3out-4min-355max.txt")
fixedDegree_g2 = Graph("./graphs/FixedDegree/100v-5out-25min-200max.txt")

print("Fixed Degree graphs:")
print("g1: The maximum possible flow is:", fixedDegree_g1.ford_fulkerson("s", "t"))
print("g2: The maximum possible flow is:", fixedDegree_g2.ford_fulkerson("s", "t"))

#################################################

mesh_g1 = Graph("./graphs/Mesh/smallMesh.txt")
mesh_g2 = Graph("./graphs/Mesh/mediumMesh.txt")

print("")
print("Mesh graphs:")
print("g1: The maximum possible flow is:", mesh_g1.ford_fulkerson("s", "t"))
print("g2: The maximum possible flow is:", mesh_g2.ford_fulkerson("s", "t"))

#################################################

random_g1 = Graph("./graphs/Random/n10-m10-cmin5-cmax10-f30.txt")
random_g2 = Graph("./graphs/Random/n100-m100-cmin10-cmax20-f949.txt")

print("")
print("Random graphs:")
print("g1: The maximum possible flow is:", random_g1.ford_fulkerson("s", "t"))
print("g2: The maximum possible flow is:", random_g2.ford_fulkerson("s", "t"))
