#!/usr/bin/env python3
"""
Graph Generation Script

Generates graphs for max flow experiments. Supports both:
- Phase 1: Default parameters (see docs/graph-generation-phase1.md)
- Phase 2: CLI-driven parameter overrides for custom experiments

Output directory: GeneratedGraphs/ (default) or custom via -o flag
"""

import argparse
import subprocess
import sys
from pathlib import Path


# =============================================================================
# Default Configuration (Phase 1 values)
# =============================================================================

DEFAULT_OUTPUT_DIR = Path("GeneratedGraphs")
GRAPH_GEN_DIR = Path("graphGenerationCode")

# Default parameters for each graph type (Phase 1)
DEFAULT_BIPARTITE_PARAMS = {"probability": 0.5, "min_cap": 1, "max_cap": 1000}
DEFAULT_FIXED_DEGREE_PARAMS = {
    "edges_per_node": 30,
    "min_cap": 1,
    "max_cap": 1000,
}
DEFAULT_MESH_PARAMS = {"capacity": 1000, "constant": True}
DEFAULT_RANDOM_PARAMS = {
    "density": 30,
    "min_cap": 1,
    "max_cap": 1000,
}

# Default graph sizes (Phase 1)
DEFAULT_BIPARTITE_SIZES = [50, 100, 200, 300, 400, 500, 600, 800, 1000, 1200]
DEFAULT_FIXED_DEGREE_SIZES = [100, 250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000]
DEFAULT_MESH_SIZES = [20, 40, 60, 80, 100, 125, 150, 200, 250, 300]
DEFAULT_RANDOM_SIZES = [100, 200, 400, 600, 800, 1000, 1250, 1500, 1750, 2000]


# =============================================================================
# Helper Functions
# =============================================================================


def parse_int_list(s: str) -> list:
    """Parse a comma-separated list of integers."""
    return [int(x.strip()) for x in s.split(",")]


def parse_size_pairs(s: str) -> list:
    """Parse comma-separated size pairs like '50x100,100x200' into list of tuples."""
    pairs = []
    for item in s.split(","):
        item = item.strip()
        if "x" in item:
            parts = item.split("x")
            pairs.append((int(parts[0]), int(parts[1])))
        else:
            # Single value means square (rows=cols or source=sink)
            val = int(item)
            pairs.append((val, val))
    return pairs


def ensure_compiled(java_dir: Path, java_file: str):
    """Compile Java file if .class doesn't exist."""
    class_file = java_dir / java_file.replace(".java", ".class")
    java_path = java_dir / java_file

    if (
        not class_file.exists()
        or java_path.stat().st_mtime > class_file.stat().st_mtime
    ):
        print(f"  Compiling {java_file}...")
        result = subprocess.run(
            ["javac", java_file],
            cwd=java_dir,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"  ERROR compiling {java_file}: {result.stderr}")
            return False
    return True


def run_cli_java(java_dir: Path, class_name: str, args: list):
    """Run a Java program with command-line arguments."""
    result = subprocess.run(
        ["java", class_name] + [str(a) for a in args],
        cwd=java_dir,
        capture_output=True,
        text=True,
    )

    return result.returncode == 0, result.stderr


# =============================================================================
# Graph Generators
# =============================================================================


