# Benchmark Results Summary - Phase 1

## Graph Generation Commands

Phase 1 used default parameters. The graphs were generated with:

```bash
# Generate all graph types with default Phase 1 parameters
python3 generate_graphs.py -o GeneratedGraphs

# Or generate specific types:
python3 generate_graphs.py -o GeneratedGraphs --types bipartite
python3 generate_graphs.py -o GeneratedGraphs --types fixeddegree
python3 generate_graphs.py -o GeneratedGraphs --types mesh
python3 generate_graphs.py -o GeneratedGraphs --types random
```

### Default Parameters Used

| Graph Type | Parameter | Value |
|------------|-----------|-------|
| **Bipartite** | probability | 0.5 |
| **Bipartite** | min_cap | 1 |
| **Bipartite** | max_cap | 1000 |
| **Bipartite** | sizes | 50, 100, 200, 300, 400, 500, 600, 800 |
| **FixedDegree** | edges_per_node | 30 |
| **FixedDegree** | min_cap | 1 |
| **FixedDegree** | max_cap | 1000 |
| **FixedDegree** | sizes | 100, 250, 500, 1000, 1500, 2000, 2500, 3000 |
| **Mesh** | capacity | 1000 |
| **Mesh** | mode | constant |
| **Mesh** | sizes | 20, 40, 60, 80, 100, 125, 150, 200 |
| **Random** | density | 30 |
| **Random** | min_cap | 1 |
| **Random** | max_cap | 1000 |
| **Random** | sizes | 100, 200, 400, 600, 800, 1000, 1250, 1500 |

### Benchmark Commands

```bash
# Run benchmarks on Phase 1 graphs
python3 benchmark.py -i GeneratedGraphs -o BenchmarkResultsData \
    -a ford_fulkerson,scaling_ford_fulkerson,preflow_push

# Generate plots
python3 plot_results.py -r BenchmarkResultsData -o BenchmarkResultsPlots --clean --log-scale
```

---

## Overview

Phase 1 experiments tested three maximum flow algorithms on four graph types with varying sizes:

- **Ford-Fulkerson (FF)**: Basic augmenting path algorithm
- **Scaling Ford-Fulkerson (SFF)**: Capacity scaling variant
- **Preflow-Push (PFP)**: Push-relabel algorithm

### Graph Parameters

- **Bipartite**: 50-800 source/sink nodes, 0.5 edge probability, capacities 1-1000
- **Mesh**: 20x20 to 200x200 grids, constant capacity 1000
- **FixedDegree**: 100-3000 vertices, 30 outgoing edges per node, capacities 1-1000
- **Random**: 100-2000 vertices, density ~30, capacities 1-1000

---

## Bipartite Graphs

### Performance Summary

| Graph Size | Vertices | Edges   | Max Flow | FF Mean (s) | SFF Mean (s) | PFP Mean (s) | Best Algorithm |
| ---------- | -------- | ------- | -------- | ----------- | ------------ | ------------ | -------------- |
| 50x50      | 102      | 1,331   | 23,224   | 0.0711      | 0.0828       | 0.0815       | **FF**         |
| 100x100    | 202      | 5,212   | 43,384   | 0.1213      | 0.1050       | 0.0970       | **PFP**        |
| 200x200    | 402      | 20,509  | 96,982   | 0.5202      | 0.2976       | 12.1445      | **SFF**        |
| 300x300    | 602      | 45,532  | 145,336  | 1.6601      | 0.7274       | 47.7462      | **SFF**        |
| 400x400    | 802      | 80,460  | 194,060  | 2.8845      | 1.3203       | 85.2093      | **SFF**        |
| 500x500    | 1,002    | 126,084 | 235,464  | 5.0802      | 2.0777       | 0.9047       | **PFP**        |
| 600x600    | 1,202    | 181,708 | 288,785  | 7.9856      | 3.3653       | 1.0569       | **PFP**        |
| 800x800    | 1,602    | 321,677 | 390,404  | 13.9960     | 6.1373       | 683.9838     | **SFF**        |

### Algorithm Comparison

| Algorithm | Min | Max | Mean | Median | StdDev | Overall Rank |
|-----------|-----|-----|------|--------|--------|--------------|
| **Ford-Fulkerson** | 0.056 | 23.505 | 4.017 | 1.560 | 5.352 | 3rd |
| **Scaling FF** | 0.059 | 9.478 | 2.064 | 1.057 | 2.491 | 2nd |
| **Preflow-Push** | 0.056 | 980.447 | 105.133 | 0.950 | 242.871 | 1st (large), 3rd (medium) |

### Runtime Ratios (Mean)

| Graph Size | FF/SFF | FF/PFP | SFF/PFP |
|------------|--------|--------|---------|
| 50x50 | 0.86 | 0.87 | 1.02 |
| 100x100 | 1.16 | 1.25 | 1.08 |
| 200x200 | 1.75 | 0.04 | 0.02 |
| 300x300 | 2.28 | 0.03 | 0.02 |
| 400x400 | 2.18 | 0.03 | 0.02 |
| 500x500 | 2.44 | 5.62 | 2.30 |
| 600x600 | 2.37 | 7.55 | 3.18 |
| 800x800 | 2.28 | 0.02 | 0.01 |

