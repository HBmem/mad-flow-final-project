# Plan

## Upperbound Runtime of Each Algorithm

n = num vertices
m = num edges

FF: O(nC), C = sum of capacities out of s
SFF: O(n*log2(C))
PFP: ?

## Graph Generation

### Bipartite

params:

- source side num nodes
- sink side num nodes
- max probability of edge between sides between 0-1
- min capacity
- max capacity

### FixedDegree

params

- num vertices
- num edges leaving each node
- min capacity
- max capacity

### Mesh

A grid of vertices with connections between each adjacent vertex

n = rows x columns

params

- num rows
- num colums
- max capacity
- const capacity? boolean (else random between 1 and max capacity)

### Random

- num vertices
- density (0-100) (probability of an edge between any two vertices)
- min capacity
- max capacity

### Experiment Methodology and Graph Generation Plan

Our methodology follows a two-phase approach:

#### Phase 1 (Primary): Size Scaling Analysis

- Vary only the number of vertices/edges for each graph type
- Keep capacity ranges, probabilities, and other parameters constant
- This isolates the effect of input size on algorithm performance
- Enables direct comparison of theoretical O() bounds to empirical results

#### Phase 2 (Optional/Future Work): Parameter Sensitivity

- For selected graph sizes, vary secondary parameters (density, edge probability, etc.)
- This reveals how graph structure (beyond size) affects performance

---

## Phase 1: Graph Generation Specifications

### Fixed Parameters (Constant Across All Size Variants)

| Graph Type   | Fixed Parameters                                    |
|--------------|-----------------------------------------------------|
| Bipartite    | probability=0.5, min_cap=1, max_cap=10              |
| FixedDegree  | edges_per_node=5, min_cap=1, max_cap=10             |
| Mesh         | capacity=5, **constant_capacity=true**              |
| Random       | density=30, min_cap=1, max_cap=10                   |

### Bipartite Graphs (10 graphs)

| Graph # | Source Nodes | Sink Nodes | Total Vertices | Est. Edges |
|---------|--------------|------------|----------------|------------|
| 1       | 5            | 5          | 12             | ~22        |
| 2       | 10           | 10         | 22             | ~70        |
| 3       | 20           | 20         | 42             | ~220       |
| 4       | 30           | 30         | 62             | ~480       |
| 5       | 40           | 40         | 82             | ~840       |
| 6       | 50           | 50         | 102            | ~1,300     |
| 7       | 75           | 75         | 152            | ~2,900     |
| 8       | 100          | 100        | 202            | ~5,100     |
| 9       | 125          | 125        | 252            | ~7,900     |
| 10      | 150          | 150        | 302            | ~11,400    |

File naming: `{src}s-{sink}t-05p-1min-10max.txt`
Example: `10s-10t-05p-1min-10max.txt`

### FixedDegree Graphs (10 graphs)

| Graph # | Vertices | Edges/Node | Total Edges |
|---------|----------|------------|-------------|
| 1       | 15       | 5          | ~95         |
| 2       | 25       | 5          | ~145        |
| 3       | 50       | 5          | ~270        |
| 4       | 100      | 5          | ~520        |
| 5       | 150      | 5          | ~770        |
| 6       | 200      | 5          | ~1,020      |
| 7       | 300      | 5          | ~1,520      |
| 8       | 400      | 5          | ~2,020      |
| 9       | 500      | 5          | ~2,520      |
| 10      | 750      | 5          | ~3,770      |

File naming: `{v}v-5out-1min-10max.txt`
Example: `100v-5out-1min-10max.txt`

### Mesh Graphs (10 graphs)

| Graph # | Rows | Cols | Total Vertices | Est. Edges |
|---------|------|------|----------------|------------|
| 1       | 5    | 5    | 27             | ~60        |
| 2       | 8    | 8    | 66             | ~170       |
| 3       | 10   | 10   | 102            | ~270       |
| 4       | 15   | 15   | 227            | ~630       |
| 5       | 20   | 20   | 402            | ~1,140     |
| 6       | 25   | 25   | 627            | ~1,800     |
| 7       | 30   | 30   | 902            | ~2,610     |
| 8       | 35   | 35   | 1,227          | ~3,570     |
| 9       | 40   | 40   | 1,602          | ~4,680     |
| 10      | 50   | 50   | 2,502          | ~7,350     |

File naming: `{r}r-{c}c-5cap-const.txt`
Example: `10r-10c-5cap-const.txt`

### Random Graphs (10 graphs)

| Graph # | Vertices | Density | Est. Edges |
|---------|----------|---------|------------|
| 1       | 15       | 30      | ~35        |
| 2       | 25       | 30      | ~95        |
| 3       | 50       | 30      | ~370       |
| 4       | 75       | 30      | ~840       |
| 5       | 100      | 30      | ~1,500     |
| 6       | 150      | 30      | ~3,400     |
| 7       | 200      | 30      | ~6,000     |
| 8       | 250      | 30      | ~9,400     |
| 9       | 300      | 30      | ~13,500    |
| 10      | 400      | 30      | ~24,000    |

File naming: `{v}v-30d-1min-10max.txt`
Example: `100v-30d-1min-10max.txt`

---

