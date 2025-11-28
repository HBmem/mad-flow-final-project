# Plan

## Upperbound Runtime of Each Algorithm

n = num vertices
m = num edges

FF: O(mC), C = sum of capacities out of s
Reference: Book theorem 7.5

SFF: O(m^2*log2(C))
Reference: Book theorem 7.20

PFP: Generic O(n^2*m), Max Height Selection Variant: O(n^3)
Refence: Book theorem 7.33

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
| Bipartite    | probability=0.5, min_cap=1, max_cap=1000            |
| FixedDegree  | **edges_per_node=30**, min_cap=1, max_cap=1000      |
| Mesh         | **capacity=1000**, constant_capacity=true           |
| Random       | **density=30**, min_cap=1, max_cap=1000             |

> **Note on capacities:** Using high capacities (1-1000) to increase max_flow values.
> Ford-Fulkerson is O(V×E×max_flow), so high max_flow is essential for meaningful runtimes.
>
> **Note on FixedDegree:** Using **30 edges per node** to create many flow paths
> from source to sink. With fewer edges, max_flow stays too low regardless of capacity.
>
> **Note on Random density:** Using **density=30** (30% of possible edges) for
> strong connectivity and high max_flow values.
>
> **Target runtime:** ~5 minutes for largest Ford-Fulkerson runs.

### Bipartite Graphs (10 graphs)

| Graph # | Source Nodes | Sink Nodes | Total Vertices | Est. Edges |
|---------|--------------|------------|----------------|------------|
| 1       | 50           | 50         | 102            | ~1,350     |
| 2       | 100          | 100        | 202            | ~5,200     |
| 3       | 200          | 200        | 402            | ~20,400    |
| 4       | 300          | 300        | 602            | ~45,000    |
| 5       | 400          | 400        | 802            | ~80,000    |
| 6       | 500          | 500        | 1,002          | ~125,000   |
| 7       | 600          | 600        | 1,202          | ~180,000   |
| 8       | 800          | 800        | 1,602          | ~320,000   |
| 9       | 1000         | 1000       | 2,002          | ~500,000   |
| 10      | 1200         | 1200       | 2,402          | ~720,000   |

File naming: `{src}s-{sink}t-05p-1min-1000max.txt`
Example: `1000s-1000t-05p-1min-1000max.txt`

### FixedDegree Graphs (10 graphs)

| Graph # | Vertices | Edges/Node | Total Edges |
|---------|----------|------------|-------------|
| 1       | 100      | 30         | ~3,000      |
| 2       | 250      | 30         | ~7,500      |
| 3       | 500      | 30         | ~15,000     |
| 4       | 1000     | 30         | ~30,000     |
| 5       | 1500     | 30         | ~45,000     |
| 6       | 2000     | 30         | ~60,000     |
| 7       | 2500     | 30         | ~75,000     |
| 8       | 3000     | 30         | ~90,000     |
| 9       | 3500     | 30         | ~105,000    |
| 10      | 4000     | 30         | ~120,000    |

File naming: `{v}v-30out-1min-1000max.txt`
Example: `1000v-30out-1min-1000max.txt`

### Mesh Graphs (10 graphs)

| Graph # | Rows | Cols | Total Vertices | Est. Edges |
|---------|------|------|----------------|------------|
| 1       | 20   | 20   | 402            | ~1,140     |
| 2       | 40   | 40   | 1,602          | ~4,680     |
| 3       | 60   | 60   | 3,602          | ~10,620    |
| 4       | 80   | 80   | 6,402          | ~19,040    |
| 5       | 100  | 100  | 10,002         | ~29,700    |
| 6       | 125  | 125  | 15,627         | ~46,500    |
| 7       | 150  | 150  | 22,502         | ~67,050    |
| 8       | 200  | 200  | 40,002         | ~119,400   |
| 9       | 250  | 250  | 62,502         | ~186,750   |
| 10      | 300  | 300  | 90,002         | ~269,100   |

File naming: `{r}r-{c}c-1000cap-const.txt`
Example: `100r-100c-1000cap-const.txt`

### Random Graphs (10 graphs)

| Graph # | Vertices | Density | Est. Edges  |
|---------|----------|---------|-------------|
| 1       | 100      | 30      | ~1,500      |
| 2       | 200      | 30      | ~6,000      |
| 3       | 400      | 30      | ~24,000     |
| 4       | 600      | 30      | ~54,000     |
| 5       | 800      | 30      | ~96,000     |
| 6       | 1000     | 30      | ~150,000    |
| 7       | 1250     | 30      | ~234,000    |
| 8       | 1500     | 30      | ~337,500    |
| 9       | 1750     | 30      | ~459,000    |
| 10      | 2000     | 30      | ~600,000    |

File naming: `{v}v-30d-1min-1000max.txt`
Example: `1000v-30d-1min-1000max.txt`

---

## Summary Statistics

| Graph Type   | Graphs | Vertex Range    | Edge Range           |
|--------------|--------|-----------------|----------------------|
| Bipartite    | 10     | 102 - 2,402     | ~1,350 - ~720,000    |
| FixedDegree  | 10     | 100 - 4,000     | ~3,000 - ~120,000    |
| Mesh         | 10     | 402 - 90,002    | ~1,140 - ~269,100    |
| Random       | 10     | 100 - 2,000     | ~1,500 - ~600,000    |
| **Total**    | **40** |                 |                      |

## Estimated Benchmark Runtime

- **Total graphs:** 40 (10 per type × 4 types)
- **Runs per graph:** 10 runs × 3 algorithms = 30 executions per graph
- **Small/medium graphs:** Most under 1 minute per graph
- **Largest graphs:** Estimated 5-30 minutes per graph

**Target total runtime:** ~1-2 hours (may vary by machine and algorithm)

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

```text
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
