from graph import Graph
import math


def scaling_max_flow(graph, source, sink):

    # Find the max_capacity in the edges outgoing from source
    max_capacity = 0
    for v, cap_str in graph.graph.get(source, {}).items():
        max_capacity = max(max_capacity, int(cap_str))

    # If there is no outgoing edge from source, return 0
    if max_capacity == 0:
        return 0

    # Delta initialization
    delta = 1
    if max_capacity > 0:
        # Find the largest 2^k(Delta) such that 2^k <= max_capacity
        k = math.floor(math.log2(max_capacity))
        delta = 2**k

    # Initialize flow f = 0
    parent = {}
    max_flow = 0

    # Outer loop: While Delta >= 1
    while delta >= 1:

        # Inner loop: While there is an s-t path in the graph G_f(Delta)
        # Here we call the delta_BFS to find a s-t path with capacity >= Delta
        while graph.BFS(source, sink, parent, delta):

            # 1. Find the bottleneck capacity (path_flow) on path P
            path_flow = float("Inf")
            s = sink

            while s != source:
                # Update path_flow to the minimum capacity found (i.e. bottleneck value)
                path_flow = min(path_flow, int(graph.graph[parent[s]][s]))
                s = parent[s]

            max_flow += path_flow  # increase overall flow by the bottleneck value

            # 2. Update residual graph
            v = sink
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

        # Outer loop ends, reduce Delta: Delta = Delta / 2
        delta //= 2

    # Return f (max_flow)
    return max_flow
