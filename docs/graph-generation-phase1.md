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

| Graph Type   | Fixed Parameters                         |
|--------------|------------------------------------------|
| Bipartite    | probability=0.5, min_cap=1, max_cap=10   |
| FixedDegree  | edges_per_node=5, min_cap=1, max_cap=10  |
| Mesh         | capacity=5, constant_capacity=true       |
| Random       | density=30, min_cap=1, max_cap=10        |

---

## Bipartite Graphs (10 graphs)

| # | Source | Sink | Filename                    |
|---|--------|------|-----------------------------|
| 1 | 5      | 5    | 5s-5t-05p-1min-10max.txt    |
| 2 | 10     | 10   | 10s-10t-05p-1min-10max.txt  |
| 3 | 20     | 20   | 20s-20t-05p-1min-10max.txt  |
| 4 | 30     | 30   | 30s-30t-05p-1min-10max.txt  |
| 5 | 40     | 40   | 40s-40t-05p-1min-10max.txt  |
| 6 | 50     | 50   | 50s-50t-05p-1min-10max.txt  |
| 7 | 75     | 75   | 75s-75t-05p-1min-10max.txt  |
| 8 | 100    | 100  | 100s-100t-05p-1min-10max.txt|
| 9 | 125    | 125  | 125s-125t-05p-1min-10max.txt|
| 10| 150    | 150  | 150s-150t-05p-1min-10max.txt|

---

## FixedDegree Graphs (10 graphs)

| # | Vertices | Filename                   |
|---|----------|----------------------------|
| 1 | 15       | 15v-5out-1min-10max.txt    |
| 2 | 25       | 25v-5out-1min-10max.txt    |
| 3 | 50       | 50v-5out-1min-10max.txt    |
| 4 | 100      | 100v-5out-1min-10max.txt   |
| 5 | 150      | 150v-5out-1min-10max.txt   |
| 6 | 200      | 200v-5out-1min-10max.txt   |
| 7 | 300      | 300v-5out-1min-10max.txt   |
| 8 | 400      | 400v-5out-1min-10max.txt   |
| 9 | 500      | 500v-5out-1min-10max.txt   |
| 10| 750      | 750v-5out-1min-10max.txt   |

---

## Mesh Graphs (10 graphs)

| # | Rows | Cols | Filename               |
|---|------|------|------------------------|
| 1 | 5    | 5    | 5r-5c-5cap-const.txt   |
| 2 | 8    | 8    | 8r-8c-5cap-const.txt   |
| 3 | 10   | 10   | 10r-10c-5cap-const.txt |
| 4 | 15   | 15   | 15r-15c-5cap-const.txt |
| 5 | 20   | 20   | 20r-20c-5cap-const.txt |
| 6 | 25   | 25   | 25r-25c-5cap-const.txt |
| 7 | 30   | 30   | 30r-30c-5cap-const.txt |
| 8 | 35   | 35   | 35r-35c-5cap-const.txt |
| 9 | 40   | 40   | 40r-40c-5cap-const.txt |
| 10| 50   | 50   | 50r-50c-5cap-const.txt |

---

## Random Graphs (10 graphs)

| # | Vertices | Filename                  |
|---|----------|---------------------------|
| 1 | 15       | 15v-30d-1min-10max.txt    |
| 2 | 25       | 25v-30d-1min-10max.txt    |
| 3 | 50       | 50v-30d-1min-10max.txt    |
| 4 | 75       | 75v-30d-1min-10max.txt    |
| 5 | 100      | 100v-30d-1min-10max.txt   |
| 6 | 150      | 150v-30d-1min-10max.txt   |
| 7 | 200      | 200v-30d-1min-10max.txt   |
| 8 | 250      | 250v-30d-1min-10max.txt   |
| 9 | 300      | 300v-30d-1min-10max.txt   |
| 10| 400      | 400v-30d-1min-10max.txt   |

---

## Output Directory Structure

```text
GeneratedGraphs/
├── Bipartite/
│   ├── 5s-5t-05p-1min-10max.txt
│   ├── 10s-10t-05p-1min-10max.txt
│   └── ...
├── FixedDegree/
│   ├── 15v-5out-1min-10max.txt
│   └── ...
├── Mesh/
│   ├── 5r-5c-5cap-const.txt
│   └── ...
└── Random/
    ├── 15v-30d-1min-10max.txt
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
