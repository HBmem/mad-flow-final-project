from collections import defaultdict

def preflow_push_max_flow(capacity, source, sink):


    vertices = set(capacity.keys())
    for u in capacity:
        for v in capacity[u]:
            vertices.add(v)
    vertices = list(vertices)

    neighbors = {u: set() for u in vertices}
    for u in capacity:
        for v in capacity[u]:
            neighbors[u].add(v)
            neighbors[v].add(u)

    flow = defaultdict(lambda: defaultdict(int))

    height = {u: 0 for u in vertices}
    excess = {u: 0 for u in vertices}

    height[source] = len(vertices)

    def residual(u, v):
        cap = capacity.get(u, {}).get(v, 0)
        return cap - flow[u][v]

    for v in capacity.get(source, {}):
        c = capacity[source][v]
        flow[source][v] = c
        flow[v][source] = -c
        excess[v] += c
        excess[source] -= c

    active = [u for u in vertices if u not in (source, sink) and excess[u] > 0]

    current = {u: 0 for u in vertices}
    neighbors_list = {u: list(neighbors[u]) for u in vertices}

    def push(u, v):
        send = min(excess[u], residual(u, v))
        if send <= 0:
            return
        flow[u][v] += send
        flow[v][u] -= send
        excess[u] -= send
        excess[v] += send

    def relabel(u):
        min_height = None
        for v in neighbors[u]:
            if residual(u, v) > 0:
                if min_height is None or height[v] < min_height:
                    min_height = height[v]
        if min_height is None:
            return
        height[u] = min_height + 1

    def discharge(u):
        while excess[u] > 0:
            if current[u] >= len(neighbors_list[u]):
                relabel(u)
                current[u] = 0
            else:
                v = neighbors_list[u][current[u]]
                if residual(u, v) > 0 and height[u] == height[v] + 1:
                    push(u, v)
                else:
                    current[u] += 1

    p = 0
    while p < len(active):
        u = active[p]
        old_height = height[u]
        discharge(u)
        if excess[u] > 0:
            if height[u] > old_height:
                active.insert(0, active.pop(p))
                p = 0
            else:
                p += 1
        else:
            active.pop(p)

    max_flow = 0
    for v in capacity.get(source, {}):
        max_flow += flow[source][v]

    return max_flow


def preflow_push(graph, source, sink):
    capacity = {}

    for u in graph.graph:
        capacity[u] = {}
        for v, w in graph.graph[u].items():
            c = int(w)
            if c > 0:
                capacity[u][v] = c

    return preflow_push_max_flow(capacity, source, sink)


if __name__ == "__main__":
    capacity = {
        "s": {"a": 10, "b": 5},
        "a": {"t": 5},
        "b": {"t": 10},
        "t": {}
    }

    max_flow = preflow_push_max_flow(capacity, "s", "t")
    print("Test max flow (expected 15):", max_flow)
