# Max Flow Algorithm Analysis

A complete toolkit for generating graphs, computing max flow, benchmarking algorithms, and visualizing results.

## Quick Start

```bash
# Generate test graphs
python3 generate_graphs.py -n 5              # First 5 sizes of each type

# Run max flow on a single graph
python3 mad-flow.py -g GeneratedGraphs/Mesh/20r-20c-1000cap-const.txt

# Benchmark all algorithms
python3 benchmark.py -i GeneratedGraphs -r 10 --clean

# Generate plots with algorithm comparisons
python3 plot_results.py --clean --log-scale
```

## Tools

### generate_graphs.py - Graph Generator

Generates test graphs for benchmarking. Supports Phase 1 (size scaling) and Phase 2 (parameter variation) experiments.

```bash
python3 generate_graphs.py [options]

Options:
  -n, --num         Number of graphs per type (1-10, default: all 10)
  -o, --output      Output directory (default: GeneratedGraphs)
  --types           Graph types: bipartite,fixeddegree,mesh,random (default: all)
```

**Per-type parameters** (override defaults for Phase 2 experiments):
- Bipartite: `--bipartite-probability`, `--bipartite-sizes`, `--bipartite-min-cap`, `--bipartite-max-cap`
- FixedDegree: `--fixeddegree-edges`, `--fixeddegree-sizes`, `--fixeddegree-min-cap`, `--fixeddegree-max-cap`
- Mesh: `--mesh-capacity`, `--mesh-constant`/`--mesh-random`, `--mesh-sizes`
- Random: `--random-density`, `--random-sizes`, `--random-min-cap`, `--random-max-cap`

**Examples:**
```bash
# Phase 1: Generate all default graphs
python3 generate_graphs.py

# Phase 2: Vary density on random graphs
python3 generate_graphs.py -o GeneratedGraphs2 --types random --random-density 10
```

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

Generates plots showing runtime vs input size relationships, including algorithm comparison charts.

```bash
python3 plot_results.py [options]

Options:
  -r, --results       Directory with benchmark results (default: BenchmarkResultsData)
  -o, --output        Output directory for plots (default: BenchmarkResultsPlots)
  -a, --algorithm     Algorithm(s) to plot (default: all available)
  -t, --types         Graph types to plot (default: all)
  --clean             Remove output directory before starting
  --no-comparison     Skip algorithm comparison plots
  --comparison-only   Only generate comparison plots
  --log-scale         Also generate log scale comparison plots (saved with _log suffix)
```

**Output:**
- Per-algorithm: `BenchmarkResultsPlots/<algorithm>/<graph_type>/{mean,max}_runtime.png`
- Comparisons: `BenchmarkResultsPlots/Comparisons/<graph_type>/{mean,max}_runtime_comparison.png`

**Examples:**
```bash
# Generate all plots including comparisons
python3 plot_results.py --clean

# Generate with log scale versions
python3 plot_results.py --clean --log-scale

# Only comparison plots
python3 plot_results.py --clean --comparison-only
```

## Complete Workflow

```bash
# Step 1: Generate graphs
python3 generate_graphs.py

# Step 2: Run benchmarks for all algorithms
python3 benchmark.py -i GeneratedGraphs -r 10 --clean

# Step 3: Generate plots with comparisons
python3 plot_results.py --clean --log-scale

# Step 4: View results
# - Data: BenchmarkResultsData/<algorithm>/<graph_type>/results.{json,csv}
# - Plots: BenchmarkResultsPlots/<algorithm>/<graph_type>/
# - Comparisons: BenchmarkResultsPlots/Comparisons/<graph_type>/
```

**Phase 2 experiments** (varying parameters):
```bash
python3 generate_graphs.py -o GeneratedGraphs2 --types random --random-density 10
python3 benchmark.py -i GeneratedGraphs2 -o BenchmarkResultsData2 --clean
python3 plot_results.py -r BenchmarkResultsData2 -o BenchmarkResultsPlots2 --clean
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
- Preflow-Push (push-relabel algorithm)
