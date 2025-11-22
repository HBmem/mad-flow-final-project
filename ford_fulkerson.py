from graph import Graph


def ford_fulkerson(graph, source, sink):
    parent = {}
    max_flow = 0

    # Augment the flow while there is a path from source to sink
    while graph.BFS(source, sink, parent):
        path_flow = float("Inf")
        s = sink

        # Find minimum residual capacity of the edges along the path filled by BFS
        while s != source:
            # Update path_flow to the minimum capacity found (i.e. bottleneck value)
            path_flow = min(path_flow, int(graph.graph[parent[s]][s]))
            s = parent[s]

        max_flow += path_flow  # increase overall flow by the bottleneck value

        v = sink

        # Update residual capacities of the edges and reverse edges along the path
        while v != source:
            u = parent[v]

            # Decrease capacity of forward edge because we pushed that much additional flow through it. This is the leftover capacity.
            graph.graph[u][v] = str(int(graph.graph[u][v]) - path_flow)

            # Ensure reverse edge exists
            if v not in graph.graph:
                graph.graph[v] = {}

            # Add reverse edge if it doesn't exist, with initial capacity 0
            if u not in graph.graph[v]:
                graph.graph[v][u] = "0"

            # Set capacity of the backward edge to the bottleneck value because we have pushed that much flow through the forward edge
            graph.graph[v][u] = str(int(graph.graph[v][u]) + path_flow)
            v = parent[v]

    return max_flow


if __name__ == "__main__":
    bipartite_g1 = Graph("./graphs/Bipartite/g1.txt")
    print("")
    bipartite_g2 = Graph("./graphs/Bipartite/g2.txt")

    print("Bipartite graphs:")
    print("g1: The maximum possible flow is:", ford_fulkerson(bipartite_g1, "s", "t"))
    print("g2: The maximum possible flow is:", ford_fulkerson(bipartite_g2, "s", "t"))

    #################################################

    print("")
    fixedDegree_g1 = Graph("./graphs/FixedDegree/20v-3out-4min-355max.txt")
    fixedDegree_g2 = Graph("./graphs/FixedDegree/100v-5out-25min-200max.txt")

    print("Fixed Degree graphs:")
    print("g1: The maximum possible flow is:", ford_fulkerson(fixedDegree_g1, "s", "t"))
    print("g2: The maximum possible flow is:", ford_fulkerson(fixedDegree_g2, "s", "t"))

    #################################################

    mesh_g1 = Graph("./graphs/Mesh/smallMesh.txt")
    mesh_g2 = Graph("./graphs/Mesh/mediumMesh.txt")

    print("")
    print("Mesh graphs:")
    print("g1: The maximum possible flow is:", ford_fulkerson(mesh_g1, "s", "t"))
    print("g2: The maximum possible flow is:", ford_fulkerson(mesh_g2, "s", "t"))

    #################################################

    random_g1 = Graph("./graphs/Random/n10-m10-cmin5-cmax10-f30.txt")
    random_g2 = Graph("./graphs/Random/n100-m100-cmin10-cmax20-f949.txt")

    print("")
    print("Random graphs:")
    print("g1: The maximum possible flow is:", ford_fulkerson(random_g1, "s", "t"))
    print("g2: The maximum possible flow is:", ford_fulkerson(random_g2, "s", "t"))
