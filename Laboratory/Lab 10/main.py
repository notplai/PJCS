import glob
import os
import sys


def main(path: str, /) -> list[int]:
    with open(path) as f: tokens = f.read().split()
    n, m, c = int(tokens[0]), int(tokens[1]), int(tokens[2])

    # need[i] = number of people country i still has room for (1-indexed)
    need = [0] + [int(x) for x in tokens[3:3 + n]]

    graph = [[] for _ in range(n + 1)]
    edges = []
    base = 3 + n
    for i in range(m):
        a, b, w = (int(x) for x in tokens[base + 3 * i:base + 3 * i + 3])
        graph[a].append(b)
        edges.append((a, b, w))  # one-way road a -> b
    k = int(tokens[base + 3 * m])

    # Bellman-Ford from country 1: road costs may be negative, so `Dijkstra` is not valid here.
    INF = float("inf")
    dist = [INF] * (n + 1)
    dist[1] = 0
    for _ in range(n - 1):
        changed = False
        for a, b, w in edges:
            if dist[a] + w < dist[b]:
                dist[b] = dist[a] + w
                changed = True
        if not changed: break

    # An edge that still relaxes lies on / behind a negative cycle. Every
    # country reachable from it has no minimum travel cost, so nobody can be
    # assigned there.
    unbounded = [False] * (n + 1)
    stack = [b for a, b, w in edges if dist[a] + w < dist[b]]
    while stack:
        u = stack.pop()
        if unbounded[u]: continue
        unbounded[u] = True
        stack.extend(graph[u])

    # Fill countries in increasing order of distance: this gives the cheapest
    # assignment for person 1, 2, ..., K in order.
    costs = []
    for d, u in sorted(
        (dist[u], u) for u in range(1, n + 1) if dist[u] < INF and not unbounded[u]
    ):
        if len(costs) >= k: break
        costs.extend([d + c] * min(need[u], k - len(costs)))

    # Every usable country is full: the remaining people cannot be placed.
    costs.extend([-1] * (k - len(costs)))

    print("\n".join(map(str, costs)))
    return costs


if __name__ == "__main__":
    workdir = sys.argv[1] if len(sys.argv) > 1 else "example"
    for path in (
        sorted(glob.glob(os.path.join(workdir, "*.txt"))) if os.path.isdir(workdir) else [workdir]
    ): main(path)
