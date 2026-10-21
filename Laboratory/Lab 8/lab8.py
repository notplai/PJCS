import glob
import os
import sys


def bruteForce(exc: list[float], /) -> tuple[float, int, int] | None:
    """O(n^2): try every (buy, sell) pair with buy < sell."""
    best = None  # (profit, buy, sell)
    for i in range(len(exc)): # buy day
        for j in range(i + 1, len(exc)): # sell day
            p = exc[j] - exc[i] # profit
            if best is None or p > best[0]: best = (p, i, j)
    return best

def divideNconquer(exc: list[float], lo: int, hi: int, /) -> tuple[float, int, int] | None:
    """O(n log n): best (profit, buy, sell) with lo <= buy < sell <= hi."""
    if lo >= hi: return None
    mid = (lo + hi) // 2
    l, r = divideNconquer(exc, lo, mid), divideNconquer(exc, mid + 1, hi)

    # Crossing case: buy at the cheapest day in the left half,
    # sell at the most expensive day in the right half.
    buy = min(range(lo, mid + 1), key=lambda k: (exc[k], k)) # select min from range lo to mid + 1 by using exchange rate as key.
    sell = max(range(mid + 1, hi + 1), key=lambda k: (exc[k], -k))
    cross = (exc[sell] - exc[buy], buy, sell)

    best = cross
    for c in (l, r):
        if c is not None and c[0] > best[0]: best = c
    return best

def main(path: str, /) -> None:
    with open(path) as f: _ = f.read().split()
    n = int(_[0]); a = [float(x) for x in _[1:1 + (n)]]

    if n < 2: return print(1, a[0], 1, a[0], 0, 0, sep="\n")

    dc = divideNconquer(a, 0, n - 1)
    bf = bruteForce(a)

    assert dc is not None and bf is not None
    # Compare on rounded profit to avoid float noise
    assert round(dc[0], 6) == round(bf[0], 6), (dc, bf)

    p, i, j = dc
    print(f"Day: {i + 1} Buy rate : {a[i]:.2f}")
    print(f"Day: {j + 1} Sell rate: {a[j]:.2f}")
    print(f"Profit: {p:.2f}")
    print(f"Day held: {j - 1}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example"
    files = sorted(glob.glob(os.path.join(target, "*.txt"))) if os.path.isdir(target) else [target]
    for path in files: main(path)