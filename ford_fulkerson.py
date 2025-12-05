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
