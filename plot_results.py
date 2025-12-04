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


ALGORITHM_COLORS = {
    "ford_fulkerson": "#e74c3c",  # Red
    "scaling_ford_fulkerson": "#3498db",  # Blue
    "preflow_push": "#2ecc71",  # Green
}

ALGORITHM_LABELS = {
    "ford_fulkerson": "Ford-Fulkerson",
    "scaling_ford_fulkerson": "Scaling FF",
    "preflow_push": "Preflow-Push",
}


def plot_bar_chart(
    x_values,
    y_values,
    labels,
    title,
    xlabel,
    ylabel,
    output_path,
    annotations=None,
    max_flows=None,
):
    """Create a bar chart and save to file."""
    fig, ax = plt.subplots(figsize=(14, 7))

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

    # Calculate threshold for "small" bars (labels should float above)
    max_height = max(y_values) if y_values else 1
    small_bar_threshold = max_height * 0.15  # Bars under 15% of max are "small"

    # Add annotations if provided (for n×m plots)
    if annotations:
        for i, (bar, annotation) in enumerate(zip(bars, annotations)):
            height = bar.get_height()
            if height < small_bar_threshold:
                # Float above bar for small bars (higher to avoid runtime label)
                y_pos = height + max_height * 0.06
                va = "bottom"
            else:
                # Center inside bar for large bars
                y_pos = height * 0.5
                va = "center"
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                annotation,
                ha="center",
                va=va,
                fontsize=7,
                bbox=dict(
                    boxstyle="round,pad=0.3",
                    facecolor="lightyellow",
                    alpha=0.9,
                    edgecolor="orange",
                ),
            )

    # Add max_flow annotations inside bars at the bottom if provided
    if max_flows:
        for i, (bar, mf) in enumerate(zip(bars, max_flows)):
            height = bar.get_height()
            if height < small_bar_threshold:
                # Float above bar (stack above n/m annotation)
                y_pos = height + max_height * 0.16
                va = "bottom"
            else:
                # Fixed distance below n/m box (which is at height * 0.5)
                # But ensure it stays inside the bar
                ideal_y = height * 0.5 - max_height * 0.08
                min_y = height * 0.08  # Don't go below 8% of bar height
                y_pos = max(ideal_y, min_y)
                va = "top" if y_pos == ideal_y else "bottom"
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                f"f={mf:,}",
                ha="center",
                va=va,
                fontsize=6,
                color="white",
                fontweight="bold",
                bbox=dict(
                    boxstyle="round,pad=0.2",
                    facecolor="darkgreen",
                    alpha=0.9,
                ),
            )

    plt.tight_layout()
    # Save PNG
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    # Save SVG
    svg_path = output_path.with_suffix(".svg")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()

    print(f"  Saved: {output_path} and {svg_path}")


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
    max_flows=None,
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
        max_flows=max_flows,
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
        max_flows=max_flows,
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
    max_flows = [r.get("max_flow", 0) for r in results]  # Extract max_flow

    # Create output directory for this graph type
    output_dir = Path(plots_dir) / algorithm / graph_type
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate size plots (vertices × edges) with n and m annotations
    products = [v * e for v, e in zip(num_vertices, num_edges)]
    annotations = [f"n={v}\nm={e}" for v, e in zip(num_vertices, num_edges)]

    # Sort by product (include max_flows in sort)
    sorted_by_product = sorted(
        zip(products, mean_times, max_times, annotations, max_flows), key=lambda x: x[0]
    )
    products_sorted = [x[0] for x in sorted_by_product]
    mean_times_by_product = [x[1] for x in sorted_by_product]
    max_times_by_product = [x[2] for x in sorted_by_product]
    annotations_sorted = [x[3] for x in sorted_by_product]
    max_flows_sorted = [x[4] for x in sorted_by_product]

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
        max_flows=max_flows_sorted,
    )

    return 2  # Number of plots generated (mean and max)


