# Max Flow Algorithm Analysis

A complete toolkit for computing, benchmarking, and visualizing max flow algorithms on various graph types.

## Quick Start

```bash
# Run max flow on a single graph (default: Ford-Fulkerson)
python3 mad-flow.py -g graphGenerationCode/Mesh/smallMesh.txt

# Run with Scaling Ford-Fulkerson algorithm
python3 mad-flow.py -g graphGenerationCode/Mesh/smallMesh.txt -a scaling_ford_fulkerson

# Benchmark all algorithms (auto-detects and runs both, outputs to BenchmarkResultsData/)
python3 benchmark.py -i graphGenerationCode -r 10

# Generate visualization plots for all algorithms (outputs to BenchmarkResultsPlots/)
python3 plot_results.py
```

## Tools

### mad-flow.py - Max Flow Calculator

Computes maximum flow using various algorithms (Ford-Fulkerson, Scaling Ford-Fulkerson).

```bash
python3 mad-flow.py -g <graph_file> [options]

Options:
  -g, --graph      Path to graph file (required)
  -s, --source     Source node (default: 's')
  -t, --sink       Sink node (default: 't')
  -a, --algorithm  Algorithm: ford_fulkerson, scaling_ford_fulkerson (default: ford_fulkerson)
  --json           Output in JSON format for scripting
```

**Examples:**

```bash
# Human-readable output with default Ford-Fulkerson
python3 mad-flow.py -g graph.txt
# Output: The maximum possible flow is: 150

# Using Scaling Ford-Fulkerson algorithm
python3 mad-flow.py -g graph.txt -a scaling_ford_fulkerson

# Machine-readable JSON
python3 mad-flow.py -g graph.txt -a scaling_ford_fulkerson --json
# Output: {"max_flow": 150, "algorithm": "scaling_ford_fulkerson", "source": "s", "sink": "t", ...}
```

### benchmark.py - Performance Benchmarking

Runs max flow algorithms multiple times and collects timing statistics.

```bash
python3 benchmark.py -i <input_dir> [options]

Options:
  -i, --input       Input directory with graph subdirectories (required)
  -o, --output      Output directory for results (default: BenchmarkResultsData)
  -a, --algorithm   Algorithm(s): single or comma-separated list, e.g., "ford_fulkerson" or
                    "ford_fulkerson,scaling_ford_fulkerson"
                    If not specified, automatically benchmarks all implemented algorithms
  -t, --types       Graph types to test: bipartite,mesh,random,fixeddegree (default: all)
  -r, --runs        Number of runs per graph (default: 10)
  -p, --processes   Number of parallel processes (default: CPU count)
  -s, --source      Source node (default: 's')
  --sink            Sink node (default: 't')
  --clean           Remove output directory before starting (safeguard against accidental overwrites)
```

**Output:** Results organized as `BenchmarkResultsData/algorithm/graph_type/results.{json,csv}` with statistics: min, max, mean, median, stddev.

**Auto-Detection:** If no algorithm is specified, `benchmark.py` automatically benchmarks all implemented algorithms (Ford-Fulkerson and Scaling Ford-Fulkerson).

**Performance:** Uses multiprocessing to benchmark graphs in parallel. Automatically detects CPU count but can be customized with `-p` flag.

**Examples:**
```bash
# Auto-benchmark all algorithms (recommended - benchmarks both algorithms)
python3 benchmark.py -i graphGenerationCode -r 10

# Benchmark specific algorithm only
python3 benchmark.py -i graphGenerationCode -r 10 -a ford_fulkerson
python3 benchmark.py -i graphGenerationCode -r 10 -a scaling_ford_fulkerson

# Explicitly specify multiple algorithms
python3 benchmark.py -i graphGenerationCode -r 10 -a ford_fulkerson,scaling_ford_fulkerson

# Limit to 4 parallel processes
python3 benchmark.py -i graphGenerationCode -r 10 -p 4

# Single-threaded for comparison
python3 benchmark.py -i graphGenerationCode -r 10 -p 1
```

