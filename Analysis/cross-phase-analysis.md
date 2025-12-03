# Cross-Phase Analysis: Maximum Flow Algorithm Comparison

## Executive Summary

This analysis compares three maximum flow algorithms across three experimental phases:

| Phase | Variable Tested | Key Finding |
|-------|----------------|-------------|
| **Phase 1** | Baseline (high capacity C=1000) | SFF dominates; PFP erratic |
| **Phase 2** | Higher density | SFF most density-resistant; PFP collapses |
| **Phase 3** | Low capacity (C=10) | FF becomes competitive; PFP still erratic |

**Bottom Line**:

- **Scaling Ford-Fulkerson (SFF)** is the safest choice across all conditions
- **Ford-Fulkerson (FF)** excels with low capacities, especially on mesh graphs
- **Preflow-Push (PFP)** is unpredictable and should be avoided without graph-specific testing

---

## Phase Overview

### What Each Phase Tested

| Phase | Focus | Hypothesis |
|-------|-------|------------|
| **Phase 1** | Baseline performance | Establish algorithm rankings on standard graphs |
| **Phase 2** | Density impact | Higher density should favor PFP (local operations) |
| **Phase 3** | Capacity impact | Lower C should speed up FF by 100x (O(mC)) |

### Parameter Changes

| Graph Type | Phase 1 | Phase 2 | Phase 3 |
|------------|---------|---------|---------|
| **Bipartite** | p=0.5, C=1000 | p=0.8, C=1000 | p=0.5, C=10 |
| **FixedDegree** | 30 edges, C=1000 | 50 edges, C=1000 | 30 edges, C=10 |
| **Mesh** | C=1000 | smaller sizes | C=10 |
| **Random** | density=30, C=1000 | density=60, C=1000 | density=30, C=10 |

---

## Algorithm Performance Across Phases

### Ford-Fulkerson (FF)

| Phase | Strengths | Weaknesses | Ranking |
|-------|-----------|------------|---------|
| **Phase 1** | Predictable, no catastrophes | 1.2-2.5x slower than SFF | 2nd-3rd |
| **Phase 2** | Competitive on small graphs | 20-30% slowdown with density | 2nd |
| **Phase 3** | **Wins on mesh graphs** | Still slower on bipartite | **1st-2nd** |

**Pattern**: FF improves dramatically with low capacity. The theoretical O(mC) complexity is validated—reducing C by 100x gives 6-23x speedup (not 100x due to constant factors).

### Scaling Ford-Fulkerson (SFF)

| Phase | Strengths | Weaknesses | Ranking |
|-------|-----------|------------|---------|
| **Phase 1** | Consistently fastest, 1.2-2.5x over FF | Slightly slower than PFP on some random | **1st** |
| **Phase 2** | Most density-resistant (0-10% slowdown) | None significant | **1st** |
| **Phase 3** | Still reliable, 1.8-7.2x speedup | Loses to FF on mesh | **1st-2nd** |

**Pattern**: SFF is remarkably consistent. It never catastrophically fails and is least affected by parameter changes. The O(m² log C) complexity means it benefits from lower C but not as dramatically as FF.

### Preflow-Push (PFP)

| Phase | Strengths | Weaknesses | Ranking |
|-------|-----------|------------|---------|
| **Phase 1** | Fastest on some random (2-4x over FF) | Catastrophic on bipartite, fixed-degree | Erratic |
| **Phase 2** | Wins on 100v, 250v random | Collapses with density (18x slowdown) | Erratic |
| **Phase 3** | Wins on 600v-1250v random | Still catastrophic on most graphs | Erratic |

**Pattern**: PFP's O(n²m) complexity makes it theoretically independent of capacity, but it shows extreme sensitivity to graph structure. Success seems random—it can be fastest or 100-1000x slowest.

---

## Graph Type Analysis Across Phases

### Bipartite Graphs

| Metric | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **Winner** | SFF | SFF | SFF |
| **FF/SFF ratio** | 1.75-2.44x | 1.10-1.61x | 1.06-2.27x |
| **PFP behavior** | Erratic (wins at 500-600, fails at 200-400, 800) | Erratic (fails at 75-100) | Erratic (wins at 100, 600) |

**Explanation**: Bipartite structure creates long augmenting paths but relatively few of them. SFF's capacity scaling finds good paths efficiently. PFP struggles because the source/sink structure means many pushes get "stuck" and need relabeling.

### Mesh Graphs

| Metric | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **Winner** | SFF | FF/SFF tied | **FF** |
| **FF/SFF ratio** | 1.12-1.47x | 0.92-1.04x | **0.87-1.18x (FF wins)** |
| **PFP behavior** | Consistently 20-30x slower | Consistently 4-11x slower | Consistently 10-35x slower |

**Explanation**: Mesh graphs have a regular, sparse structure. With high capacity, SFF's logarithmic scaling helps. With low capacity, FF's simple BFS finds short augmenting paths efficiently. PFP's O(n²m) complexity is devastating because n is very large (n = rows × cols) relative to m (sparse edges).

