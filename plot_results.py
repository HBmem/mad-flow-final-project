#!/usr/bin/env python3
import argparse
import json
import os
import shutil
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend


def read_results(results_dir, algorithm, graph_type):
    """Read benchmark results from JSON file."""
    json_path = Path(results_dir) / algorithm / graph_type / 'results.json'

    if not json_path.exists():
        return None

    with open(json_path, 'r') as f:
        data = json.load(f)

    return data.get('results', [])


def plot_bar_chart(data, x_values, y_values, labels, title, xlabel, ylabel, output_path, annotations=None):
    """Create a bar chart and save to file."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create bars
    bars = ax.bar(range(len(x_values)), y_values, color='steelblue', alpha=0.8)

    # Set labels
    ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')

    # Set x-axis ticks and labels
    ax.set_xticks(range(len(x_values)))
    ax.set_xticklabels(labels, rotation=45, ha='right')

    # Add grid for better readability
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # Add value labels on top of bars
    for i, (bar, value) in enumerate(zip(bars, y_values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.4f}s',
                ha='center', va='bottom', fontsize=8)

    # Add annotations if provided (for n×m plots)
    if annotations:
        for i, (bar, annotation) in enumerate(zip(bars, annotations)):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() * 0.5,
                    annotation,
                    ha='center', va='center', fontsize=7,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Saved: {output_path}")


def generate_plots(results_dir, plots_dir, algorithm, graph_types):
    """Generate all plots for specified graph types."""
    results_path = Path(results_dir)
    plots_path = Path(plots_dir)

    # Determine which graph types to process
    if graph_types:
        requested_types = [t.lower().strip() for t in graph_types.split(',')]
    else:
        # Find all available graph types
        algorithm_dir = results_path / algorithm
        if not algorithm_dir.exists():
            print(f"Error: No results found for algorithm '{algorithm}'")
            return

        requested_types = [d.name for d in algorithm_dir.iterdir() if d.is_dir()]

    # Process each graph type
    for graph_type in requested_types:
        print(f"\nGenerating plots for {graph_type}...")

        # Read results
        results = read_results(results_dir, algorithm, graph_type)

        if not results:
            print(f"  No results found for {graph_type}")
            continue

        # Sort results by number of vertices for consistent ordering
        results = sorted(results, key=lambda x: (x['num_vertices'], x['num_edges']))

        # Extract data
        graph_names = [r['graph_file'] for r in results]
        num_vertices = [r['num_vertices'] for r in results]
        num_edges = [r['num_edges'] for r in results]
        mean_times = [r['statistics']['mean'] for r in results]
        max_times = [r['statistics']['max'] for r in results]

        # Create output directory for this graph type
        output_dir = plots_path / algorithm / graph_type
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate 6 plots

        # 1. Mean time vs vertices
        plot_bar_chart(
            data=results,
            x_values=num_vertices,
            y_values=mean_times,
            labels=[str(v) for v in num_vertices],
            title=f'{graph_type.capitalize()} - Mean Runtime vs Number of Vertices',
            xlabel='Number of Vertices',
            ylabel='Mean Runtime (seconds)',
            output_path=output_dir / 'mean_vertices_vs_time.png'
        )

        # 2. Mean time vs edges
        # Sort by edges for this plot
        sorted_by_edges = sorted(zip(num_edges, mean_times, graph_names), key=lambda x: x[0])
        edges_sorted = [x[0] for x in sorted_by_edges]
        mean_times_by_edges = [x[1] for x in sorted_by_edges]

        plot_bar_chart(
            data=results,
            x_values=edges_sorted,
            y_values=mean_times_by_edges,
            labels=[str(e) for e in edges_sorted],
            title=f'{graph_type.capitalize()} - Mean Runtime vs Number of Edges',
            xlabel='Number of Edges',
            ylabel='Mean Runtime (seconds)',
            output_path=output_dir / 'mean_edges_vs_time.png'
        )

        # 3. Mean time vs (vertices × edges)
        products = [v * e for v, e in zip(num_vertices, num_edges)]
        annotations = [f'n={v}\nm={e}' for v, e in zip(num_vertices, num_edges)]

        # Sort by product
        sorted_by_product = sorted(zip(products, mean_times, annotations, num_vertices, num_edges),
                                   key=lambda x: x[0])
        products_sorted = [x[0] for x in sorted_by_product]
        mean_times_by_product = [x[1] for x in sorted_by_product]
        annotations_sorted = [x[2] for x in sorted_by_product]

        plot_bar_chart(
            data=results,
            x_values=products_sorted,
            y_values=mean_times_by_product,
            labels=[str(p) for p in products_sorted],
            title=f'{graph_type.capitalize()} - Mean Runtime vs Input Size (n×m)',
            xlabel='Input Size (vertices × edges)',
            ylabel='Mean Runtime (seconds)',
            output_path=output_dir / 'mean_size_vs_time.png',
            annotations=annotations_sorted
        )

        # 4. Max time vs vertices
        plot_bar_chart(
            data=results,
            x_values=num_vertices,
            y_values=max_times,
            labels=[str(v) for v in num_vertices],
            title=f'{graph_type.capitalize()} - Max Runtime vs Number of Vertices',
            xlabel='Number of Vertices',
            ylabel='Max Runtime (seconds)',
            output_path=output_dir / 'max_vertices_vs_time.png'
        )

        # 5. Max time vs edges
        sorted_by_edges_max = sorted(zip(num_edges, max_times, graph_names), key=lambda x: x[0])
        edges_sorted_max = [x[0] for x in sorted_by_edges_max]
        max_times_by_edges = [x[1] for x in sorted_by_edges_max]

        plot_bar_chart(
            data=results,
            x_values=edges_sorted_max,
            y_values=max_times_by_edges,
            labels=[str(e) for e in edges_sorted_max],
            title=f'{graph_type.capitalize()} - Max Runtime vs Number of Edges',
            xlabel='Number of Edges',
            ylabel='Max Runtime (seconds)',
            output_path=output_dir / 'max_edges_vs_time.png'
        )

        # 6. Max time vs (vertices × edges)
        sorted_by_product_max = sorted(zip(products, max_times, annotations, num_vertices, num_edges),
                                       key=lambda x: x[0])
        products_sorted_max = [x[0] for x in sorted_by_product_max]
        max_times_by_product = [x[1] for x in sorted_by_product_max]
        annotations_sorted_max = [x[2] for x in sorted_by_product_max]

        plot_bar_chart(
            data=results,
            x_values=products_sorted_max,
            y_values=max_times_by_product,
            labels=[str(p) for p in products_sorted_max],
            title=f'{graph_type.capitalize()} - Max Runtime vs Input Size (n×m)',
            xlabel='Input Size (vertices × edges)',
            ylabel='Max Runtime (seconds)',
            output_path=output_dir / 'max_size_vs_time.png',
            annotations=annotations_sorted_max
        )

        print(f"  Generated 6 plots for {graph_type}")


def main():
    parser = argparse.ArgumentParser(
        description='Generate plots from benchmark results'
    )

    parser.add_argument(
        '-r', '--results',
        type=str,
        default='BenchmarkResultsData',
        help='Directory containing benchmark results (default: BenchmarkResultsData)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default='BenchmarkResultsPlots',
        help='Output directory for plots (default: BenchmarkResultsPlots)'
    )

    parser.add_argument(
        '-a', '--algorithm',
        type=str,
        choices=['ford_fulkerson', 'scaling_ford_fulkerson', 'preflow_push'],
        default='ford_fulkerson',
        help='Algorithm to plot results for (default: ford_fulkerson)'
    )

    parser.add_argument(
        '-t', '--types',
        type=str,
        default=None,
        help='Comma-separated list of graph types to plot (e.g., "bipartite,mesh")'
    )

    parser.add_argument(
        '--clean',
        action='store_true',
        help='Remove output directory before starting (if it exists)'
    )

    args = parser.parse_args()

    # Validate paths
    if not os.path.exists(args.results):
        print(f"Error: Results directory '{args.results}' does not exist")
        return 1

    # Handle output directory
    if os.path.exists(args.output):
        if args.clean:
            print(f"Cleaning output directory: {args.output}")
            shutil.rmtree(args.output)
            print(f"  Removed existing directory")
        else:
            print(f"Error: Output directory '{args.output}' already exists")
            print(f"Use --clean flag to remove it, or specify a different output directory")
            return 1

    print(f"Plot Generation Configuration:")
    print(f"  Results directory: {args.results}")
    print(f"  Output directory: {args.output}")
    print(f"  Algorithm: {args.algorithm}")
    print(f"  Graph types: {args.types if args.types else 'all'}")

    # Generate plots
    generate_plots(args.results, args.output, args.algorithm, args.types)

    print("\nPlot generation complete!")
    return 0


if __name__ == '__main__':
    exit(main())

