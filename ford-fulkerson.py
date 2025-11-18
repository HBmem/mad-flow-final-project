class Graph:
    def __init__(self, file_path):
        self.graph = {}
        self.load_graph(file_path)

    def load_graph(self, file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip().split()
                self.add_edge(line[0], line[1], line[2])
    
    def add_edge(self, u, v, w):
        if u not in self.graph:
            self.graph[u] = {}
        if v not in self.graph:
            self.graph[v] = {}
        self.graph[u][v] = w
    
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
                    parent[v] = u

                    if v == t:
                        return True
        return False
    
    def ford_fulkerson(self, source, sink):
        parent = {}
        max_flow = 0

        # Augment the flow while there is a path from source to sink
        while self.BFS(source, sink, parent):
            path_flow = float('Inf')
            s = sink

            # Find minimum residual capacity of the edges along the path filled by BFS
            while s != source:
                # Update path_flow to the minimum capacity found
                path_flow = min(path_flow, int(self.graph[parent[s]][s]))
                s = parent[s]

            max_flow += path_flow

            v = sink

            # update residual capacities of the edges and reverse edges along the path
            while v != source:
                u = parent[v]
                self.graph[u][v] = str(int(self.graph[u][v]) - path_flow)
                # Ensure reverse edge exists
                if v not in self.graph:
                    self.graph[v] = {}
                # Add reverse edge if it doesn't exist
                if u not in self.graph[v]:
                    self.graph[v][u] = '0'
                self.graph[v][u] = str(int(self.graph[v][u]) + path_flow)
                v = parent[v]

        return max_flow
    
    def print_graph(self):
        for e in self.graph:
            print(e, "->", self.graph[e])


bipartite_g1 = Graph('./graphs/Bipartite/g1.txt')
bipartite_g2 = Graph('./graphs/Bipartite/g2.txt')

print("The maximum possible flow is:", bipartite_g1.ford_fulkerson('s', 't'))
print("The maximum possible flow is:", bipartite_g2.ford_fulkerson('s', 't'))

#################################################

print('')
fixedDegree_g1 = Graph('./graphs/FixedDegree/20v-3out-4min-355max.txt')
fixedDegree_g2 = Graph('./graphs/FixedDegree/100v-5out-25min-200max.txt')

print("The maximum possible flow is:", fixedDegree_g1.ford_fulkerson('s', 't'))
print("The maximum possible flow is:", fixedDegree_g2.ford_fulkerson('s', 't'))

#################################################

mesh_g1 = Graph('./graphs/Mesh/smallMesh.txt')
mesh_g2 = Graph('./graphs/Mesh/mediumMesh.txt')

print('')
print("The maximum possible flow is:", mesh_g1.ford_fulkerson('s', 't'))
print("The maximum possible flow is:", mesh_g2.ford_fulkerson('s', 't'))

#################################################

random_g1 = Graph('./graphs/Random/n10-m10-cmin5-cmax10-f30.txt')
random_g2 = Graph('./graphs/Random/n100-m100-cmin10-cmax20-f949.txt')

print('')
print("The maximum possible flow is:", random_g1.ford_fulkerson('s', 't'))
print("The maximum possible flow is:", random_g2.ford_fulkerson('s', 't'))