**Key Insight**: This is the only graph type where we can confidently recommend FF over SFF (when C is low).

### Fixed Degree Graphs

| Metric | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **Winner** | SFF | SFF | SFF (FF close) |
| **FF/SFF ratio** | 0.91-1.48x | 1.01-1.11x | 0.93-1.48x |
| **PFP behavior** | Catastrophic at 500v, 2000v+ | Catastrophic at 75-150v, OK at 200-250v | Catastrophic except 100v, 250v, 2000v |

**Explanation**: Fixed-degree graphs have a uniform structure but random connectivity. The catastrophic PFP failures appear to correlate with graph structure rather than size—2000v works fine but 1500v and 2500v fail.

### Random Graphs

| Metric | Phase 1 | Phase 2 | Phase 3 |
|--------|---------|---------|---------|
| **Winner** | PFP (often) | Erratic | PFP (600-1250v) |
| **FF/SFF ratio** | 1.22-1.94x | 0.78-1.16x | 0.99-2.06x |
| **PFP behavior** | Wins at 200-600v, 1250-1500v; fails at 800-1000v | Wins at 100v, 250v; fails at 150-200v | Wins at 600-1250v; fails at 1500v |

**Explanation**: Random graphs favor PFP more than other types because the unstructured connectivity allows push operations to find efficient paths. However, the erratic failures suggest certain random configurations trigger pathological behavior.

---

## Key Patterns Explained

### 1. Why SFF Is So Consistent

**Observation**: SFF never catastrophically fails and shows minimal sensitivity to density or capacity changes.

**Explanation**: The capacity scaling technique ensures that each phase finds "large" augmenting paths before moving to smaller ones. This bounds the number of phases to O(log C) and makes the algorithm inherently adaptive to the graph structure.

### 2. Why FF Benefits Dramatically from Low Capacity

**Observation**: FF achieves 6-23x speedup when C drops from 1000 to 10.

**Theoretical Expectation**: 100x speedup (100/1 capacity ratio)

**Explanation**: The discrepancy comes from:

- **BFS overhead**: Finding paths takes O(m) regardless of flow sent
- **Constant factors**: Path setup, residual updates dominate for small flows
- **Path count**: With C=10, max flow ~200-4000; with C=1000, max flow ~10,000-400,000. The ratio of max flows is only 50-100x, not 100x.

### 3. Why PFP Is Unpredictable

**Observation**: PFP can be fastest (3x over SFF) or slowest (1000x over SFF) on similar-sized graphs.

**Explanation**: The push-relabel algorithm's performance depends heavily on:

- **Height distribution**: If heights become skewed, many useless pushes occur
- **Excess distribution**: Flow can get "trapped" at intermediate nodes
- **Graph structure**: Bipartite and fixed-degree graphs create bottlenecks

Our implementation uses basic FIFO discharge without:

- Global relabeling heuristic
- Gap heuristic
- Highest-label selection

These optimizations can reduce O(n²m) to O(n²√m) or better in practice.

### 4. Why Mesh Graphs Are Special

**Observation**: FF beats SFF on mesh graphs with low capacity, but PFP is always terrible.

**Explanation**:

- **High n, low m**: Mesh has n = rows × cols vertices but only ~2n edges
- **FF advantage**: BFS naturally finds short source→sink paths in grid structure
- **SFF advantage negated**: With C=10, log C ≈ 3.3, minimal scaling benefit
- **PFP disaster**: O(n²m) becomes O(n³) effectively, while FF is O(mC) = O(nC)

---

## Theoretical vs Practical Complexity

| Algorithm | Theoretical | Practical Observation |
|-----------|-------------|----------------------|
| **FF** | O(mC) | Matches theory; C dominates performance |
| **SFF** | O(m² log C) | Matches theory; consistent across conditions |
| **PFP** | O(n²m) | **High variance**; often approaches worst-case bound |

**Note on Big-O**: The O(n²m) bound for PFP is an absolute upper limit that cannot be violated. However, big-O hides constant factors—the same O(n²m) algorithm can run with a constant of 0.001 or 1000. PFP's "catastrophic" cases aren't exceeding the bound; they're hitting it with a large constant, while SFF and FF consistently run near their average case with small constants.

### The Complexity Reality Check

| Algorithm | Phase 1 (C=1000) Mesh 100×100 | Phase 3 (C=10) Mesh 100×100 | Speedup |
|-----------|------------------------------|----------------------------|---------|
| **FF** | 0.75s | 0.55s | 1.4x |
| **SFF** | 0.58s | 0.62s | ~same |
| **PFP** | 12.7s | 13.1s | ~same |

- **FF**: Should see 100x speedup but only gets 1.4x because the mesh has low max flow (100,000 → 1,000)
- **SFF**: log(1000) ≈ 10, log(10) ≈ 3.3, so expected ~3x speedup; seeing ~same due to overhead
- **PFP**: Independent of C; confirmed

---

## The Preflow-Push Mystery

### Understanding the Variance