## Summary Statistics

| Graph Type   | Graphs | Vertex Range | Edge Range      |
|--------------|--------|--------------|-----------------|
| Bipartite    | 10     | 12 - 302     | ~22 - ~11,400   |
| FixedDegree  | 10     | 15 - 750     | ~95 - ~3,770    |
| Mesh         | 10     | 27 - 2,502   | ~60 - ~7,350    |
| Random       | 10     | 15 - 400     | ~35 - ~24,000   |
| **Total**    | **40** |              |                 |

## Estimated Benchmark Runtime

- **Total graphs:** 40 (10 per type × 4 types)
- **Runs per graph:** 10 runs × 3 algorithms = 30 executions per graph
- **Small graphs (vertices < 200):** ~0.1s per run → negligible
- **Medium graphs (200-500 vertices):** ~0.5-2s per run
- **Largest graphs:** ~5-20s per run (worst case)

**Conservative estimate:** 2-3 hours total benchmark time

---

## Graph Generation Commands

### Bipartite Commands

```bash
cd graphGenerationCode/Bipartite

# Interactive: java BipartiteGraph

# Enter: source_nodes, sink_nodes, 0.5 (probability), 1 (min), 10 (max), filename
```

### FixedDegree Commands

```bash
cd graphGenerationCode/FixedDegree
java RandomGraph <vertices> <edges_per_node> <min_cap> <max_cap> <filename>

# Example: java RandomGraph 100 5 1 10 100v-5out-1min-10max.txt
```

### Mesh Commands

```bash
cd graphGenerationCode/Mesh
java MeshGenerator <rows> <cols> <capacity> <filename> -cc

# Example: java MeshGenerator 10 10 5 10r-10c-5cap-const.txt -cc

# Note: -cc flag enables constant capacity
```

### Random Commands

```bash
cd graphGenerationCode/Random

# Interactive: java BuildGraph

# Enter: directory, vertices, density, min_cap, max_cap, filename
```

---

## Benchmarking Configuration

### Number of Runs

- **Runs per graph:** 10
- This provides sufficient data for reliable statistics while keeping total runtime manageable
- Total executions: 40 graphs × 10 runs × 3 algorithms = **1,200 runs**

### Benchmark Command

python3 benchmark.py \
  -i graphs \
  -o BenchmarkResultsData \
  -r 10 \
  -s s \
  --sink t \
  --clean

### Estimated Total Runtime

- Small/medium graphs (30 of 40): ~0.1-1s per run → ~15 min
- Large graphs (10 of 40): ~5-20s per run → ~50 min
- **Total estimate: 1.5-2.5 hours** (varies by machine)

---

## Analysis Plan

### Primary Statistics to Report

| Statistic | Purpose | Use in Report |
|-----------|---------|---------------|
| **Mean runtime** | Expected/typical performance | Primary comparison metric |
| **Max runtime** | Worst-case behavior | Complexity analysis |
| Std deviation | Algorithm consistency | Note variance patterns |
| Min runtime | Best-case (less useful) | Optional/footnote |

### Plots to Generate

For each of the 4 graph types, generate:

1. **Mean Runtime vs. Number of Vertices**
   - X-axis: Number of vertices (log or linear scale)
   - Y-axis: Mean runtime (seconds)
   - Series: One line per algorithm (FF, SFF, PFP)
   - Purpose: Compare average performance scaling

2. **Max Runtime vs. Number of Vertices**
   - X-axis: Number of vertices (log or linear scale)
   - Y-axis: Max runtime (seconds)
   - Series: One line per algorithm
   - Purpose: Compare worst-case performance scaling

**Total plots: 8 plots** (2 per graph type × 4 graph types)

### Optional Additional Plots

- **Combined comparison plots**: All graph types on one plot for each algorithm
- **Speedup plots**: SFF/FF ratio or PFP/FF ratio to show relative improvement
- **Log-log plots**: To visually identify polynomial complexity (slope = exponent)

### Plot File Organization

```
BenchmarkResultsPlots/
├── bipartite/
│   ├── mean_runtime.png
│   └── max_runtime.png
├── fixeddegree/
│   ├── mean_runtime.png
│   └── max_runtime.png
├── mesh/
│   ├── mean_runtime.png
│   └── max_runtime.png
└── random/
    ├── mean_runtime.png
    └── max_runtime.png
```

---

## Report Integration

### Key Questions to Answer with Data

1. **How does each algorithm scale with input size?**
   - Do observed runtimes match theoretical O() bounds?
   - Which algorithm shows best scaling behavior?

2. **Which algorithm performs best for each graph type?**
   - Are there graph structures where one algorithm dominates?
   - Does relative performance change with graph size?

3. **How does graph structure affect performance?**
   - Compare same-sized graphs across different types
   - Which graph type is "hardest" for each algorithm?

### Suggested Report Figures

1. One combined figure per graph type showing mean runtime for all 3 algorithms
2. Summary table with speedup ratios (e.g., "SFF is 2.5x faster than FF on large random graphs")
3. Optional: Log-log plot to estimate empirical complexity exponent

---

## Report

### Sections

- Introduction
- Methodology
- Results
- Future Work
- Division of Labor
- Lessons Learned
- References
