#!/usr/bin/env python3
import argparse
import json
import os
import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend


def read_results(results_dir, algorithm, graph_type):
    """Read benchmark results from JSON file."""
    json_path = Path(results_dir) / algorithm / graph_type / "results.json"

    if not json_path.exists():
        return None

    with open(json_path, "r") as f:
        data = json.load(f)

    return data.get("results", [])


def plot_bar_chart(
    x_values, y_values, labels, title, xlabel, ylabel, output_path, annotations=None
):
    """Create a bar chart and save to file."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create bars
    bars = ax.bar(range(len(x_values)), y_values, color="steelblue", alpha=0.8)

    # Set labels
    ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
    ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Set x-axis ticks and labels
    ax.set_xticks(range(len(x_values)))
    ax.set_xticklabels(labels, rotation=45, ha="right")

    # Add grid for better readability
    ax.grid(axis="y", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)

    # Add value labels on top of bars
    for i, (bar, value) in enumerate(zip(bars, y_values)):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{value:.4f}s",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    # Add annotations if provided (for n×m plots)
    if annotations:
        for i, (bar, annotation) in enumerate(zip(bars, annotations)):
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                bar.get_height() * 0.5,
                annotation,
                ha="center",
                va="center",
                fontsize=7,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.5),
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()

    print(f"  Saved: {output_path}")


def generate_metric_plots(
    graph_type,
    output_dir,
    metric_name,
    x_values,
    y_mean,
    y_max,
    x_labels,
    xlabel,
    algorithm,
    annotations=None,
):
    """Generate mean and max plots for a specific metric (vertices, edges, or size)."""
    # Mean time plot
    plot_bar_chart(
        x_values=x_values,
        y_values=y_mean,
        labels=x_labels,
        title=f"{algorithm.replace('_', ' ').title()} - {graph_type.capitalize()} - Mean Runtime vs {metric_name}",
        xlabel=xlabel,
        ylabel="Mean Runtime (seconds)",
        output_path=output_dir / "mean_runtime.png",
        annotations=annotations,
    )

    # Max time plot
    plot_bar_chart(
        x_values=x_values,
        y_values=y_max,
        labels=x_labels,
        title=f"{algorithm.replace('_', ' ').title()} - {graph_type.capitalize()} - Max Runtime vs {metric_name}",
        xlabel=xlabel,
        ylabel="Max Runtime (seconds)",
        output_path=output_dir / "max_runtime.png",
        annotations=annotations,
    )


def generate_plots_for_graph_type(results_dir, plots_dir, algorithm, graph_type):
    """Generate all plots for a single graph type."""
    # Read results
    results = read_results(results_dir, algorithm, graph_type)

    if not results:
        print(f"  No results found for {graph_type}")
        return 0

    # Sort results by number of vertices for consistent ordering
    results = sorted(results, key=lambda x: (x["num_vertices"], x["num_edges"]))

    # Extract data
    num_vertices = [r["num_vertices"] for r in results]
    num_edges = [r["num_edges"] for r in results]
    mean_times = [r["statistics"]["mean"] for r in results]
    max_times = [r["statistics"]["max"] for r in results]

    # Create output directory for this graph type
    output_dir = Path(plots_dir) / algorithm / graph_type
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate size plots (vertices × edges) with n and m annotations
    products = [v * e for v, e in zip(num_vertices, num_edges)]
    annotations = [f"n={v}\nm={e}" for v, e in zip(num_vertices, num_edges)]

    # Sort by product
    sorted_by_product = sorted(
        zip(products, mean_times, max_times, annotations), key=lambda x: x[0]
    )
    products_sorted = [x[0] for x in sorted_by_product]
    mean_times_by_product = [x[1] for x in sorted_by_product]
    max_times_by_product = [x[2] for x in sorted_by_product]
    annotations_sorted = [x[3] for x in sorted_by_product]

    generate_metric_plots(
        graph_type=graph_type,
        output_dir=output_dir,
        metric_name="Input Size (n×m)",
        x_values=products_sorted,
        y_mean=mean_times_by_product,
        y_max=max_times_by_product,
        x_labels=[str(p) for p in products_sorted],
        xlabel="Input Size (vertices × edges)",
        algorithm=algorithm,
        annotations=annotations_sorted,
    )

    return 2  # Number of plots generated (mean and max)


def generate_plots(results_dir, plots_dir, algorithm, graph_types):
    """Generate all plots for specified graph types and algorithm."""
    results_path = Path(results_dir)

    # Determine which graph types to process
    if graph_types:
        requested_types = [t.lower().strip() for t in graph_types.split(",")]
    else:
        # Find all available graph types
        algorithm_dir = results_path / algorithm
        if not algorithm_dir.exists():
            print(f"  Warning: No results found for algorithm '{algorithm}'")
            return False

        requested_types = [d.name for d in algorithm_dir.iterdir() if d.is_dir()]

    if not requested_types:
        print(f"  Warning: No graph types found for algorithm '{algorithm}'")
        return False

    # Process each graph type
    total_plots = 0
    for graph_type in requested_types:
        print(f"  Generating plots for {graph_type}...")
        plots_generated = generate_plots_for_graph_type(
            results_dir, plots_dir, algorithm, graph_type
        )
        if plots_generated > 0:
            print(f"    Generated {plots_generated} plots for {graph_type}")
            total_plots += plots_generated

    return total_plots > 0


def main():
    parser = argparse.ArgumentParser(
        description="Generate plots from benchmark results"
    )

    parser.add_argument(
        "-r",
        "--results",
        type=str,
        default="BenchmarkResultsData",
        help="Directory containing benchmark results (default: BenchmarkResultsData)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="BenchmarkResultsPlots",
        help="Output directory for plots (default: BenchmarkResultsPlots)",
    )

    parser.add_argument(
        "-a",
        "--algorithm",
        type=str,
        default=None,
        help='Algorithm(s) to plot: comma-separated list (e.g., "ford_fulkerson,scaling_ford_fulkerson") or single algorithm. If not specified, plots all available algorithms.',
    )

    parser.add_argument(
        "-t",
        "--types",
        type=str,
        default=None,
        help='Comma-separated list of graph types to plot (e.g., "bipartite,mesh")',
    )

    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove output directory before starting (if it exists)",
    )

    args = parser.parse_args()

    # Validate paths
    if not os.path.exists(args.results):
        print(f"Error: Results directory '{args.results}' does not exist")
        return 1

    # Determine which algorithms to plot
    if args.algorithm:
        # Parse comma-separated list
        algorithms = [alg.strip() for alg in args.algorithm.split(",")]
    else:
        # Auto-detect algorithms from results directory
        results_path = Path(args.results)
        algorithms = [d.name for d in results_path.iterdir() if d.is_dir()]

        if not algorithms:
            print(f"Error: No algorithm directories found in '{args.results}'")
            return 1

        print(f"Auto-detected algorithms: {', '.join(algorithms)}")

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

    print(f"Plot Generation Configuration:")
    print(f"  Results directory: {args.results}")
    print(f"  Output directory: {args.output}")
    print(f"  Algorithm(s): {', '.join(algorithms)}")
    print(f"  Graph types: {args.types if args.types else 'all'}")

    # Generate plots for each algorithm
    all_success = True
    for i, algorithm in enumerate(algorithms):
        if len(algorithms) > 1:
            print(f"\n{'='*60}")
            print(
                f"Generating plots for algorithm {i+1}/{len(algorithms)}: {algorithm}"
            )
            print(f"{'='*60}")

        success = generate_plots(args.results, args.output, algorithm, args.types)

        if not success:
            print(f"\n  Warning: No plots generated for algorithm: {algorithm}")
            all_success = False
        elif len(algorithms) > 1:
            print(f"\n✓ Completed plots for: {algorithm}")

    if len(algorithms) > 1:
        print(f"\n{'='*60}")
        if all_success:
            print(f"✓ All plot generation complete! ({len(algorithms)} algorithms)")
        else:
            print(
                f"⚠️  Plot generation complete with some warnings ({len(algorithms)} algorithms)"
            )
        print(f"{'='*60}")
    else:
        print("\n✓ Plot generation complete!")

    return 0


if __name__ == "__main__":
    exit(main())
