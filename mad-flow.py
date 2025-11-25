import argparse
import json
from graph import Graph
from ford_fulkerson import ford_fulkerson
from preflow_push import preflow_push 

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
    
    parser.add_argument(
        "-a", "--algorithm",
        type=str,
        choices=["ford_fulkerson", "preflow_push"],
        default="ford_fulkerson",
        help="Max-flow algorithm to use (default: ford_fulkerson)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format"
    )
    args = parser.parse_args()

    graph = Graph(args.graph)

    if args.algorithm == "ford_fulkerson":
        max_flow = ford_fulkerson(graph, args.source, args.sink)
    elif args.algorithm == "preflow_push":
        max_flow = preflow_push(graph, args.source, args.sink)
    else:
        # shouldn't be happeninng
        raise ValueError(f"Unknown algorithm: {args.algorithm}")

    if args.json:
        # JSON output mode for machine parsing
        output = {
            "max_flow": max_flow,
            "source": args.source,
            "sink": args.sink,
            "graph_file": args.graph,
            "num_vertices": graph.get_num_vertices(),
            "num_edges": graph.get_num_edges()
        }
        print(json.dumps(output))
    else:
        # Human-readable output mode
        print("The maximum possible flow is:", max_flow)
