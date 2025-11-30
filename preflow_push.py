from collections import defaultdict, deque

def preflow_push_max_flow(capacity, source, sink):
    # Collect all vertices that appear anywhere in the graph
    vertices = set(capacity.keys())
    for u in capacity:
        for v in capacity[u]:
            vertices.add(v)
    vertices = list(vertices)

    # For each vertex, keep track of neighbors for residual edges
    neighbors = {u: set() for u in vertices}
    for u in capacity:
        for v in capacity[u]:
            neighbors[u].add(v)
            neighbors[v].add(u)

    # Flow starts at 0 on every edge
    flow = defaultdict(lambda: defaultdict(int))

    # Height and excess for each vertex
    height = {u: 0 for u in vertices}
    excess = {u: 0 for u in vertices}

    # Source starts "above" everyone else
    height[source] = len(vertices)

    def residual(u, v):
        # Residual capacity = original capacity - current flow
        cap = capacity.get(u, {}).get(v, 0)
        return cap - flow[u][v]

    # Push all possible flow out of the source once (initial preflow)
    for v, c in capacity.get(source, {}).items():
        flow[source][v] = c
        flow[v][source] = -c
        excess[v] += c
        excess[source] -= c

    # Active = vertices (except s, t) that currently have extra flow
    active = deque(
        u for u in vertices
        if u not in (source, sink) and excess[u] > 0
    )

    def push(u, v):
        # Send as much as we can from u to v
        send = min(excess[u], residual(u, v))
        if send <= 0:
            return
        prev_excess_v = excess[v]
        flow[u][v] += send
        flow[v][u] -= send
        excess[u] -= send
        excess[v] += send
        # If v just became active (and is not s or t), add it to the queue
        if v not in (source, sink) and prev_excess_v == 0 and excess[v] > 0:
            active.append(v)

    def relabel(u):
        # Raise u just enough to make at least one outgoing edge admissible
        min_height = None
        for v in neighbors[u]:
            if residual(u, v) > 0:
                if min_height is None or height[v] < min_height:
                    min_height = height[v]
        if min_height is not None:
            height[u] = min_height + 1

    def discharge(u):
        # Keep pushing from u until it has no extra flow left
        while excess[u] > 0:
            pushed = False
            for v in neighbors[u]:
                if residual(u, v) > 0 and height[u] == height[v] + 1:
                    push(u, v)
                    pushed = True
                    if excess[u] == 0:
                        break
            if not pushed:
                # No admissible edge right now, so increase u's height
                relabel(u)

    # Main loop: process active vertices until none are left
    while active:
        u = active.popleft()
        discharge(u)
        # If u is still active after discharge, put it back into the queue
        if excess[u] > 0:
            active.append(u)

    # At the end, the excess at the sink is the max flow value
    return excess[sink]


def preflow_push(graph, source, sink):
    # Build a clean capacity dictionary from our Graph object:
    # convert string weights to ints and skip zero-capacity edges.
    capacity = {}
    for u in graph.graph:
        capacity[u] = {}
        for v, w in graph.graph[u].items():
            c = int(w)
            if c > 0:
                capacity[u][v] = c

    return preflow_push_max_flow(capacity, source, sink)


if __name__ == "__main__":
    # Small sanity check graph:
    # s -> a (10), s -> b (5)
    # a -> t (5),  b -> t (10)
    # Max flow here is 10.
    capacity = {
        "s": {"a": 10, "b": 5},
        "a": {"t": 5},
        "b": {"t": 10},
        "t": {},
    }

    max_flow = preflow_push_max_flow(capacity, "s", "t")
    print("Test max flow (expected 10):", max_flow)