def plot_comparison_line_chart(
    x_labels,
    algorithm_data,
    title,
    xlabel,
    ylabel,
    output_path,
    use_log_scale=False,
):
    """Create a line chart comparing multiple algorithms.

    Args:
        x_labels: Labels for x-axis
        algorithm_data: Dictionary mapping algorithm names to value lists
        title: Plot title
        xlabel: X-axis label
        ylabel: Y-axis label
        output_path: Path to save the plot
        use_log_scale: If True, use log scale for y-axis
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    algorithms = list(algorithm_data.keys())
    indices = range(len(x_labels))

    # Create lines for each algorithm
    for i, algorithm in enumerate(algorithms):
        values = algorithm_data[algorithm]
        color = ALGORITHM_COLORS.get(algorithm, f"C{i}")
        label = ALGORITHM_LABELS.get(algorithm, algorithm.replace("_", " ").title())

        # Plot line with markers
        ax.plot(
            indices,
            values,
            label=label,
            color=color,
            linewidth=2.5,
            marker="o",
            markersize=8,
            markerfacecolor="white",
            markeredgewidth=2,
            markeredgecolor=color,
        )

    # Set labels and title
    ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
    if use_log_scale:
        ax.set_ylabel(ylabel + " (log scale)", fontsize=12, fontweight="bold")
        ax.set_yscale("log")
    else:
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Set x-axis ticks
    ax.set_xticks(indices)
    ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=9)

    # Add grid and legend
    ax.grid(axis="both", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=10)

    plt.tight_layout()
    # Save PNG
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    # Save SVG
    svg_path = output_path.with_suffix(".svg")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()

    print(f"  Saved: {output_path} and {svg_path}")


# Colors for ratio comparison pairs
RATIO_COLORS = {
    "FF/SFF": "#e74c3c",  # Red
    "FF/PFP": "#3498db",  # Blue
    "SFF/PFP": "#2ecc71",  # Green
}


def plot_ratio_comparison_chart(
    x_labels,
    mean_data,
    title,
    xlabel,
    output_path,
    use_log_scale=False,
):
    """Create a line chart showing pairwise runtime ratios between algorithms.

    Args:
        x_labels: Labels for x-axis (graph sizes)
        mean_data: Dictionary mapping algorithm names to mean runtime lists
        title: Plot title
        xlabel: X-axis label
        output_path: Path to save the plot
        use_log_scale: If True, use log scale for y-axis
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    indices = range(len(x_labels))
    algorithms = list(mean_data.keys())

    # Define the pairs to compare (numerator/denominator)
    # Ratios > 1 mean denominator is faster
    pairs = [
        ("ford_fulkerson", "scaling_ford_fulkerson", "FF/SFF"),
        ("ford_fulkerson", "preflow_push", "FF/PFP"),
        ("scaling_ford_fulkerson", "preflow_push", "SFF/PFP"),
    ]

    # Plot each pair that has data
    plotted_pairs = 0
    for algo1, algo2, label in pairs:
        if algo1 in mean_data and algo2 in mean_data:
            ratios = []
            for i in range(len(x_labels)):
                val1 = mean_data[algo1][i]
                val2 = mean_data[algo2][i]
                if val2 > 0:
                    ratios.append(val1 / val2)
                else:
                    ratios.append(float("nan"))

            color = RATIO_COLORS.get(label, f"C{plotted_pairs}")

            ax.plot(
                indices,
                ratios,
                label=label,
                color=color,
                linewidth=2.5,
                marker="o",
                markersize=8,
                markerfacecolor="white",
                markeredgewidth=2,
                markeredgecolor=color,
            )
            plotted_pairs += 1

    # Add horizontal reference line at y=1 (equal performance)
    ax.axhline(
        y=1,
        color="gray",
        linestyle="--",
        linewidth=1.5,
        alpha=0.7,
        label="Equal (ratio=1)",
    )

    # Set labels and title
    ax.set_xlabel(xlabel, fontsize=12, fontweight="bold")
    ylabel = "Runtime Ratio"
    if use_log_scale:
        ax.set_ylabel(ylabel + " (log scale)", fontsize=12, fontweight="bold")
        ax.set_yscale("log")
    else:
        ax.set_ylabel(ylabel, fontsize=12, fontweight="bold")
    ax.set_title(title, fontsize=14, fontweight="bold")

    # Set x-axis ticks
    ax.set_xticks(indices)
    ax.set_xticklabels(x_labels, rotation=45, ha="right", fontsize=9)

    # Add grid and legend
    ax.grid(axis="both", alpha=0.3, linestyle="--")
    ax.set_axisbelow(True)
    ax.legend(loc="best", fontsize=10)

    plt.tight_layout()
    # Save PNG
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    # Save SVG
    svg_path = output_path.with_suffix(".svg")
    plt.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close()

    print(f"  Saved: {output_path} and {svg_path}")


