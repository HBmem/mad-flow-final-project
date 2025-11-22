import argparse
from graph import Graph
from ford_fulkerson import ford_fulkerson

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-g", "--graph", type=str, required=True, help="Path to the graph file"
    )
    parser.add_argument(
        "-s", "--source", type=str, default="s", help="Source node (default: 's')"
    )
    parser.add_argument(
        "-t", "--sink", type=str, default="t", help="Sink node (default: 't')"
    )
    args = parser.parse_args()

    graph = Graph(args.graph)
    print(
        "The maximum possible flow is:", ford_fulkerson(graph, args.source, args.sink)
    )
