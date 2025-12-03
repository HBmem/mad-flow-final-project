# Benchmark Results Summary - Phase 3

## Graph Generation Commands

Phase 3 tests the effect of **low edge capacities** (1-10 vs 1-1000 in Phase 1) to see how capacity-dependent algorithms perform:

- **Ford-Fulkerson**: O(mC) - should be ~100x faster with C=10 vs C=1000
- **Scaling Ford-Fulkerson**: O(m² log C) - should be ~3x faster (log 10 ≈ 3.3 vs log 1000 ≈ 10)
- **Preflow-Push**: O(n²m) - should be unchanged (independent of capacity)

```bash
# Bipartite: Same as Phase 1 but with max_cap=10
python3 generate_graphs.py -o GeneratedGraphs3 --types bipartite \
    --bipartite-min-cap 1 --bipartite-max-cap 10 \
    --bipartite-sizes 50,100,200,300,400,500,600,800

# FixedDegree: Same as Phase 1 but with max_cap=10
python3 generate_graphs.py -o GeneratedGraphs3 --types fixeddegree \
    --fixeddegree-min-cap 1 --fixeddegree-max-cap 10 \
    --fixeddegree-sizes 100,250,500,1000,1500,2000,2500,3000

# Mesh: Capacity=10 with constant mode
python3 generate_graphs.py -o GeneratedGraphs3 --types mesh \
    --mesh-capacity 10 --mesh-constant \
    --mesh-sizes 20,40,60,80,100,125,150,200

# Random: Same as Phase 1 but with max_cap=10
python3 generate_graphs.py -o GeneratedGraphs3 --types random \
    --random-min-cap 1 --random-max-cap 10 \
    --random-sizes 100,200,400,600,800,1000,1250,1500
```

### Or as a Single Command

```bash
python3 generate_graphs.py -o GeneratedGraphs3 \
    --bipartite-min-cap 1 --bipartite-max-cap 10 \
    --fixeddegree-min-cap 1 --fixeddegree-max-cap 10 \
    --mesh-capacity 10 --mesh-constant \
    --random-min-cap 1 --random-max-cap 10
```

### Benchmark Commands

```bash
# Run benchmarks on Phase 3 graphs
python3 benchmark.py -i GeneratedGraphs3 -o BenchmarkResultsData3 \
    -a ford_fulkerson,scaling_ford_fulkerson,preflow_push

# Generate plots
python3 plot_results.py -r BenchmarkResultsData3 -o BenchmarkResultsPlots3 --clean --log-scale
```

---

## Overview

Phase 3 experiments test the effect of **low edge capacities** on algorithm performance.

| Graph Type | Parameter Changed | Phase 1 Value | Phase 3 Value |
|------------|------------------|---------------|---------------|
| **Bipartite** | max_cap | 1000 | **10** |
| **FixedDegree** | max_cap | 1000 | **10** |
| **Mesh** | capacity | 1000 | **10** |
| **Random** | max_cap | 1000 | **10** |

### Expected Impact

| Algorithm | Complexity | Phase 1 (C=1000) | Phase 3 (C=10) | Expected Speedup |
|-----------|------------|------------------|----------------|------------------|
| **FF** | O(mC) | O(m × 1000) | O(m × 10) | **~100x faster** |
| **SFF** | O(m² log C) | O(m² × 10) | O(m² × 3.3) | **~3x faster** |
| **PFP** | O(n²m) | O(n²m) | O(n²m) | **No change** |

### Algorithms Tested

- **Ford-Fulkerson (FF)**: O(mC) - Basic augmenting path
- **Scaling Ford-Fulkerson (SFF)**: O(m² log C) - Capacity scaling variant
- **Preflow-Push (PFP)**: O(n²m) - Push-relabel algorithm

---

## Bipartite Graphs (max_cap=10)

Lower capacities dramatically changed the performance landscape.

### Performance Summary