def generate_bipartite_graphs(
    output_dir: Path, params: dict, size_pairs: list, n: int = None
):
    """Generate bipartite graphs.

    Args:
        output_dir: Base output directory
        params: Dictionary with probability, min_cap, max_cap
        size_pairs: List of (source_nodes, sink_nodes) tuples
        n: Number of graphs to generate (default: all)
    """
    print("\n" + "=" * 60)
    print("Generating Bipartite Graphs")
    print("=" * 60)

    java_dir = GRAPH_GEN_DIR / "Bipartite"
    graph_output_dir = output_dir / "Bipartite"
    graph_output_dir.mkdir(parents=True, exist_ok=True)

    if not ensure_compiled(java_dir, "BipartiteGraph.java"):
        return False

    pairs_to_use = size_pairs[:n] if n is not None else size_pairs
    for source_nodes, sink_nodes in pairs_to_use:
        # Format probability for filename (e.g., 0.5 -> 05p)
        prob_str = str(params["probability"]).replace("0.", "").replace(".", "")
        filename = f"{source_nodes}s-{sink_nodes}t-{prob_str}p-{params['min_cap']}min-{params['max_cap']}max.txt"
        filepath = graph_output_dir / filename

        if filepath.exists():
            print(f"  Skipping {filename} (already exists)")
            continue

        print(f"  Generating {filename}...")

        # Command-line args: source_nodes sink_nodes probability min_cap max_cap output_file
        args = [
            source_nodes,
            sink_nodes,
            params["probability"],
            params["min_cap"],
            params["max_cap"],
            str(filepath.absolute()),
        ]

        success, error = run_cli_java(java_dir, "BipartiteGraph", args)
        if not success:
            print(f"    ERROR: {error}")
            return False

    return True


def generate_fixed_degree_graphs(
    output_dir: Path, params: dict, sizes: list, n: int = None
):
    """Generate fixed degree graphs.

    Args:
        output_dir: Base output directory
        params: Dictionary with edges_per_node, min_cap, max_cap
        sizes: List of vertex counts
        n: Number of graphs to generate (default: all)
    """
    print("\n" + "=" * 60)
    print("Generating FixedDegree Graphs")
    print("=" * 60)

    java_dir = GRAPH_GEN_DIR / "FixedDegree"
    graph_output_dir = output_dir / "FixedDegree"
    graph_output_dir.mkdir(parents=True, exist_ok=True)

    if not ensure_compiled(java_dir, "RandomGraph.java"):
        return False

    sizes_to_use = sizes[:n] if n is not None else sizes
    for size in sizes_to_use:
        filename = f"{size}v-{params['edges_per_node']}out-{params['min_cap']}min-{params['max_cap']}max.txt"
        filepath = graph_output_dir / filename

        if filepath.exists():
            print(f"  Skipping {filename} (already exists)")
            continue

        print(f"  Generating {filename}...")

        # Command-line args: vertices, edges_per_node, min_cap, max_cap, output_path
        args = [
            size,
            params["edges_per_node"],
            params["min_cap"],
            params["max_cap"],
            str(filepath.absolute()),
        ]

        success, error = run_cli_java(java_dir, "RandomGraph", args)
        if not success:
            print(f"    ERROR: {error}")
            return False

    return True


def generate_mesh_graphs(
    output_dir: Path, params: dict, size_pairs: list, n: int = None
):
    """Generate mesh graphs.

    Args:
        output_dir: Base output directory
        params: Dictionary with capacity, constant
        size_pairs: List of (rows, cols) tuples
        n: Number of graphs to generate (default: all)
    """
    print("\n" + "=" * 60)
    print("Generating Mesh Graphs")
    print("=" * 60)

    java_dir = GRAPH_GEN_DIR / "Mesh"
    graph_output_dir = output_dir / "Mesh"
    graph_output_dir.mkdir(parents=True, exist_ok=True)

    if not ensure_compiled(java_dir, "MeshGenerator.java"):
        return False

    pairs_to_use = size_pairs[:n] if n is not None else size_pairs
    for rows, cols in pairs_to_use:
        cap_type = "const" if params["constant"] else "rand"
        filename = f"{rows}r-{cols}c-{params['capacity']}cap-{cap_type}.txt"
        filepath = graph_output_dir / filename

        if filepath.exists():
            print(f"  Skipping {filename} (already exists)")
            continue

        print(f"  Generating {filename}...")

        # Command-line args: rows, cols, capacity, filename, [-cc for constant]
        args = [rows, cols, params["capacity"], str(filepath.absolute())]
        if params["constant"]:
            args.append("-cc")

        success, error = run_cli_java(java_dir, "MeshGenerator", args)
        if not success:
            print(f"    ERROR: {error}")
            return False

    return True