**Key Insight**: Preflow-Push shows erratic performance on bipartite graphs, excellent on some sizes (500, 600) but catastrophic on others (200-400, 800). SFF consistently outperforms FF by 2-2.5x.

---

## Mesh Graphs

### Performance Summary

| Graph Size | Vertices | Edges | Max Flow | FF Mean (s) | SFF Mean (s) | PFP Mean (s) | Best Algorithm |
|------------|----------|-------|----------|-------------|--------------|--------------|----------------|
| 20x20 | 402 | 1,180 | 20,000 | 0.0954 | 0.0753 | 0.0956 | **SFF** |
| 40x40 | 1,602 | 4,760 | 40,000 | 0.1255 | 0.0856 | 0.5002 | **SFF** |
| 60x60 | 3,602 | 10,740 | 60,000 | 0.1955 | 0.1567 | 2.1276 | **SFF** |
| 80x80 | 6,402 | 19,120 | 80,000 | 0.3651 | 0.3274 | 6.0749 | **SFF** |
| 100x100 | 10,002 | 29,900 | 100,000 | 0.7463 | 0.5823 | 12.6976 | **SFF** |
| 125x125 | 15,627 | 46,750 | 125,000 | 1.4141 | 1.2308 | 27.7979 | **SFF** |
| 150x150 | 22,502 | 67,350 | 150,000 | 2.5446 | 2.1383 | 55.5579 | **SFF** |
| 200x200 | 40,002 | 119,800 | 200,000 | 5.2196 | 4.0499 | 135.6259 | **SFF** |

### Algorithm Comparison

| Algorithm | Min | Max | Mean | Median | StdDev | Overall Rank |
|-----------|-----|-----|------|--------|--------|--------------|
| **Ford-Fulkerson** | 0.095 | 5.220 | 1.342 | 0.630 | 1.758 | 2nd |
| **Scaling FF** | 0.075 | 4.050 | 1.082 | 0.485 | 1.359 | **1st** |
| **Preflow-Push** | 0.096 | 135.626 | 30.016 | 12.699 | 45.668 | 3rd |

### Runtime Ratios (Mean)

| Graph Size | FF/SFF | FF/PFP | SFF/PFP |
|------------|--------|--------|---------|
| 20x20 | 1.27 | 1.00 | 0.79 |
| 40x40 | 1.47 | 0.25 | 0.17 |
| 60x60 | 1.25 | 0.09 | 0.07 |
| 80x80 | 1.12 | 0.06 | 0.05 |
| 100x100 | 1.28 | 0.06 | 0.05 |
| 125x125 | 1.15 | 0.05 | 0.04 |
| 150x150 | 1.19 | 0.05 | 0.04 |
| 200x200 | 1.29 | 0.04 | 0.03 |

**Key Insight**: SFF dominates on mesh graphs, consistently 15-30% faster than FF. Preflow-Push scales very poorly (O(n²m) behavior), becoming 20-30x slower than SFF on larger meshes.

---

## Fixed Degree Graphs

### Performance Summary FD

| Graph Size | Vertices | Edges | Max Flow | FF Mean (s) | SFF Mean (s) | PFP Mean (s) | Best Algorithm |
|------------|----------|-------|----------|-------------|--------------|--------------|----------------|
| 100v | 102 | 3,060 | 13,370 | 0.0736 | 0.0813 | 0.4273 | **FF** |
| 250v | 252 | 7,560 | 13,107 | 0.0977 | 0.0719 | 0.0910 | **SFF** |
| 500v | 502 | 15,060 | 15,046 | 0.1299 | 0.1079 | 10.3521 | **SFF** |
| 1000v | 1,002 | 30,060 | 16,189 | 0.1774 | 0.1386 | 0.1963 | **SFF** |
| 1500v | 1,502 | 45,060 | 14,829 | 0.2458 | 0.1659 | 0.2493 | **SFF** |
| 2000v | 2,002 | 60,060 | 13,977 | 0.4028 | 0.2967 | 159.4608 | **SFF** |
| 2500v | 2,502 | 75,060 | 13,994 | 0.4571 | 0.3519 | 236.0366 | **SFF** |
| 3000v | 3,002 | 90,060 | 14,613 | 0.5672 | 0.4489 | 315.3634 | **SFF** |

### Algorithm Comparison

| Algorithm | Min | Max | Mean | Median | StdDev | Overall Rank |
|-----------|-----|-----|------|--------|--------|--------------|
| **Ford-Fulkerson** | 0.074 | 0.567 | 0.269 | 0.212 | 0.179 | 2nd |
| **Scaling FF** | 0.072 | 0.449 | 0.206 | 0.154 | 0.138 | **1st** |
| **Preflow-Push** | 0.091 | 315.363 | 90.244 | 0.249 | 141.128 | 3rd |

### Runtime Ratios (Mean)

