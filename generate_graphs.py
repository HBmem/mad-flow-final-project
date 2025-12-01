#!/usr/bin/env python3
"""
Graph Generation Script for Phase 1 Experiments

Generates all graphs according to the Phase 1 plan (see docs/graph-generation-phase1.md):
- 10 Bipartite graphs (varying source/sink node counts)
- 10 FixedDegree graphs (varying vertex count)
- 10 Mesh graphs (varying rows/cols)
- 10 Random graphs (varying vertex count)

Output directory: GeneratedGraphs/
"""

import argparse
import subprocess
import sys
from pathlib import Path


# =============================================================================
# Configuration
# =============================================================================

OUTPUT_DIR = Path("GeneratedGraphs")
GRAPH_GEN_DIR = Path("graphGenerationCode")

# Fixed parameters for each graph type
# NOTE: Tuned for ~5 minute max Ford-Fulkerson runtimes
# Ford-Fulkerson is O(V*E*max_flow), so we need high max_flow for longer runtimes
BIPARTITE_PARAMS = {"probability": 0.5, "min_cap": 1, "max_cap": 1000}
FIXED_DEGREE_PARAMS = {
    "edges_per_node": 30,  # 30 edges to create more flow paths → higher max_flow
    "min_cap": 1,
    "max_cap": 1000,
}
MESH_PARAMS = {"capacity": 1000, "constant": True}  # Higher capacity for more flow
RANDOM_PARAMS = {
    "density": 30,  # density 30 for more edges and higher max_flow
    "min_cap": 1,
    "max_cap": 1000,
}

# Graph sizes to generate - scaled for ~5 minute max Ford-Fulkerson runtime
# FF is O(V*E*f), bipartite scales as n^4, so 2x size ≈ 16x runtime
BIPARTITE_SIZES = [
    50,
    100,
    200,
    300,
    400,
    500,
    600,
    800,
    1000,
    1200,
]  # source = sink nodes (largest ~5 min)

# FixedDegree needs high edges_per_node (30) to get meaningful max_flow
FIXED_DEGREE_SIZES = [
    100,
    250,
    500,
    1000,
    1500,
    2000,
    2500,
    3000,
    3500,
    4000,
]  # vertices

# Mesh scales more slowly - need larger sizes
MESH_SIZES = [20, 40, 60, 80, 100, 125, 150, 200, 250, 300]  # rows = cols

# Random with density 30 for more edges and higher max_flow
RANDOM_SIZES = [100, 200, 400, 600, 800, 1000, 1250, 1500, 1750, 2000]  # vertices


# =============================================================================
# Helper Functions
# =============================================================================


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


def generate_bipartite_graphs(n: int = None):
    """Generate bipartite graphs.

    Args:
        n: Number of graphs to generate (default: all)
    """
    print("\n" + "=" * 60)
    print("Generating Bipartite Graphs")
    print("=" * 60)

    java_dir = GRAPH_GEN_DIR / "Bipartite"
    output_dir = OUTPUT_DIR / "Bipartite"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ensure_compiled(java_dir, "BipartiteGraph.java"):
        return False

    p = BIPARTITE_PARAMS
    sizes = BIPARTITE_SIZES[:n] if n is not None else BIPARTITE_SIZES
    for size in sizes:
        filename = f"{size}s-{size}t-05p-{p['min_cap']}min-{p['max_cap']}max.txt"
        filepath = output_dir / filename

        if filepath.exists():
            print(f"  Skipping {filename} (already exists)")
            continue

        print(f"  Generating {filename}...")

        # Command-line args: source_nodes sink_nodes probability min_cap max_cap output_file
        args = [
            size,
            size,
            p["probability"],
            p["min_cap"],
            p["max_cap"],
            str(filepath.absolute()),
        ]

        success, error = run_cli_java(java_dir, "BipartiteGraph", args)
        if not success:
            print(f"    ERROR: {error}")
            return False

    return True