| Size | Vertices | Edges | Max Flow | FF (s) | SFF (s) | PFP (s) | Winner |
|------|----------|-------|----------|--------|---------|---------|--------|
| 50×50 | 102 | 1,366 | 211 | 0.079 | 0.074 | 0.077 | SFF |
| 100×100 | 202 | 5,198 | 521 | 0.117 | 0.098 | **0.087** | **PFP** |
| 200×200 | 402 | 20,380 | 1,018 | 0.358 | **0.251** | 12.41 | SFF |
| 300×300 | 602 | 45,481 | 1,647 | 1.12 | **0.60** | 20.72 | SFF |
| 400×400 | 802 | 80,750 | 2,059 | 2.15 | **1.11** | 96.83 | SFF |
| 500×500 | 1,002 | 126,037 | 2,735 | 3.99 | **1.94** | 147.48 | SFF |
| 600×600 | 1,202 | 181,588 | 3,225 | 6.07 | 2.75 | **0.98** | **PFP** ⚠️ |
| 800×800 | 1,602 | 321,384 | 4,325 | 10.72 | **4.72** | 541.36 | SFF |

**Key Findings**:

- SFF dominates most sizes (1.4-2.3x faster than FF)
- PFP shows extreme bimodal behavior:
  - **Wins** at 100×100 and 600×600 (order of magnitude faster)
  - **Catastrophic failures** at most other sizes (10-100x slower)
- The 600×600 PFP result (0.98s vs 2.75s for SFF) is a striking anomaly

### Algorithm Ratios (Mean Runtime)

| Size | Edges | FF/SFF | FF/PFP | SFF/PFP |
|------|-------|--------|--------|---------|
| 50×50 | 1,366 | 1.06 | 1.02 | 0.96 |
| 100×100 | 5,198 | 1.20 | 1.34 | 1.12 |
| 200×200 | 20,380 | 1.42 | 0.03 | 0.02 |
| 300×300 | 45,481 | 1.87 | 0.05 | 0.03 |
| 400×400 | 80,750 | 1.94 | 0.02 | 0.01 |
| 500×500 | 126,037 | 2.06 | 0.03 | 0.01 |
| 600×600 | 181,588 | 2.21 | 6.21 | 2.81 |
| 800×800 | 321,384 | 2.27 | 0.02 | 0.01 |

---

## Fixed Degree Graphs (max_cap=10)

### Performance Summary

| Size | Vertices | Edges | Max Flow | FF (s) | SFF (s) | PFP (s) | Winner |
|------|----------|-------|----------|--------|---------|---------|--------|
| 100v | 102 | 3,060 | 170 | 0.075 | 0.074 | 0.074 | Tie |
| 250v | 252 | 7,560 | 146 | 0.081 | 0.081 | 0.086 | Tie |
| 500v | 502 | 15,060 | 196 | 0.106 | **0.088** | 9.97 | SFF |
| 1000v | 1,002 | 30,060 | 147 | **0.137** | 0.148 | 40.75 | FF |
| 1500v | 1,502 | 45,060 | 151 | 0.172 | **0.160** | 86.24 | SFF |
| 2000v | 2,002 | 60,060 | 169 | 0.201 | **0.164** | **0.277** | SFF |
| 2500v | 2,502 | 75,060 | 157 | 0.309 | **0.282** | 210.71 | SFF |
| 3000v | 3,002 | 90,060 | 175 | 0.398 | **0.270** | 278.26 | SFF |

**Key Findings**:

- FF and SFF are very close in performance (within 20% of each other)
- At 1000v, FF actually beats SFF slightly
- PFP shows severe pathological behavior:
  - Normal at 100v, 250v, 2000v
  - **100-1000x slower** at most other sizes
- The 2000v PFP result (0.277s) is an anomaly surrounded by catastrophic cases

### Algorithm Ratios (Mean Runtime)

| Size | Edges | FF/SFF | FF/PFP | SFF/PFP |
|------|-------|--------|--------|---------|
| 100v | 3,060 | 1.00 | 1.00 | 1.00 |
| 250v | 7,560 | 0.99 | 0.94 | 0.95 |
| 500v | 15,060 | 1.20 | 0.01 | 0.01 |
| 1000v | 30,060 | 0.93 | 0.003 | 0.004 |
| 1500v | 45,060 | 1.08 | 0.002 | 0.002 |
| 2000v | 60,060 | 1.23 | 0.73 | 0.59 |
| 2500v | 75,060 | 1.10 | 0.001 | 0.001 |
| 3000v | 90,060 | 1.48 | 0.001 | 0.001 |

---

## Mesh Graphs (capacity=10)

### Performance Summary