| Graph Size | FF/SFF | FF/PFP | SFF/PFP |
|------------|--------|--------|---------|
| 100v | 0.91 | 0.17 | 0.19 |
| 250v | 1.36 | 1.07 | 0.79 |
| 500v | 1.20 | 0.01 | 0.01 |
| 1000v | 1.28 | 0.90 | 0.71 |
| 1500v | 1.48 | 0.99 | 0.67 |
| 2000v | 1.36 | 0.00 | 0.00 |
| 2500v | 1.30 | 0.00 | 0.00 |
| 3000v | 1.26 | 0.00 | 0.00 |

**Key Insight**: Preflow-Push catastrophically fails on certain fixed-degree graphs (500v, 2000v+), taking hundreds of seconds. SFF is consistently 25-50% faster than FF and orders of magnitude faster than PFP on problematic cases.

---

## Random Graphs

### Performance Summary

| Graph Size | Vertices | Edges | Max Flow | FF Mean (s) | SFF Mean (s) | PFP Mean (s) | Best Algorithm |
|------------|----------|-------|----------|-------------|--------------|--------------|----------------|
| 100v | 101 | 2,947 | 11,745 | 0.0804 | 0.0655 | 0.0670 | **SFF** |
| 200v | 201 | 12,206 | 33,735 | 0.1413 | 0.1162 | 0.0843 | **PFP** |
| 400v | 401 | 47,271 | 61,185 | 0.3300 | 0.2325 | 0.1974 | **PFP** |
| 600v | 601 | 107,589 | 89,375 | 0.7080 | 0.4455 | 0.3085 | **PFP** |
| 800v | 801 | 191,043 | 113,742 | 1.5797 | 0.9979 | 102.2616 | **SFF** |
| 1000v | 1,001 | 298,712 | 141,504 | 3.0914 | 2.0862 | 188.1224 | **SFF** |
| 1250v | 1,251 | 467,890 | 182,410 | 4.9226 | 2.6416 | 1.2610 | **PFP** |
| 1500v | 1,501 | 672,543 | 228,726 | 6.6109 | 3.4021 | 1.8031 | **PFP** |

### Algorithm Comparison

| Algorithm | Min | Max | Mean | Median | StdDev | Overall Rank |
|-----------|-----|-----|------|--------|--------|--------------|
| **Ford-Fulkerson** | 0.080 | 6.611 | 2.183 | 1.036 | 2.406 | 3rd |
| **Scaling FF** | 0.066 | 3.402 | 1.374 | 0.687 | 1.292 | 2nd |
| **Preflow-Push** | 0.067 | 188.122 | 36.807 | 0.854 | 71.051 | 1st (most cases) |

### Runtime Ratios (Mean)

| Graph Size | FF/SFF | FF/PFP | SFF/PFP |
|------------|--------|--------|---------|
| 100v | 1.23 | 1.20 | 0.98 |
| 200v | 1.22 | 1.68 | 1.38 |
| 400v | 1.42 | 1.67 | 1.18 |
| 600v | 1.59 | 2.29 | 1.44 |
| 800v | 1.58 | 0.02 | 0.01 |
| 1000v | 1.48 | 0.02 | 0.01 |
| 1250v | 1.86 | 3.90 | 2.09 |
| 1500v | 1.94 | 3.67 | 1.89 |

**Key Insight**: Preflow-Push excels on most random graphs (2-4x faster than FF), but fails catastrophically at 800-1000 vertices. SFF provides consistent performance, 1.4-2x faster than FF across all sizes.

---

## Overall Analysis

### Algorithm Performance by Graph Type

| Graph Type      | Best Overall      | Most Consistent | Most Predictable |
| --------------- | ----------------- | --------------- | ---------------- |
| **Bipartite**   | SFF               | SFF             | SFF              |
| **Mesh**        | SFF               | SFF             | SFF              |
| **FixedDegree** | SFF               | SFF             | SFF              |
| **Random**      | PFP (conditional) | SFF             | SFF              |

### Key Findings

1. **Scaling Ford-Fulkerson is the most reliable**: Consistently 1.2-2.5x faster than basic FF across all graph types with no catastrophic failures.

2. **Preflow-Push has high variance**: Can be 2-5x faster than FF on favorable graphs (random, some bipartite) but suffers catastrophic O(n²m) behavior on:
   - Dense bipartite graphs (200-400, 800 nodes)
   - Fixed-degree graphs (500v, 2000v+)
   - Some random graphs (800-1000v)

3. **Ford-Fulkerson is predictable but slow**: Never catastrophic, but consistently slower than SFF.

### Capacity Impact

Phase 1 used high capacities (1-1000) which may favor capacity-scaling algorithms (SFF). The O(mC) dependence of FF may explain its worse performance compared to SFF's O(m² log C).

### Recommendations

- **For production**: Use Scaling FF - best balance of performance and reliability
- **For research**: Investigate why Preflow-Push fails on specific graph structures
- **Next phase**: Test with lower capacities (1-10) to see if capacity-dependent algorithms change relative performance
