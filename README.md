# Max Flow Algorithm Analysis

A complete toolkit for computing, benchmarking, and visualizing max flow algorithms on various graph types.

## Quick Start

```bash
# Run max flow on a single graph
python3 mad-flow.py -g graphGenerationCode/Mesh/smallMesh.txt

# Benchmark across all graph types (outputs to BenchmarkResultsData/)
python3 benchmark.py -i graphGenerationCode -r 10

# Generate visualization plots (outputs to BenchmarkResultsPlots/)
python3 plot_results.py
```

## Tools

### mad-flow.py - Max Flow Calculator

Computes maximum flow using the Ford-Fulkerson algorithm.

```bash
python3 mad-flow.py -g <graph_file> [options]

Options:
  -g, --graph    Path to graph file (required)
  -s, --source   Source node (default: 's')
  -t, --sink     Sink node (default: 't')
  --json         Output in JSON format for scripting
```

**Examples:**

```bash
# Human-readable output
python3 mad-flow.py -g graph.txt
# Output: The maximum possible flow is: 150

# Machine-readable JSON
python3 mad-flow.py -g graph.txt --json
# Output: {"max_flow": 150, "source": "s", "sink": "t", ...}
```

### benchmark.py - Performance Benchmarking

Runs max flow algorithms multiple times and collects timing statistics.

```bash
python3 benchmark.py -i <input_dir> [options]

Options:
  -i, --input       Input directory with graph subdirectories (required)
  -o, --output      Output directory for results (default: BenchmarkResultsData)
  -a, --algorithm   Algorithm: ford_fulkerson, scaling_ford_fulkerson, preflow_push (default: ford_fulkerson)
  -t, --types       Graph types to test: bipartite,mesh,random,fixeddegree (default: all)
  -r, --runs        Number of runs per graph (default: 10)
  -p, --processes   Number of parallel processes (default: CPU count)
  -s, --source      Source node (default: 's')
  --sink            Sink node (default: 't')
  --clean           Remove output directory before starting (safeguard against accidental overwrites)
```

**Output:** Results organized as `BenchmarkResultsData/algorithm/graph_type/results.{json,csv}` with statistics: min, max, mean, median, stddev.

**Performance:** Uses multiprocessing to benchmark graphs in parallel. Automatically detects CPU count but can be customized with `-p` flag.

**Examples:**
```bash
# Use all available CPU cores (default)
python3 benchmark.py -i graphGenerationCode -r 10

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
  -a, --algorithm  Algorithm to plot (default: ford_fulkerson)
  -t, --types      Graph types to plot (default: all)
  --clean          Remove output directory before starting (safeguard against accidental overwrites)
```

**Output:** 6 plots per graph type (mean/max × vertices/edges/size) as PNG files in `BenchmarkResultsPlots/`.

**Note:** If output directory exists, you must use `--clean` or specify a different output directory to prevent accidental data loss.

## Complete Workflow

```bash
# Step 1: Run benchmarks (10 runs per graph)
python3 benchmark.py -i graphGenerationCode -r 10

# Step 2: Generate plots
python3 plot_results.py

# Step 3: View results
# - Data: BenchmarkResultsData/ford_fulkerson/<graph_type>/results.{json,csv}
# - Plots: BenchmarkResultsPlots/ford_fulkerson/<graph_type>/*.png

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

- Python 3.x
- matplotlib: `pip3 install matplotlib` (for plotting only)

## Architecture

The system is built on the `Graph` class which tracks vertices/edges efficiently using cached counters (O(1) lookups). The `mad-flow.py` script supports JSON output mode for robust machine parsing by the benchmark script.

**Performance:** The benchmark script uses Python's `multiprocessing` module to analyze multiple graphs in parallel, automatically utilizing all available CPU cores for faster execution on multicore systems.

**Graph types supported:** Bipartite, Mesh, Random, FixedDegree

**Algorithms:** Currently Ford-Fulkerson (extensible to Scaling Ford-Fulkerson and Preflow-Push)
