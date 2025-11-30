from collections import defaultdict, deque

def preflow_push_max_flow(capacity, source, sink):
    # Collect all vertices that appear in the capacity graph
    vertices = set(capacity.keys())
    for u in capacity:
        for v in capacity[u]:
            vertices.add(v)
    vertices = list(vertices)

    # Track neighbors so we can check residual edges easily
    neighbors = {u: set() for u in vertices}
    for u in capacity:
        for v in capacity[u]:
            neighbors[u].add(v)
            neighbors[v].add(u)

    # Start with zero flow everywhere
    flow = defaultdict(lambda: defaultdict(int))

    # Height and excess are the main values used by Preflow-Push
    height = {u: 0 for u in vertices}
    excess = {u: 0 for u in vertices}

    # Standard initialization: source starts with a large height
    height[source] = len(vertices)

    # Residual capacity helper
    def residual(u, v):
        cap = capacity.get(u, {}).get(v, 0)
        return cap - flow[u][v]

    # Initial push: send as much as possible out of the source
    for v, c in capacity.get(source, {}).items():
        flow[source][v] = c
        flow[v][source] = -c
        excess[v] += c
        excess[source] -= c

    # Active nodes = nodes with extra flow (except s and t)
    active = deque(
        u for u in vertices
        if u not in (source, sink) and excess[u] > 0
    )

    def push(u, v):
        # Push whatever u can send through (u, v)
        send = min(excess[u], residual(u, v))
        if send <= 0:
            return
        prev_excess_v = excess[v]
        flow[u][v] += send
        flow[v][u] -= send
        excess[u] -= send
        excess[v] += send

        # If v becomes active for the first time, add it to the queue
        if v not in (source, sink) and prev_excess_v == 0 and excess[v] > 0:
            active.append(v)

    def relabel(u):
        # Increase u's height so it can push somewhere
        min_height = None
        for v in neighbors[u]:
            if residual(u, v) > 0:
                if min_height is None or height[v] < min_height:
                    min_height = height[v]
        if min_height is not None:
            height[u] = min_height + 1

    def discharge(u):
        # Keep trying to push flow out of u until it has no excess left
        while excess[u] > 0:
            pushed = False
            for v in neighbors[u]:
                if residual(u, v) > 0 and height[u] == height[v] + 1:
                    push(u, v)
                    pushed = True
                    if excess[u] == 0:
                        break
            if not pushed:
                # No valid push edges, so lift u
                relabel(u)

    # Main algorithm loop: process active nodes one at a time
    while active:
        u = active.popleft()
        discharge(u)

        # If the node still has extra flow, it stays active
        if excess[u] > 0:
            active.append(u)

    # Max flow sits in the sink's excess after all pushes finish
    return excess[sink]


def preflow_push(graph, source, sink):
    # Build a simple capacity dict from the Graph object
    capacity = {}
    for u in graph.graph:
        capacity[u] = {}
        for v, w in graph.graph[u].items():
            c = int(w)
            if c > 0:  # Only keep usable edges
                capacity[u][v] = c

    return preflow_push_max_flow(capacity, source, sink)


if __name__ == "__main__":
    # Small sanity check graph:
    # s -> a (10), s -> b (5)
    # a -> t (5),  b -> t (10)
    # Correct max flow here is 10.
    capacity = {
        "s": {"a": 10, "b": 5},
        "a": {"t": 5},
        "b": {"t": 10},
        "t": {},
    }

    max_flow = preflow_push_max_flow(capacity, "s", "t")
    print("Test max flow (expected 10):", max_flow)