| Size | Vertices | Edges | Max Flow | FF (s) | SFF (s) | PFP (s) | Winner |
|------|----------|-------|----------|--------|---------|---------|--------|
| 20×20 | 402 | 1,180 | 200 | **0.061** | 0.070 | 0.098 | FF |
| 40×40 | 1,602 | 4,760 | 400 | **0.095** | 0.093 | 0.534 | Tie |
| 60×60 | 3,602 | 10,740 | 600 | **0.165** | 0.184 | 1.98 | FF |
| 80×80 | 6,402 | 19,120 | 800 | **0.292** | 0.335 | 5.80 | FF |
| 100×100 | 10,002 | 29,900 | 1,000 | **0.545** | 0.619 | 13.10 | FF |
| 125×125 | 15,627 | 46,750 | 1,250 | **1.14** | 1.19 | 28.68 | FF |
| 150×150 | 22,502 | 67,350 | 1,500 | 2.03 | **1.85** | 51.28 | SFF |
| 200×200 | 40,002 | 119,800 | 2,000 | 4.29 | **3.64** | 129.68 | SFF |

**Key Findings**:

- **FF wins on small-to-medium meshes** (up to 125×125)
- SFF catches up on larger meshes (150×150+)
- PFP is consistently **10-35x slower** than FF/SFF
- No erratic PFP behavior here - just consistently bad performance
- With low capacities, FF's O(mC) complexity becomes very competitive

### Algorithm Ratios (Mean Runtime)

| Size | Edges | FF/SFF | FF/PFP | SFF/PFP |
|------|-------|--------|--------|---------|
| 20×20 | 1,180 | 0.87 | 0.62 | 0.71 |
| 40×40 | 4,760 | 1.02 | 0.18 | 0.17 |
| 60×60 | 10,740 | 0.90 | 0.08 | 0.09 |
| 80×80 | 19,120 | 0.87 | 0.05 | 0.06 |
| 100×100 | 29,900 | 0.88 | 0.04 | 0.05 |
| 125×125 | 46,750 | 0.96 | 0.04 | 0.04 |
| 150×150 | 67,350 | 1.10 | 0.04 | 0.04 |
| 200×200 | 119,800 | 1.18 | 0.03 | 0.03 |

---

## Random Graphs (max_cap=10)

### Performance Summary

| Size | Vertices | Edges | Max Flow | FF (s) | SFF (s) | PFP (s) | Winner |
|------|----------|-------|----------|--------|---------|---------|--------|
| 100v | 101 | 2,895 | 80 | 0.066 | 0.066 | **0.064** | PFP |
| 200v | 201 | 12,014 | 268 | 0.110 | **0.099** | 1.65 | SFF |
| 400v | 401 | 47,856 | 615 | 0.225 | **0.162** | 0.191 | SFF |
| 600v | 601 | 107,878 | 1,023 | 0.630 | 0.323 | **0.314** | PFP |
| 800v | 801 | 191,827 | 1,304 | 1.10 | 0.634 | **0.459** | PFP |
| 1000v | 1,001 | 298,909 | 1,649 | 2.23 | 1.13 | **0.721** | PFP |
| 1250v | 1,251 | 467,254 | 1,899 | 3.51 | 1.70 | **1.17** | PFP |
| 1500v | 1,501 | 675,307 | 2,300 | 5.68 | **2.83** | 491.51 | SFF |

**Key Findings**:

- **PFP wins on dense random graphs** (600v-1250v)
- The 1500v PFP catastrophe is dramatic: jumps from 1.17s to 491s
- SFF provides consistent ~2x speedup over FF
- Random graphs with low capacity show most favorable PFP behavior of any type

### Algorithm Ratios (Mean Runtime)

| Size | Edges | FF/SFF | FF/PFP | SFF/PFP |
|------|-------|--------|--------|---------|
| 100v | 2,895 | 0.99 | 1.03 | 1.04 |
| 200v | 12,014 | 1.11 | 0.07 | 0.06 |
| 400v | 47,856 | 1.39 | 1.18 | 0.85 |
| 600v | 107,878 | 1.95 | 2.01 | 1.03 |
| 800v | 191,827 | 1.73 | 2.39 | 1.38 |
| 1000v | 298,909 | 1.98 | 3.09 | 1.56 |
| 1250v | 467,254 | 2.06 | 3.00 | 1.46 |
| 1500v | 675,307 | 2.01 | 0.01 | 0.01 |