def generate_comparison_plots(
    results_dir, plots_dir, graph_types=None, generate_log_plots=False
):
    """Generate comparison plots showing all algorithms side by side for each graph type.

    Args:
        results_dir: Directory containing benchmark results
        plots_dir: Output directory for plots
        graph_types: Comma-separated list of graph types, or None for all
        generate_log_plots: If True, also generate log scale versions
    """
    results_path = Path(results_dir)
    comparison_dir = Path(plots_dir) / "Comparisons"

    # Find all available algorithms
    available_algorithms = [d.name for d in results_path.iterdir() if d.is_dir()]
    if not available_algorithms:
        print("  No algorithms found for comparison")
        return False

    print(f"  Comparing algorithms: {', '.join(available_algorithms)}")

    # Determine graph types to process
    if graph_types:
        requested_types = [t.lower().strip() for t in graph_types.split(",")]
    else:
        # Find all graph types across all algorithms
        all_types = set()
        for algo in available_algorithms:
            algo_dir = results_path / algo
            for d in algo_dir.iterdir():
                if d.is_dir():
                    all_types.add(d.name)
        requested_types = sorted(all_types)

    if not requested_types:
        print("  No graph types found for comparison")
        return False

    total_plots = 0

    for graph_type in requested_types:
        print(f"  Generating comparison for {graph_type}...")

        # Collect data from each algorithm
        all_data = {}
        for algorithm in available_algorithms:
            results = read_results(results_dir, algorithm, graph_type)
            if results:
                all_data[algorithm] = sorted(
                    results, key=lambda x: (x["num_vertices"], x["num_edges"])
                )

        if len(all_data) < 2:
            print(f"    Skipping {graph_type}: need at least 2 algorithms with data")
            continue

        # Find common graph sizes across all algorithms (by vertices × edges)
        size_sets = []
        for algorithm, results in all_data.items():
            sizes = {(r["num_vertices"], r["num_edges"]) for r in results}
            size_sets.append(sizes)

        common_sizes = sorted(set.intersection(*size_sets))
        if not common_sizes:
            print(f"    Skipping {graph_type}: no common graph sizes found")
            continue

        # Create output directory
        output_dir = comparison_dir / graph_type
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build data structures for plotting
        x_labels = [f"n={v}\nm={e}" for v, e in common_sizes]

        # Mean times comparison
        mean_data = {}
        max_data = {}
        for algorithm, results in all_data.items():
            size_to_result = {(r["num_vertices"], r["num_edges"]): r for r in results}
            mean_data[algorithm] = [
                size_to_result[size]["statistics"]["mean"] for size in common_sizes
            ]
            max_data[algorithm] = [
                size_to_result[size]["statistics"]["max"] for size in common_sizes
            ]

        # Generate mean comparison plot (linear scale)
        plot_comparison_line_chart(
            x_labels=x_labels,
            algorithm_data=mean_data,
            title=f"Algorithm Comparison - {graph_type.capitalize()} - Mean Runtime",
            xlabel="Graph Size (n=vertices, m=edges)",
            ylabel="Mean Runtime (seconds)",
            output_path=output_dir / "mean_runtime_comparison.png",
            use_log_scale=False,
        )
        total_plots += 1

        # Generate max comparison plot (linear scale)
        plot_comparison_line_chart(
            x_labels=x_labels,
            algorithm_data=max_data,
            title=f"Algorithm Comparison - {graph_type.capitalize()} - Max Runtime",
            xlabel="Graph Size (n=vertices, m=edges)",
            ylabel="Max Runtime (seconds)",
            output_path=output_dir / "max_runtime_comparison.png",
            use_log_scale=False,
        )
        total_plots += 1

        # Generate log scale plots if requested
        if generate_log_plots:
            plot_comparison_line_chart(
                x_labels=x_labels,
                algorithm_data=mean_data,
                title=f"Algorithm Comparison - {graph_type.capitalize()} - Mean Runtime (Log Scale)",
                xlabel="Graph Size (n=vertices, m=edges)",
                ylabel="Mean Runtime (seconds)",
                output_path=output_dir / "mean_runtime_comparison_log.png",
                use_log_scale=True,
            )
            total_plots += 1

            plot_comparison_line_chart(
                x_labels=x_labels,
                algorithm_data=max_data,
                title=f"Algorithm Comparison - {graph_type.capitalize()} - Max Runtime (Log Scale)",
                xlabel="Graph Size (n=vertices, m=edges)",
                ylabel="Max Runtime (seconds)",
                output_path=output_dir / "max_runtime_comparison_log.png",
                use_log_scale=True,
            )
            total_plots += 1

        # Generate ratio comparison plot (always generate this one)
        plot_ratio_comparison_chart(
            x_labels=x_labels,
            mean_data=mean_data,
            title=f"Algorithm Ratio Comparison - {graph_type.capitalize()}",
            xlabel="Graph Size (n=vertices, m=edges)",
            output_path=output_dir / "ratio_comparison.png",
            use_log_scale=False,
        )
        total_plots += 1

        # Generate log scale ratio plot if requested
        if generate_log_plots:
            plot_ratio_comparison_chart(
                x_labels=x_labels,
                mean_data=mean_data,
                title=f"Algorithm Ratio Comparison - {graph_type.capitalize()} (Log Scale)",
                xlabel="Graph Size (n=vertices, m=edges)",
                output_path=output_dir / "ratio_comparison_log.png",
                use_log_scale=True,
            )
            total_plots += 1

        plots_count = 3 if not generate_log_plots else 6
        print(f"    Generated {plots_count} comparison plots for {graph_type}")

    return total_plots > 0


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
        help="Input directory containing benchmark results (default: BenchmarkResultsData)",
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
        help='Algorithm(s) to plot: comma-separated list (e.g., "ford_fulkerson,scaling_ford_fulkerson,preflow_push") or single algorithm. If not specified, plots all available algorithms.',
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

    parser.add_argument(
        "--no-comparison",
        action="store_true",
        help="Skip generating comparison plots across algorithms",
    )

    parser.add_argument(
        "--comparison-only",
        action="store_true",
        help="Only generate comparison plots (skip individual algorithm plots)",
    )

    parser.add_argument(
        "--log-scale",
        action="store_true",
        help="Also generate log scale versions of comparison plots (saved with _log suffix)",
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
    print(
        f"  Comparison plots: {'skip' if args.no_comparison else ('only' if args.comparison_only else 'yes')}"
    )
    if not args.no_comparison:
        print(f"  Log scale plots: {'yes' if args.log_scale else 'no'}")

    all_success = True

    # Generate individual algorithm plots (unless --comparison-only)
    if not args.comparison_only:
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

    # Generate comparison plots (unless --no-comparison)
    if not args.no_comparison:
        print(f"\n{'='*60}")
        print("Generating Algorithm Comparison Plots")
        print(f"{'='*60}")

        comparison_success = generate_comparison_plots(
            args.results, args.output, args.types, args.log_scale
        )

        if not comparison_success:
            print("\n  Warning: No comparison plots generated")
            all_success = False
        else:
            print("\n✓ Completed comparison plots")

    # Summary
    print(f"\n{'='*60}")
    if all_success:
        print(f"✓ All plot generation complete!")
    else:
        print(f"⚠️  Plot generation complete with some warnings")
    print(f"{'='*60}")

    return 0


if __name__ == "__main__":
    exit(main())
