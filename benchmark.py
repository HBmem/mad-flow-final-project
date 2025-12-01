#!/usr/bin/env python3
import argparse
import subprocess
import time
import os
import sys
import json
import csv
import statistics
import shutil
import multiprocessing
from pathlib import Path
from graph import Graph


def detect_python_command():
    """Detect whether to use 'python3' or 'python' command."""
    # Try python3 first
    try:
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return "python3"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fall back to python
    try:
        result = subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return "python"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Default to python3 if detection fails
    return "python3"


def run_max_flow(
    graph_path, source, sink, algorithm, mad_flow_script, python_cmd="python3"
):
    """Run mad-flow.py on a graph and measure execution time."""
    start_time = time.perf_counter()

    try:
        result = subprocess.run(
            [
                python_cmd,
                mad_flow_script,
                "-g",
                graph_path,
                "-s",
                source,
                "-t",
                sink,
                "-a",
                algorithm,
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
    (
        graph_file,
        graph_type,
        num_runs,
        source,
        sink,
        algorithm,
        mad_flow_script,
        python_cmd,
    ) = args_tuple

    # Load graph and get size information
    try:
        graph = Graph(str(graph_file))
        num_vertices = graph.get_num_vertices()
        num_edges = graph.get_num_edges()
    except Exception as e:
        error_msg = f"ERROR: {graph_type}/{graph_file.name} - Failed to load graph: {e}"
        print(error_msg, file=sys.stderr)
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
            str(graph_file), source, sink, algorithm, mad_flow_script, python_cmd
        )

        if error:
            error_msg = f"Run {run+1}: {error}"
            errors.append(error_msg)
            print(
                f"ERROR: {graph_type}/{graph_file.name} - {error_msg}", file=sys.stderr
            )
        elif elapsed is not None:
            times.append(elapsed)
            max_flow_values.append(flow)
            if max_flow_value is None:
                max_flow_value = flow
            elif max_flow_value != flow:
                # Inconsistent max_flow across runs - this is an error!
                error_msg = f"Inconsistent max_flow values: expected {max_flow_value}, got {flow} on run {run+1}"
                print(
                    f"ERROR: {graph_type}/{graph_file.name} - {error_msg}",
                    file=sys.stderr,
                )
                return {
                    "graph_file": graph_file.name,
                    "graph_type": graph_type,
                    "error": error_msg,
                    "success": False,
                }

    if not times:
        error_msg = f"All {num_runs} runs failed"
        print(f"ERROR: {graph_type}/{graph_file.name} - {error_msg}", file=sys.stderr)
        return {
            "graph_file": graph_file.name,
            "graph_type": graph_type,
            "error": error_msg,
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
    python_cmd="python3",
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
                (
                    graph_file,
                    normalized_type,
                    num_runs,
                    source,
                    sink,
                    algorithm,
                    mad_flow_script,
                    python_cmd,
                )
            )

            # Track graph types
            if normalized_type not in graph_type_info:
                graph_type_info[normalized_type] = []
            graph_type_info[normalized_type].append(graph_file.name)

    if not tasks:
        print("\nERROR: No valid graph files found to process")
        return False

    # Process graphs in parallel
    print(f"\nProcessing {len(tasks)} graphs using {num_processes} processes...")

    with multiprocessing.Pool(processes=num_processes) as pool:
        all_results = pool.map(process_single_graph, tasks)

    # Group results by graph type and track failures
    results_by_type = {}
    failed_graphs = []
    successful_count = 0

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
            successful_count += 1

            stats = result["statistics"]
            print(
                f"  {graph_type}/{result['graph_file']}: "
                f"min={stats['min']:.6f}s, mean={stats['mean']:.6f}s, "
                f"max={stats['max']:.6f}s, stddev={stats['stddev']:.6f}s"
            )
        else:
            failed_graphs.append(f"{graph_type}/{result['graph_file']}")
            print(
                f"  {graph_type}/{result['graph_file']}: ERROR - {result.get('error', 'Unknown error')}"
            )

    # Check if all graphs failed
    if successful_count == 0:
        print("\n" + "=" * 60)
        print("FATAL ERROR: All graphs failed to process!")
        print("=" * 60)
        print(f"\nFailed graphs ({len(failed_graphs)}):")
        for failed in failed_graphs:
            print(f"  - {failed}")
        return False

    # Save results for each graph type
    print("\nSaving results...")
    for graph_type, results in results_by_type.items():
        if results:
            save_results(output_path, algorithm, graph_type, results)
            print(f"  Saved results for {graph_type} ({len(results)} graphs)")

    # Report any failures
    if failed_graphs:
        print(f"\n⚠️  WARNING: {len(failed_graphs)} graph(s) failed (see errors above)")
        print(f"✓  Successfully processed {successful_count} graph(s)")

    return True


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
        default=None,
        help='Algorithm(s) to benchmark: comma-separated list (e.g., "ford_fulkerson,scaling_ford_fulkerson") or single algorithm. If not specified, benchmarks all implemented algorithms.',
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

    # Detect python command
    python_cmd = detect_python_command()
    print(f"Using Python command: {python_cmd}")

    # Determine which algorithms to benchmark
    valid_algorithms = ["ford_fulkerson", "scaling_ford_fulkerson", "preflow_push"]
    implemented_algorithms = [
        "ford_fulkerson",
        "scaling_ford_fulkerson",
        "preflow_push",
    ]

    if args.algorithm:
        # Parse comma-separated list
        algorithms = [alg.strip() for alg in args.algorithm.split(",")]

        # Validate algorithms
        invalid_algorithms = [alg for alg in algorithms if alg not in valid_algorithms]
        if invalid_algorithms:
            print(f"Error: Invalid algorithm(s): {', '.join(invalid_algorithms)}")
            print(f"Valid algorithms: {', '.join(valid_algorithms)}")
            return 1

    else:
        # Auto-detect: use all implemented algorithms
        algorithms = implemented_algorithms
        print(f"Auto-detected algorithms: {', '.join(algorithms)}")

    # Auto-detect script if not specified (defaults to mad-flow.py)
    if args.mad_flow_script is None:
        args.mad_flow_script = "mad-flow.py"

    # Validate paths
    if not os.path.exists(args.input):
        print(f"Error: Input directory '{args.input}' does not exist")
        return 1

    if not os.path.exists(args.mad_flow_script):
        print(f"Error: Max flow script '{args.mad_flow_script}' not found")
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
    print(f"  Algorithm(s): {', '.join(algorithms)}")
    print(f"  Algorithm script: {args.mad_flow_script}")
    print(f"  Graph types: {args.types if args.types else 'all'}")
    print(f"  Runs per graph: {args.runs}")
    print(f"  Parallel processes: {args.processes}")
    print(f"  Source node: {args.source}")
    print(f"  Sink node: {args.sink}")

    # Run benchmarks for each algorithm
    all_success = True
    for i, algorithm in enumerate(algorithms):
        if len(algorithms) > 1:
            print(f"\n{'='*60}")
            print(f"Benchmarking algorithm {i+1}/{len(algorithms)}: {algorithm}")
            print(f"{'='*60}")

        success = benchmark_graphs(
            args.input,
            args.output,
            algorithm,
            args.types,
            args.runs,
            args.source,
            args.sink,
            args.mad_flow_script,
            args.processes,
            python_cmd,
        )

        if not success:
            print(f"\n✗ Benchmark FAILED for algorithm: {algorithm}")
            all_success = False
        elif len(algorithms) > 1:
            print(f"\n✓ Completed benchmark for: {algorithm}")

    if not all_success:
        print("\n✗ Some benchmarks FAILED")
        return 1

    if len(algorithms) > 1:
        print(f"\n{'='*60}")
        print(f"✓ All benchmarks complete! ({len(algorithms)} algorithms)")
        print(f"{'='*60}")
    else:
        print("\n✓ Benchmark complete!")

    return 0


if __name__ == "__main__":
    exit(main())