---

## Phase 1 vs Phase 3: Capacity Impact Analysis

### Did FF Get the Expected 100x Speedup?

Comparing comparable graph sizes between Phase 1 (C=1000) and Phase 3 (C=10):

| Graph Type | Size | Phase 1 FF | Phase 3 FF | Actual Speedup |
|------------|------|------------|------------|----------------|
| Bipartite | 200×200 | 8.15s | 0.358s | **23x** |
| Bipartite | 400×400 | 36.0s | 2.15s | **17x** |
| FixedDegree | 1000v | 1.42s | 0.137s | **10x** |
| FixedDegree | 2000v | 2.75s | 0.201s | **14x** |
| Mesh | 100×100 | 4.32s | 0.545s | **8x** |
| Mesh | 200×200 | 25.4s | 4.29s | **6x** |
| Random | 1000v | 39.7s | 2.23s | **18x** |

**Observation**: FF achieved **6-23x speedup**, not the theoretical 100x. This suggests:

- Constant factors dominate at smaller graph sizes
- BFS overhead doesn't scale with capacity
- Graph structure affects number of augmenting paths found

### Did SFF Get the Expected 3x Speedup?

| Graph Type | Size | Phase 1 SFF | Phase 3 SFF | Actual Speedup |
|------------|------|-------------|-------------|----------------|
| Bipartite | 200×200 | 0.594s | 0.251s | **2.4x** |
| Bipartite | 400×400 | 2.00s | 1.11s | **1.8x** |
| FixedDegree | 1000v | 0.430s | 0.148s | **2.9x** |
| FixedDegree | 2000v | 0.712s | 0.164s | **4.3x** |
| Mesh | 100×100 | 4.20s | 0.619s | **6.8x** |
| Mesh | 200×200 | 26.2s | 3.64s | **7.2x** |
| Random | 1000v | 2.00s | 1.13s | **1.8x** |

**Observation**: SFF achieved **1.8-7.2x speedup**, roughly matching or exceeding the expected ~3x for most cases.

### Did PFP Stay the Same?

| Graph Type | Size | Phase 1 PFP | Phase 3 PFP | Change |
|------------|------|-------------|-------------|--------|
| Bipartite | 200×200 | 2.60s | 12.41s | **4.8x slower** |
| Bipartite | 400×400 | 15.1s | 96.83s | **6.4x slower** |
| FixedDegree | 1000v | 6.07s | 40.75s | **6.7x slower** |
| Mesh | 100×100 | 10.5s | 13.10s | 1.2x slower |
| Random | 1000v | 0.697s | 0.721s | ~same |

**Observation**: PFP got **worse** on some graph types, not unchanged! This is surprising since PFP is theoretically O(n²m) independent of capacity. Possible explanations:

- Different graph structures (new random seeds)
- More augmenting paths needed with lower capacities
- Implementation details affecting practical performance

---

## Conclusions

### Key Finding: Low Capacity Makes FF Competitive

With C=10 instead of C=1000:

1. **FF wins on Mesh graphs** - The clearest result: FF beats SFF on meshes up to 125×125
2. **FF nearly ties SFF on FixedDegree** - Within 20% of each other
3. **SFF still dominates Bipartite** - But by a smaller margin (1.4-2.3x vs 5-10x in Phase 1)

### PFP Remains Unpredictable

- **Random graphs**: Best PFP performance (wins at 600v-1250v)
- **Mesh graphs**: Consistently 10-35x slower (no catastrophes, but no wins)
- **Bipartite/FixedDegree**: Erratic - some anomalous wins, many catastrophic failures

### Revised Algorithm Recommendations

| Scenario | Phase 1 (High C) | Phase 3 (Low C) |
|----------|------------------|-----------------|
| **General use** | SFF | SFF (still safest) |
| **Mesh graphs** | SFF or FF | **FF** (definite winner) |
| **Dense random** | SFF | **PFP** (if no catastrophe) |
| **Predictability needed** | SFF | **FF** (more consistent than SFF) |

### Summary

**With low capacities (C=10), Ford-Fulkerson becomes the algorithm of choice for structured graphs like meshes**, while Scaling Ford-Fulkerson remains the safe default for general use. Preflow-Push continues to be unpredictable regardless of capacity.