def generate_random_graphs(output_dir: Path, params: dict, sizes: list, n: int = None):
    """Generate random graphs.

    Args:
        output_dir: Base output directory
        params: Dictionary with density, min_cap, max_cap
        sizes: List of vertex counts
        n: Number of graphs to generate (default: all)
    """
    print("\n" + "=" * 60)
    print("Generating Random Graphs")
    print("=" * 60)

    java_dir = GRAPH_GEN_DIR / "Random"
    graph_output_dir = output_dir / "Random"
    graph_output_dir.mkdir(parents=True, exist_ok=True)

    if not ensure_compiled(java_dir, "BuildGraph.java"):
        return False

    sizes_to_use = sizes[:n] if n is not None else sizes
    for size in sizes_to_use:
        filename = f"{size}v-{params['density']}d-{params['min_cap']}min-{params['max_cap']}max.txt"
        filepath = graph_output_dir / filename

        if filepath.exists():
            print(f"  Skipping {filename} (already exists)")
            continue

        print(f"  Generating {filename}...")

        # Command-line args: vertices density min_cap max_cap output_file
        args = [
            size,
            params["density"],
            params["min_cap"],
            params["max_cap"],
            str(filepath.absolute()),
        ]

        success, error = run_cli_java(java_dir, "BuildGraph", args)
        if not success:
            print(f"    ERROR: {error}")
            return False

    return True


