#!/usr/bin/env python3
import argparse
import subprocess
import time
import os
import json
import csv
import statistics
import shutil
import multiprocessing
from pathlib import Path
from graph import Graph


def run_max_flow(graph_path, source, sink, mad_flow_script):
    """Run mad-flow.py on a graph and measure execution time."""
    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            [
                "python3",
                mad_flow_script,
                "-g",
                graph_path,
                "-s",
                source,
                "-t",
                sink,
                "--json",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=3600,  # 1 hour timeout
        )

        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        # Parse JSON output
        try:
            output_data = json.loads(result.stdout.strip())
            max_flow = output_data.get("max_flow")
        except json.JSONDecodeError:
            max_flow = None

        return elapsed_time, max_flow, None

    except subprocess.TimeoutExpired:
        return None, None, "Timeout"
    except subprocess.CalledProcessError as e:
        return None, None, f"Error: {e.stderr}"
    except Exception as e:
        return None, None, f"Exception: {str(e)}"


def should_skip_file(filename):
    """Check if file should be skipped based on name patterns."""
    skip_patterns = ["readme", "read me", "output", "test"]
    filename_lower = filename.lower()

    for pattern in skip_patterns:
        if pattern in filename_lower:
            return True
    return False


def is_valid_graph_file(file_path):
    """
    Validate that a file has proper graph format.
    Expected format: source_node destination_node weight
    """
    try:
        with open(file_path, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

            if not lines:
                return False, "Empty file"

            # Check first few lines to validate format
            sample_size = min(5, len(lines))
            for i, line in enumerate(lines[:sample_size]):
                fields = line.split()
                if len(fields) < 3:
                    return False, f"Line {i+1} has fewer than 3 fields"

                # Try to parse the weight as a number
                try:
                    int(fields[2])
                except (ValueError, IndexError):
                    return False, f"Line {i+1} has invalid weight"

            return True, None

    except Exception as e:
        return False, str(e)


def calculate_statistics(times):
    """Calculate statistical measures from a list of times."""
    if not times:
        return None

    return {
        "min": min(times),
        "max": max(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "stddev": statistics.stdev(times) if len(times) > 1 else 0.0,
    }


def process_single_graph(args_tuple):
    """
    Worker function to process a single graph file.
    Takes a tuple of arguments for multiprocessing compatibility.
    """
    graph_file, graph_type, num_runs, source, sink, mad_flow_script = args_tuple

    # Load graph and get size information
    try:
        graph = Graph(str(graph_file))
        num_vertices = graph.get_num_vertices()
        num_edges = graph.get_num_edges()
    except Exception as e:
        return {
            "graph_file": graph_file.name,
            "graph_type": graph_type,
            "error": f"Failed to load graph: {e}",
            "success": False,
        }

    # Run benchmark multiple times
    times = []
    max_flow_value = None
    max_flow_values = []  # Track all max_flow values to verify consistency
    errors = []

    for run in range(num_runs):
        elapsed, flow, error = run_max_flow(
            str(graph_file), source, sink, mad_flow_script
        )

        if error:
            errors.append(f"Run {run+1}: {error}")
        elif elapsed is not None:
            times.append(elapsed)
            max_flow_values.append(flow)
            if max_flow_value is None:
                max_flow_value = flow
            elif max_flow_value != flow:
                # Inconsistent max_flow across runs - this is an error!
                return {
                    "graph_file": graph_file.name,
                    "graph_type": graph_type,
                    "error": f"Inconsistent max_flow values: expected {max_flow_value}, got {flow} on run {run+1}",
                    "success": False,
                }

    if not times:
        return {
            "graph_file": graph_file.name,
            "graph_type": graph_type,
            "error": f"All runs failed",
            "errors": errors,
            "success": False,
        }

    # Calculate statistics
    stats = calculate_statistics(times)

    return {
        "graph_file": graph_file.name,
        "graph_type": graph_type,
        "num_vertices": num_vertices,
        "num_edges": num_edges,
        "max_flow": max_flow_value,
        "num_successful_runs": len(times),
        "num_failed_runs": num_runs - len(times),
        "statistics": stats,
        "all_times": times,
        "errors": errors if errors else None,
        "success": True,
    }


def benchmark_graphs(
    input_dir,
    output_dir,
    algorithm,
    graph_types,
    num_runs,
    source,
    sink,
    mad_flow_script,
    num_processes,
):
    """Benchmark all graphs in the input directory using multiprocessing."""
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Map directory names to normalized names (case insensitive, lowercase)
    type_mapping = {
        "bipartite": "bipartite",
        "mesh": "mesh",
        "random": "random",
        "fixeddegree": "fixeddegree",
    }

    # If specific types requested, filter them
    if graph_types:
        requested_types = [t.lower().strip() for t in graph_types.split(",")]
    else:
        requested_types = None

    # Collect all graph files to process
    tasks = []
    graph_type_info = {}  # Track which files belong to which type

    for subdir in sorted(input_path.iterdir()):
        if not subdir.is_dir():
            continue

        graph_type = subdir.name.lower()

        # Normalize graph type name
        if graph_type not in type_mapping:
            continue

        normalized_type = type_mapping[graph_type]

        # Filter by requested types if specified
        if requested_types and normalized_type not in requested_types:
            continue

        print(f"\nCollecting {normalized_type} graphs from {subdir.name}/")

        # Find all .txt files
        graph_files = sorted([f for f in subdir.glob("*.txt")])

        if not graph_files:
            print(f"  No .txt files found in {subdir.name}/")
            continue

        for graph_file in graph_files:
            # Skip files with non-graph names
            if should_skip_file(graph_file.name):
                print(f"  Skipping {graph_file.name} (non-graph file)")
                continue

            # Validate graph file format
            is_valid, error_msg = is_valid_graph_file(graph_file)
            if not is_valid:
                print(f"  Skipping {graph_file.name} (invalid format: {error_msg})")
                continue

            # Add to tasks
            tasks.append(
                (graph_file, normalized_type, num_runs, source, sink, mad_flow_script)
            )

            # Track graph types
            if normalized_type not in graph_type_info:
                graph_type_info[normalized_type] = []
            graph_type_info[normalized_type].append(graph_file.name)

    if not tasks:
        print("\nNo valid graph files found to process")
        return

    # Process graphs in parallel
    print(f"\nProcessing {len(tasks)} graphs using {num_processes} processes...")

    with multiprocessing.Pool(processes=num_processes) as pool:
        all_results = pool.map(process_single_graph, tasks)

    # Group results by graph type
    results_by_type = {}
    for result in all_results:
        graph_type = result["graph_type"]

        if graph_type not in results_by_type:
            results_by_type[graph_type] = []

        if result["success"]:
            # Remove graph_type and success fields as they're not needed in final output
            clean_result = {
                k: v for k, v in result.items() if k not in ["graph_type", "success"]
            }
            results_by_type[graph_type].append(clean_result)

            stats = result["statistics"]
            print(
                f"  {graph_type}/{result['graph_file']}: "
                f"min={stats['min']:.6f}s, mean={stats['mean']:.6f}s, "
                f"max={stats['max']:.6f}s, stddev={stats['stddev']:.6f}s"
            )
        else:
            print(
                f"  {graph_type}/{result['graph_file']}: ERROR - {result.get('error', 'Unknown error')}"
            )

    # Save results for each graph type
    print("\nSaving results...")
    for graph_type, results in results_by_type.items():
        if results:
            save_results(output_path, algorithm, graph_type, results)
            print(f"  Saved results for {graph_type} ({len(results)} graphs)")


def save_results(output_path, algorithm, graph_type, results):
    """Save results to JSON and CSV files."""
    # Create output directory structure
    output_dir = output_path / algorithm / graph_type
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save JSON
    json_path = output_dir / "results.json"
    with open(json_path, "w") as f:
        json.dump(
            {"algorithm": algorithm, "graph_type": graph_type, "results": results},
            f,
            indent=2,
        )

    # Save CSV
    csv_path = output_dir / "results.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "graph_file",
                "num_vertices",
                "num_edges",
                "max_flow",
                "successful_runs",
                "failed_runs",
                "min_time",
                "max_time",
                "mean_time",
                "median_time",
                "stddev_time",
            ]
        )

        for result in results:
            stats = result["statistics"]
            writer.writerow(
                [
                    result["graph_file"],
                    result["num_vertices"],
                    result["num_edges"],
                    result["max_flow"],
                    result["num_successful_runs"],
                    result["num_failed_runs"],
                    stats["min"],
                    stats["max"],
                    stats["mean"],
                    stats["median"],
                    stats["stddev"],
                ]
            )


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark max flow algorithms on graph datasets"
    )

    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Input directory containing graph type subdirectories",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="BenchmarkResultsData",
        help="Output directory for results (default: BenchmarkResultsData)",
    )

    parser.add_argument(
        "-a",
        "--algorithm",
        type=str,
        choices=["ford_fulkerson", "scaling_ford_fulkerson", "preflow_push"],
        default="ford_fulkerson",
        help="Algorithm to benchmark (default: ford_fulkerson)",
    )

    parser.add_argument(
        "-t",
        "--types",
        type=str,
        default=None,
        help='Comma-separated list of graph types to process (e.g., "bipartite,mesh")',
    )

    parser.add_argument(
        "-r",
        "--runs",
        type=int,
        default=10,
        help="Number of runs per graph (default: 10)",
    )

    parser.add_argument(
        "-s", "--source", type=str, default="s", help="Source node (default: s)"
    )

    parser.add_argument("--sink", type=str, default="t", help="Sink node (default: t)")

    parser.add_argument(
        "-m",
        "--mad-flow-script",
        type=str,
        default="mad-flow.py",
        help="Path to mad-flow.py script (default: mad-flow.py)",
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove output directory before starting (if it exists)",
    )

    parser.add_argument(
        "-p",
        "--processes",
        type=int,
        default=multiprocessing.cpu_count(),
        help=f"Number of parallel processes (default: {multiprocessing.cpu_count()}, detected CPU count)",
    )

    args = parser.parse_args()

    # Validate algorithm implementation
    if args.algorithm != "ford_fulkerson":
        print(f"WARNING: Algorithm '{args.algorithm}' not yet implemented.")
        print("Currently only 'ford_fulkerson' is supported.")
        print("Proceeding with ford_fulkerson...")
        args.algorithm = "ford_fulkerson"

    # Validate paths
    if not os.path.exists(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return 1

    if not os.path.exists(args.mad_flow_script):
        print(f"Error: Script '{args.mad_flow_script}' does not exist")
        return 1

    # Validate processes
    if args.processes < 1:
        print(f"Error: Number of processes must be at least 1")
        return 1

    # Handle output directory
    if os.path.exists(args.output):
        if args.clean:
            print(f"Cleaning output directory: {args.output}")
            shutil.rmtree(args.output)
            print(f"  Removed existing directory")
        else:
            print(f"Error: Output directory '{args.output}' already exists")
            print(
                f"Use --clean flag to remove it, or specify a different output directory"
            )
            return 1

    print(f"Benchmark Configuration:")
    print(f"  Input directory: {args.input}")
    print(f"  Output directory: {args.output}")
    print(f"  Algorithm: {args.algorithm}")
    print(f"  Graph types: {args.types if args.types else 'all'}")
    print(f"  Runs per graph: {args.runs}")
    print(f"  Parallel processes: {args.processes}")
    print(f"  Source node: {args.source}")
    print(f"  Sink node: {args.sink}")

    # Run benchmark
    benchmark_graphs(
        args.input,
        args.output,
        args.algorithm,
        args.types,
        args.runs,
        args.source,
        args.sink,
        args.mad_flow_script,
        args.processes,
    )

    print("\nBenchmark complete!")
    return 0


if __name__ == "__main__":
    exit(main())