**Note:** If output directory exists, you must use `--clean` or specify a different output directory to prevent accidental data loss.

### plot_results.py - Visualization

Generates plots showing runtime vs input size relationships.

```bash
python3 plot_results.py [options]

Options:
  -r, --results    Directory with benchmark results (default: BenchmarkResultsData)
  -o, --output     Output directory for plots (default: BenchmarkResultsPlots)
  -a, --algorithm  Algorithm(s) to plot: comma-separated list or single algorithm
                   If not specified, automatically plots all available algorithms
  -t, --types      Graph types to plot (default: all)
  --clean          Remove output directory before starting (safeguard against accidental overwrites)
```

**Output:** 2 plots per graph type (`mean_runtime.png` and `max_runtime.png`) in `BenchmarkResultsPlots/<algorithm>/<graph_type>/`. Each plot shows input size (n×m) on the x-axis with annotations indicating the number of vertices (n) and edges (m).

**Auto-Detection:** If no algorithm is specified, `plot_results.py` automatically detects and plots all algorithms found in the results directory.

**Examples:**
```bash
# Plot all algorithms automatically (recommended after multi-algorithm benchmark)
python3 plot_results.py

# Plot specific algorithm
python3 plot_results.py -a ford_fulkerson

# Plot multiple specific algorithms
python3 plot_results.py -a ford_fulkerson,scaling_ford_fulkerson

# Plot only mesh graphs for all algorithms
python3 plot_results.py -t mesh
```

**Note:** If output directory exists, you must use `--clean` or specify a different output directory to prevent accidental data loss.

## Complete Workflow

```bash
# Step 1: Run benchmarks for all algorithms (auto-detects both, 10 runs per graph)
python3 benchmark.py -i graphGenerationCode -r 10

# Step 2: Generate plots for all algorithms (auto-detects both)
python3 plot_results.py

# Step 3: View results
# - Data: BenchmarkResultsData/<algorithm>/<graph_type>/results.{json,csv}
# - Plots: BenchmarkResultsPlots/<algorithm>/<graph_type>/{mean_runtime.png,max_runtime.png}

# Alternative: Run specific algorithms
# Ford-Fulkerson only
python3 benchmark.py -i graphGenerationCode -r 10 -a ford_fulkerson

# Scaling Ford-Fulkerson only
python3 benchmark.py -i graphGenerationCode -r 10 -a scaling_ford_fulkerson

# Explicit multi-algorithm
python3 benchmark.py -i graphGenerationCode -r 10 -a ford_fulkerson,scaling_ford_fulkerson

# Plot specific algorithms:
python3 plot_results.py -a ford_fulkerson
python3 plot_results.py -a scaling_ford_fulkerson

# To re-run and replace existing results, use --clean:
python3 benchmark.py -i graphGenerationCode -r 10 --clean
python3 plot_results.py --clean
```

## Graph File Format

One edge per line: `source_node destination_node capacity`

```text
s a 10
a b 5
b t 15
```

## Requirements

- Python 3.x (either `python3` or `python` command)
- matplotlib: `pip3 install matplotlib` (for plotting only)

**Note:** The `benchmark.py` script automatically detects whether to use `python3` or `python` command based on system availability.

## Architecture

The system is built on the `Graph` class which tracks vertices/edges efficiently using cached counters (O(1) lookups). The `mad-flow.py` script is a unified driver that supports multiple max flow algorithms and provides JSON output mode for robust machine parsing by the benchmark script.

**Performance:** The benchmark script uses Python's `multiprocessing` module to analyze multiple graphs in parallel, automatically utilizing all available CPU cores for faster execution on multicore systems.

**Graph types supported:** Bipartite, Mesh, Random, FixedDegree

**Algorithms implemented:**
- Ford-Fulkerson (standard augmenting path algorithm)
- Scaling Ford-Fulkerson (capacity scaling variant for improved performance)
- Preflow-Push (placeholder for future implementation)