def generate_fixed_degree_graphs(n: int = None):
    """Generate fixed degree graphs.

    Args:
        n: Number of graphs to generate (default: all)
    """
    print("\n" + "=" * 60)
    print("Generating FixedDegree Graphs")
    print("=" * 60)

    java_dir = GRAPH_GEN_DIR / "FixedDegree"
    output_dir = OUTPUT_DIR / "FixedDegree"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ensure_compiled(java_dir, "RandomGraph.java"):
        return False

    p = FIXED_DEGREE_PARAMS
    sizes = FIXED_DEGREE_SIZES[:n] if n is not None else FIXED_DEGREE_SIZES
    for size in sizes:
        filename = (
            f"{size}v-{p['edges_per_node']}out-{p['min_cap']}min-{p['max_cap']}max.txt"
        )
        filepath = output_dir / filename

        if filepath.exists():
            print(f"  Skipping {filename} (already exists)")
            continue

        print(f"  Generating {filename}...")

        # Command-line args: vertices, edges_per_node, min_cap, max_cap, output_path
        args = [
            size,
            p["edges_per_node"],
            p["min_cap"],
            p["max_cap"],
            str(filepath.absolute()),
        ]

        success, error = run_cli_java(java_dir, "RandomGraph", args)
        if not success:
            print(f"    ERROR: {error}")
            return False

    return True


def generate_mesh_graphs(n: int = None):
    """Generate mesh graphs.

    Args:
        n: Number of graphs to generate (default: all)
    """
    print("\n" + "=" * 60)
    print("Generating Mesh Graphs")
    print("=" * 60)

    java_dir = GRAPH_GEN_DIR / "Mesh"
    output_dir = OUTPUT_DIR / "Mesh"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ensure_compiled(java_dir, "MeshGenerator.java"):
        return False

    p = MESH_PARAMS
    sizes = MESH_SIZES[:n] if n is not None else MESH_SIZES
    for size in sizes:
        filename = f"{size}r-{size}c-{p['capacity']}cap-const.txt"
        filepath = output_dir / filename

        if filepath.exists():
            print(f"  Skipping {filename} (already exists)")
            continue

        print(f"  Generating {filename}...")

        # Command-line args: rows, cols, capacity, filename, [-cc for constant]
        args = [size, size, p["capacity"], str(filepath.absolute())]
        if p["constant"]:
            args.append("-cc")

        success, error = run_cli_java(java_dir, "MeshGenerator", args)
        if not success:
            print(f"    ERROR: {error}")
            return False

    return True


def generate_random_graphs(n: int = None):
    """Generate random graphs.

    Args:
        n: Number of graphs to generate (default: all)
    """
    print("\n" + "=" * 60)
    print("Generating Random Graphs")
    print("=" * 60)

    java_dir = GRAPH_GEN_DIR / "Random"
    output_dir = OUTPUT_DIR / "Random"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not ensure_compiled(java_dir, "BuildGraph.java"):
        return False

    p = RANDOM_PARAMS
    sizes = RANDOM_SIZES[:n] if n is not None else RANDOM_SIZES
    for size in sizes:
        filename = f"{size}v-{p['density']}d-{p['min_cap']}min-{p['max_cap']}max.txt"
        filepath = output_dir / filename

        if filepath.exists():
            print(f"  Skipping {filename} (already exists)")
            continue

        print(f"  Generating {filename}...")

        # Command-line args: vertices density min_cap max_cap output_file
        args = [
            size,
            p["density"],
            p["min_cap"],
            p["max_cap"],
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
        description="Generate graphs for Phase 1 experiments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_graphs.py           # Generate all graphs (default)
  python generate_graphs.py -n 5      # Generate first 5 graphs of each type
  python generate_graphs.py --num 8   # Generate first 8 graphs of each type
        """,
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        default=None,
        help="Number of graphs to generate per type (1-10, default: all)",
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

    print("=" * 60)
    print("Phase 1 Graph Generation")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    if n is not None:
        print(f"Generating first {n} graphs of each type")

    # Check that graphGenerationCode directory exists
    if not GRAPH_GEN_DIR.exists():
        print(f"ERROR: {GRAPH_GEN_DIR} directory not found!")
        print("Make sure you're running this script from the project root.")
        return 1

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Generate all graph types
    all_success = True

    if not generate_bipartite_graphs(n):
        all_success = False

    if not generate_fixed_degree_graphs(n):
        all_success = False

    if not generate_mesh_graphs(n):
        all_success = False

    if not generate_random_graphs(n):
        all_success = False

    # Summary
    print("\n" + "=" * 60)
    if all_success:
        print("✓ All graphs generated successfully!")
        print(f"  Output: {OUTPUT_DIR.absolute()}")

        # Count generated files
        total = sum(1 for _ in OUTPUT_DIR.rglob("*.txt"))
        print(f"  Total graphs: {total}")
    else:
        print("✗ Some graphs failed to generate. See errors above.")
        return 1

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