# =============================================================================
# Main
# =============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Generate graphs for max flow experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Phase 1 (defaults)
  python generate_graphs.py                    # Generate all graphs with defaults
  python generate_graphs.py -n 5               # Generate first 5 of each type

  # Phase 2 (custom parameters)
  python generate_graphs.py -o GeneratedGraphs2 --types random --random-density 10
  python generate_graphs.py -o GeneratedGraphs2 --types bipartite --bipartite-probability 0.3
  python generate_graphs.py -o GeneratedGraphs2 --types mesh --mesh-random --mesh-sizes 50,100,150
        """,
    )

    # General options
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=None,
        help="Number of graphs to generate per type (1-10, default: all)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--types",
        type=str,
        default=None,
        help="Comma-separated graph types to generate: bipartite,fixeddegree,mesh,random (default: all)",
    )

    # Bipartite parameters
    bipartite_group = parser.add_argument_group("Bipartite parameters")
    bipartite_group.add_argument(
        "--bipartite-probability",
        type=float,
        default=DEFAULT_BIPARTITE_PARAMS["probability"],
        help=f"Edge probability 0-1 (default: {DEFAULT_BIPARTITE_PARAMS['probability']})",
    )
    bipartite_group.add_argument(
        "--bipartite-min-cap",
        type=int,
        default=DEFAULT_BIPARTITE_PARAMS["min_cap"],
        help=f"Min capacity (default: {DEFAULT_BIPARTITE_PARAMS['min_cap']})",
    )
    bipartite_group.add_argument(
        "--bipartite-max-cap",
        type=int,
        default=DEFAULT_BIPARTITE_PARAMS["max_cap"],
        help=f"Max capacity (default: {DEFAULT_BIPARTITE_PARAMS['max_cap']})",
    )
    bipartite_group.add_argument(
        "--bipartite-sizes",
        type=str,
        default=None,
        help="Comma-separated sizes for source=sink (e.g., '50,100,200') or pairs (e.g., '50x100,100x200')",
    )
    bipartite_group.add_argument(
        "--bipartite-source-sizes",
        type=str,
        default=None,
        help="Comma-separated source node counts (use with --bipartite-sink-sizes)",
    )
    bipartite_group.add_argument(
        "--bipartite-sink-sizes",
        type=str,
        default=None,
        help="Comma-separated sink node counts (use with --bipartite-source-sizes)",
    )

    # FixedDegree parameters
    fixeddegree_group = parser.add_argument_group("FixedDegree parameters")
    fixeddegree_group.add_argument(
        "--fixeddegree-edges",
        type=int,
        default=DEFAULT_FIXED_DEGREE_PARAMS["edges_per_node"],
        help=f"Edges per node (default: {DEFAULT_FIXED_DEGREE_PARAMS['edges_per_node']})",
    )
    fixeddegree_group.add_argument(
        "--fixeddegree-min-cap",
        type=int,
        default=DEFAULT_FIXED_DEGREE_PARAMS["min_cap"],
        help=f"Min capacity (default: {DEFAULT_FIXED_DEGREE_PARAMS['min_cap']})",
    )
    fixeddegree_group.add_argument(
        "--fixeddegree-max-cap",
        type=int,
        default=DEFAULT_FIXED_DEGREE_PARAMS["max_cap"],
        help=f"Max capacity (default: {DEFAULT_FIXED_DEGREE_PARAMS['max_cap']})",
    )
    fixeddegree_group.add_argument(
        "--fixeddegree-sizes",
        type=str,
        default=None,
        help="Comma-separated vertex counts (default: 100,250,500,...,4000)",
    )

    # Mesh parameters
    mesh_group = parser.add_argument_group("Mesh parameters")
    mesh_group.add_argument(
        "--mesh-capacity",
        type=int,
        default=DEFAULT_MESH_PARAMS["capacity"],
        help=f"Capacity value (default: {DEFAULT_MESH_PARAMS['capacity']})",
    )
    mesh_cap_type = mesh_group.add_mutually_exclusive_group()
    mesh_cap_type.add_argument(
        "--mesh-constant",
        action="store_true",
        default=True,
        help="Use constant capacity (default)",
    )
    mesh_cap_type.add_argument(
        "--mesh-random",
        action="store_true",
        help="Use random capacities (1 to capacity)",
    )
    mesh_group.add_argument(
        "--mesh-sizes",
        type=str,
        default=None,
        help="Comma-separated sizes for rows=cols (e.g., '20,40,60') or pairs (e.g., '20x30,40x60')",
    )
    mesh_group.add_argument(
        "--mesh-rows",
        type=str,
        default=None,
        help="Comma-separated row counts (use with --mesh-cols)",
    )
    mesh_group.add_argument(
        "--mesh-cols",
        type=str,
        default=None,
        help="Comma-separated col counts (use with --mesh-rows)",
    )

    # Random parameters
    random_group = parser.add_argument_group("Random parameters")
    random_group.add_argument(
        "--random-density",
        type=int,
        default=DEFAULT_RANDOM_PARAMS["density"],
        help=f"Density 0-100 (default: {DEFAULT_RANDOM_PARAMS['density']})",
    )
    random_group.add_argument(
        "--random-min-cap",
        type=int,
        default=DEFAULT_RANDOM_PARAMS["min_cap"],
        help=f"Min capacity (default: {DEFAULT_RANDOM_PARAMS['min_cap']})",
    )
    random_group.add_argument(
        "--random-max-cap",
        type=int,
        default=DEFAULT_RANDOM_PARAMS["max_cap"],
        help=f"Max capacity (default: {DEFAULT_RANDOM_PARAMS['max_cap']})",
    )
    random_group.add_argument(
        "--random-sizes",
        type=str,
        default=None,
        help="Comma-separated vertex counts (default: 100,200,400,...,2000)",
    )

    args = parser.parse_args()

    # Validate and clamp n
    n = args.num
    if n is not None:
        if n < 1:
            print(f"Warning: n={n} is less than 1, defaulting to 1")
            n = 1
        elif n > 10:
            print(f"Warning: n={n} is greater than 10, defaulting to 10")
            n = 10

    # Parse output directory
    output_dir = Path(args.output)

    # Parse graph types
    if args.types:
        requested_types = [t.strip().lower() for t in args.types.split(",")]
    else:
        requested_types = ["bipartite", "fixeddegree", "mesh", "random"]

    # Build parameter dictionaries from CLI args
    bipartite_params = {
        "probability": args.bipartite_probability,
        "min_cap": args.bipartite_min_cap,
        "max_cap": args.bipartite_max_cap,
    }
    # Handle bipartite sizes: source/sink pairs or single sizes
    if args.bipartite_source_sizes and args.bipartite_sink_sizes:
        sources = parse_int_list(args.bipartite_source_sizes)
        sinks = parse_int_list(args.bipartite_sink_sizes)
        if len(sources) != len(sinks):
            print(
                "Error: --bipartite-source-sizes and --bipartite-sink-sizes must have same length"
            )
            return 1
        bipartite_size_pairs = list(zip(sources, sinks))
    elif args.bipartite_sizes:
        bipartite_size_pairs = parse_size_pairs(args.bipartite_sizes)
    else:
        bipartite_size_pairs = [(s, s) for s in DEFAULT_BIPARTITE_SIZES]

    fixeddegree_params = {
        "edges_per_node": args.fixeddegree_edges,
        "min_cap": args.fixeddegree_min_cap,
        "max_cap": args.fixeddegree_max_cap,
    }
    fixeddegree_sizes = (
        parse_int_list(args.fixeddegree_sizes)
        if args.fixeddegree_sizes
        else DEFAULT_FIXED_DEGREE_SIZES
    )

    mesh_params = {
        "capacity": args.mesh_capacity,
        "constant": not args.mesh_random,
    }
    # Handle mesh sizes: row/col pairs or single sizes
    if args.mesh_rows and args.mesh_cols:
        rows = parse_int_list(args.mesh_rows)
        cols = parse_int_list(args.mesh_cols)
        if len(rows) != len(cols):
            print("Error: --mesh-rows and --mesh-cols must have same length")
            return 1
        mesh_size_pairs = list(zip(rows, cols))
    elif args.mesh_sizes:
        mesh_size_pairs = parse_size_pairs(args.mesh_sizes)
    else:
        mesh_size_pairs = [(s, s) for s in DEFAULT_MESH_SIZES]

    random_params = {
        "density": args.random_density,
        "min_cap": args.random_min_cap,
        "max_cap": args.random_max_cap,
    }
    random_sizes = (
        parse_int_list(args.random_sizes) if args.random_sizes else DEFAULT_RANDOM_SIZES
    )

    # Print configuration
    print("=" * 60)
    print("Graph Generation")
    print("=" * 60)
    print(f"Output directory: {output_dir.absolute()}")
    print(f"Graph types: {', '.join(requested_types)}")
    if n is not None:
        print(f"Generating first {n} graphs of each type")

    # Check that graphGenerationCode directory exists
    if not GRAPH_GEN_DIR.exists():
        print(f"ERROR: {GRAPH_GEN_DIR} directory not found!")
        print("Make sure you're running this script from the project root.")
        return 1

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate requested graph types
    all_success = True

    if "bipartite" in requested_types:
        if not generate_bipartite_graphs(
            output_dir, bipartite_params, bipartite_size_pairs, n
        ):
            all_success = False

    if "fixeddegree" in requested_types:
        if not generate_fixed_degree_graphs(
            output_dir, fixeddegree_params, fixeddegree_sizes, n
        ):
            all_success = False

    if "mesh" in requested_types:
        if not generate_mesh_graphs(output_dir, mesh_params, mesh_size_pairs, n):
            all_success = False

    if "random" in requested_types:
        if not generate_random_graphs(output_dir, random_params, random_sizes, n):
            all_success = False

    # Summary
    print("\n" + "=" * 60)
    if all_success:
        print("✓ All graphs generated successfully!")
        print(f"  Output: {output_dir.absolute()}")

        # Count generated files
        total = sum(1 for _ in output_dir.rglob("*.txt"))
        print(f"  Total graphs: {total}")
    else:
        print("✗ Some graphs failed to generate. See errors above.")
        return 1

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