PFP's erratic behavior doesn't violate its O(n²m) bound—it reflects **high variance in the constant factor**. The same algorithm can run with an effective constant of 0.0001 on "friendly" graphs or 0.01 on "hostile" graphs—a 100x difference while both remain O(n²m).

### Observed Anomalies

| Graph | Expected | Actual | Implied Constant |
|-------|----------|--------|------------------|
| Bipartite 500×500 (Phase 1) | Near worst-case | 0.9s (fastest!) | Very small |
| Bipartite 600×600 (Phase 3) | Near worst-case | 0.98s (fastest!) | Very small |
| FixedDegree 2000v (Phase 3) | Near worst-case | 0.28s (fast) | Very small |
| Random 1250v (Phase 1) | Near worst-case | 1.26s (fastest!) | Very small |

Compare to "catastrophic" cases on similar graphs where the constant is 100-1000x larger.

### Why Such High Variance?

1. **Lucky graph structure**: Some graphs allow excess flow to drain efficiently without getting trapped
2. **Height distribution**: Favorable initial conditions minimize relabel operations
3. **FIFO queue effects**: Discharge order accidentally optimizes some cases
4. **Missing heuristics**: Production implementations use gap/global-relabeling to reduce variance

### Recommendation

**Never use PFP without testing on your specific graph instances.** The algorithm always runs within O(n²m), but the constant factor varies by 100-1000x depending on graph structure. Without advanced heuristics, this variance makes PFP unreliable.

---

## Final Recommendations

### Decision Matrix

| Scenario | Recommended Algorithm | Confidence |
|----------|----------------------|------------|
| **Unknown graph type** | SFF | ⭐⭐⭐⭐⭐ High |
| **Mesh/grid graphs, low C** | FF | ⭐⭐⭐⭐⭐ High |
| **Mesh/grid graphs, high C** | SFF | ⭐⭐⭐⭐ High |
| **Dense random graphs** | Try PFP, fall back to SFF | ⭐⭐⭐ Medium |
| **Bipartite graphs** | SFF | ⭐⭐⭐⭐⭐ High |
| **Need predictability** | SFF or FF | ⭐⭐⭐⭐⭐ High |
| **Need absolute fastest** | Test all three | ⭐⭐⭐⭐ High |

### Algorithm Selection Flowchart

```
Is capacity C known?
├── C ≤ 100
│   ├── Is graph a mesh/grid? → Use FF
│   └── Otherwise → Use SFF
├── C > 100
│   └── Use SFF
└── Unknown C
    └── Use SFF
```

### Production Recommendations

1. **Default to Scaling Ford-Fulkerson**
   - Never catastrophically fails
   - Consistently good performance
   - Resistant to density and capacity variations

2. **Use Ford-Fulkerson for mesh graphs with known low capacity**
   - Clear winner in this specific scenario
   - Simpler to implement than SFF

3. **Avoid Preflow-Push in production**
   - Unpredictable performance
   - Catastrophic failures are common
   - Only consider with advanced heuristics (gap, global relabeling)

4. **If you must use Preflow-Push**
   - Implement global relabeling heuristic
   - Add gap heuristic
   - Use highest-label selection instead of FIFO
   - Test exhaustively on representative graphs

---

## Summary Statistics Across All Phases

### Win Counts by Algorithm

| Algorithm | Phase 1 | Phase 2 | Phase 3 | Total |
|-----------|---------|---------|---------|-------|
| **FF** | 2/32 | 8/23 | 9/32 | 19/87 (22%) |
| **SFF** | 20/32 | 10/23 | 16/32 | 46/87 (53%) |
| **PFP** | 10/32 | 5/23 | 7/32 | 22/87 (25%) |

*Note: PFP's 25% win rate masks the fact that it also has 30+ catastrophic failures*

### Catastrophic Failure Counts (>10x slower than best)

| Algorithm | Phase 1 | Phase 2 | Phase 3 | Total |
|-----------|---------|---------|---------|-------|
| **FF** | 0 | 0 | 0 | 0 |
| **SFF** | 0 | 0 | 0 | 0 |
| **PFP** | 12 | 10+ | 12 | 34+ |

### The Verdict

**Scaling Ford-Fulkerson wins for reliability. Ford-Fulkerson wins for simplicity with low capacity. Preflow-Push has extreme constant-factor variance without proper heuristics, making it unreliable for production use.**

---

## Appendix: Complexity Reference

| Algorithm | Time Complexity | Space | Variance | Best For |
|-----------|-----------------|-------|----------|----------|
| **Ford-Fulkerson** | O(mC) | O(n + m) | Low | Low capacity, simple graphs |
| **Scaling Ford-Fulkerson** | O(m² log C) | O(n + m) | Low | General use, high capacity |
| **Preflow-Push** | O(n²m) | O(n + m) | **Very High** | Dense graphs (with heuristics) |

Where:

- n = number of vertices
- m = number of edges
- C = maximum edge capacity

**Important**: All algorithms run within their stated bounds. "Variance" refers to how much the constant factor varies between best-case and worst-case graph structures. High variance means unpredictable performance even though the asymptotic bound is never violated.
