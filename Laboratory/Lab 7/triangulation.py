"""
Minimum Cost Polygon Triangulation (Dynamic Programming)

Input file format (see example/1.1.txt):
    n
    x1 y1
    x2 y2
    ...
Usage:
    python3 triangulation.py example/1.1.txt
"""
import glob
import math
import os
import sys
import time
from functools import lru_cache

BRUTE_LIMIT = 16 # brute force grows ~3x per extra vertex; above this it takes too long


def dist(a: tuple[float, float], b: tuple[float, float], /) -> float:
    """Euclidean distance between two points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def perimeter(p: list[tuple[float, float]], i: int, j: int, k: int, /) -> float:
    """Weight of triangle (i, j, k) = sum of its three side lengths."""
    return dist(p[i], p[j]) + dist(p[j], p[k]) + dist(p[i], p[k])

def mintri(p: list[tuple[float, float]], brute: bool | int = 0, /) -> float:
    if not brute:
        """
        Recurrence:
            cost(i, j) = minimum cost to triangulate the sub-polygon made of
                         vertices i, i+1, ..., j
            cost(i, j) = 0                                   if j < i + 2  (fewer than 3 vertices)
            cost(i, j) = min over k in (i+1 .. j-1) of
                         cost(i, k) + cost(k, j) + perimeter(i, k, j)
    
        Idea: the edge (i, j) must belong to exactly one triangle (i, k, j).
        Choosing k splits the polygon into two smaller polygons (i..k) and (k..j),
        which are solved independently -> optimal substructure.
        Answer = cost(0, n-1).
        """
        if (n:=len(p)) < 3: return 0.0
    
        # table[i][j] holds cost(i, j); filled in order of increasing gap (j - i)
        # so that the smaller sub-polygons are always ready before they are needed.
        table = [[0.0] * n for _ in range(n)]
    
        # gap = j - i, smallest polygon is a triangle (gap 2)
        for gap in range(2, n):
            for i in range(n - gap):
                table[i][j:=(i + gap)] = math.inf
    
                # try every apex k for the triangle on edge (i, j)
                for k in range(i + 1, j):
                    c = table[i][k] + table[k][j] + perimeter(p, i, k, j)
                    table[i][j] = min(table[i][j], c)
                    # if c < table[i][j]: table[i][j] = c
    
        return table[0][n - 1]
    else:
        """
        Brute force: the same recurrence WITHOUT remembering results (no table),
        so every sub-problem is recomputed. Exponential time, only for checking
        the DP answer on small inputs.
        """
        # Optimization: compute every pairwise distance ONCE up front, so the
        # recursion only does table lookups instead of calling hypot() each time.
        n = len(p)
        d = [[dist(a, b) for b in p] for a in p]

        def solve(i: int, j: int) -> float:
            if j < i + 2: return 0.0 # n < 3
            dij = d[i][j]
            di, dj = d[i], d[j]
            best = math.inf
            # try all apex vertices k and take the cheapest
            for k in range(i + 1, j):
                c = solve(i, k) + solve(k, j) + di[k] + dj[k] + dij
                best = min(c, best)
            return best

        return solve(0, n - 1)

def main(path: str, /) -> list[tuple[float, float]]:
    """Read n, then n lines of 'x y'."""
    with open(path) as f: tokens = f.read().split()
    n = int(tokens[0])
    nums = list(map(float, tokens[1:1 + 2 * n]))
    return list(zip(nums[0::2], nums[1::2])) # pair up the flat list [x1, y1, x2, y2, ...] -> [(x1, y1), (x2, y2), ...]

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example"
    files = sorted(glob.glob(os.path.join(target, "*.txt"))) if os.path.isdir(target) else [target]
    
    print(f"{'file':<16}{'n':>4}  {'DP result':>10} {'DP time':>10}  {'brute':>10} {'brute time':>9}  check")
    for path in files: 
        """Run DP (and brute force when small) on one file and print a result row."""
        pts = main(path)
        
        t = time.perf_counter(); dp = mintri(pts); t_dp = time.perf_counter() - t # DP run
        if len(pts) <= BRUTE_LIMIT: # BF RUN
            t = time.perf_counter(); bf = mintri(pts, 1); t_bf = time.perf_counter() - t
            bf_s, tbf_s, ok = f"{bf:.4f}", f"{t_bf:.4f}s", "OK" if abs(bf - dp) < 1e-9 else "MISMATCH"
        else: bf_s, tbf_s, ok = "skipped", "-", "-"
        
        print(f"{os.path.basename(path):<16}{len(pts):>4}  {dp:>10.4f} {t_dp:>9.4f}s  {bf_s:>10} {tbf_s:>9}  {ok}")