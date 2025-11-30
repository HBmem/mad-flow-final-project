# Phase 1: Graph Generation Plan

This document describes the graphs to be generated for Phase 1 experiments (size scaling analysis).

## Overview

- **Total graphs:** 40 (10 per type × 4 types)
- **Output directory:** `GeneratedGraphs/` (gitignored - generate locally)
- **Generation script:** `generate_graphs.py`

## Quick Start

```bash
# Generate all 40 graphs (Java classes are compiled automatically)
python3 generate_graphs.py
```

The script will:

1. Compile Java files if needed
2. Create `GeneratedGraphs/{Bipartite,FixedDegree,Mesh,Random}/` directories
3. Generate all 40 graphs according to the plan below
4. Skip existing files (safe to re-run)

---

## Fixed Parameters

| Graph Type   | Fixed Parameters                              |
|--------------|-----------------------------------------------|
| Bipartite    | probability=0.5, min_cap=1, max_cap=1000      |
| FixedDegree  | **edges_per_node=30**, min_cap=1, max_cap=1000|
| Mesh         | **capacity=1000**, constant_capacity=true     |
| Random       | **density=30**, min_cap=1, max_cap=1000       |

> **Target:** ~5 minute max Ford-Fulkerson runtime.
>
> **Note on connectivity:** FixedDegree uses **30 edges/node** for many flow paths.
> Random uses **density=30** (30% of edges) for high max_flow values.

---

## Bipartite Graphs (10 graphs)

| # | Source | Sink | Vertices | Est. Edges | Filename                         |
|---|--------|------|----------|------------|----------------------------------|
| 1 | 50     | 50   | 102      | ~1,350     | 50s-50t-05p-1min-1000max.txt     |
| 2 | 100    | 100  | 202      | ~5,200     | 100s-100t-05p-1min-1000max.txt   |
| 3 | 200    | 200  | 402      | ~20,400    | 200s-200t-05p-1min-1000max.txt   |
| 4 | 300    | 300  | 602      | ~45,000    | 300s-300t-05p-1min-1000max.txt   |
| 5 | 400    | 400  | 802      | ~80,000    | 400s-400t-05p-1min-1000max.txt   |
| 6 | 500    | 500  | 1,002    | ~125,000   | 500s-500t-05p-1min-1000max.txt   |
| 7 | 600    | 600  | 1,202    | ~180,000   | 600s-600t-05p-1min-1000max.txt   |
| 8 | 800    | 800  | 1,602    | ~320,000   | 800s-800t-05p-1min-1000max.txt   |
| 9 | 1000   | 1000 | 2,002    | ~500,000   | 1000s-1000t-05p-1min-1000max.txt |
| 10| 1200   | 1200 | 2,402    | ~720,000   | 1200s-1200t-05p-1min-1000max.txt |

---

## FixedDegree Graphs (10 graphs)

| # | Vertices | Edges/Node | Est. Edges | Filename                      |
|---|----------|------------|------------|-------------------------------|
| 1 | 100      | 30         | ~3,000     | 100v-30out-1min-1000max.txt   |
| 2 | 250      | 30         | ~7,500     | 250v-30out-1min-1000max.txt   |
| 3 | 500      | 30         | ~15,000    | 500v-30out-1min-1000max.txt   |
| 4 | 1000     | 30         | ~30,000    | 1000v-30out-1min-1000max.txt  |
| 5 | 1500     | 30         | ~45,000    | 1500v-30out-1min-1000max.txt  |
| 6 | 2000     | 30         | ~60,000    | 2000v-30out-1min-1000max.txt  |
| 7 | 2500     | 30         | ~75,000    | 2500v-30out-1min-1000max.txt  |
| 8 | 3000     | 30         | ~90,000    | 3000v-30out-1min-1000max.txt  |
| 9 | 3500     | 30         | ~105,000   | 3500v-30out-1min-1000max.txt  |
| 10| 4000     | 30         | ~120,000   | 4000v-30out-1min-1000max.txt  |

---

## Mesh Graphs (10 graphs)

| # | Rows | Cols | Vertices | Est. Edges | Filename                    |
|---|------|------|----------|------------|-----------------------------|
| 1 | 20   | 20   | 402      | ~1,140     | 20r-20c-1000cap-const.txt   |
| 2 | 40   | 40   | 1,602    | ~4,680     | 40r-40c-1000cap-const.txt   |
| 3 | 60   | 60   | 3,602    | ~10,620    | 60r-60c-1000cap-const.txt   |
| 4 | 80   | 80   | 6,402    | ~19,040    | 80r-80c-1000cap-const.txt   |
| 5 | 100  | 100  | 10,002   | ~29,700    | 100r-100c-1000cap-const.txt |
| 6 | 125  | 125  | 15,627   | ~46,500    | 125r-125c-1000cap-const.txt |
| 7 | 150  | 150  | 22,502   | ~67,050    | 150r-150c-1000cap-const.txt |
| 8 | 200  | 200  | 40,002   | ~119,400   | 200r-200c-1000cap-const.txt |
| 9 | 250  | 250  | 62,502   | ~186,750   | 250r-250c-1000cap-const.txt |
| 10| 300  | 300  | 90,002   | ~269,100   | 300r-300c-1000cap-const.txt |

---

## Random Graphs (10 graphs)

| # | Vertices | Density | Est. Edges | Filename                     |
|---|----------|---------|------------|------------------------------|
| 1 | 100      | 30      | ~1,500     | 100v-30d-1min-1000max.txt    |
| 2 | 200      | 30      | ~6,000     | 200v-30d-1min-1000max.txt    |
| 3 | 400      | 30      | ~24,000    | 400v-30d-1min-1000max.txt    |
| 4 | 600      | 30      | ~54,000    | 600v-30d-1min-1000max.txt    |
| 5 | 800      | 30      | ~96,000    | 800v-30d-1min-1000max.txt    |
| 6 | 1000     | 30      | ~150,000   | 1000v-30d-1min-1000max.txt   |
| 7 | 1250     | 30      | ~234,000   | 1250v-30d-1min-1000max.txt   |
| 8 | 1500     | 30      | ~337,500   | 1500v-30d-1min-1000max.txt   |
| 9 | 1750     | 30      | ~459,000   | 1750v-30d-1min-1000max.txt   |
| 10| 2000     | 30      | ~600,000   | 2000v-30d-1min-1000max.txt   |

---

## Output Directory Structure

```text
GeneratedGraphs/
├── Bipartite/
│   ├── 50s-50t-05p-1min-1000max.txt
│   ├── 100s-100t-05p-1min-1000max.txt
│   └── ...
├── FixedDegree/
│   ├── 100v-30out-1min-1000max.txt
│   └── ...
├── Mesh/
│   ├── 20r-20c-1000cap-const.txt
│   └── ...
└── Random/
    ├── 100v-30d-1min-1000max.txt
    └── ...
```

---

## Manual Generation (Command-Line)

If you need to generate graphs manually, use these commands:

### Bipartite

```bash
cd graphGenerationCode/Bipartite
javac BipartiteGraph.java
java BipartiteGraph <src_nodes> <sink_nodes> <probability> <min_cap> <max_cap> <output_file>
# Example:
java BipartiteGraph 10 10 0.5 1 10 output.txt
```

### FixedDegree

```bash
cd graphGenerationCode/FixedDegree
javac RandomGraph.java
java RandomGraph <vertices> <edges_per_node> <min_cap> <max_cap> <output_file>
# Example:
java RandomGraph 100 5 1 10 output.txt
```

### Mesh

```bash
cd graphGenerationCode/Mesh
javac MeshGenerator.java
java MeshGenerator <rows> <cols> <capacity> <output_file> [-cc]
# Example (random capacities 1 to 10):
java MeshGenerator 10 10 10 output.txt
# Example (constant capacity 5):
java MeshGenerator 10 10 5 output.txt -cc
```

### Random

```bash
cd graphGenerationCode/Random
javac BuildGraph.java
java BuildGraph <vertices> <density> <min_cap> <max_cap> <output_file>
# Example:
java BuildGraph 100 30 1 10 output.txt
```
