import glob
import os
import sys
from typing import Any


def main(path: str, /) -> Any:
    with open(path) as f:
        tokens = f.read().split()
    n, m = int(tokens[0]), int(tokens[1])

    graph = [[] for _ in range(n + 1)]
    reverse = [[] for _ in range(n + 1)]
    for i in range(m):
        a, b = int(tokens[2 + 2 * i]), int(tokens[3 + 2 * i])
        graph[a].append(b)
        reverse[b].append(a)

    # Kosaraju pass 1: record vertices by finishing time (iterative DFS)
    visited = [False] * (n + 1)
    order = []
    for s in range(1, n + 1):
        if visited[s]:
            continue
        visited[s] = True
        stack = [(s, 0)]
        while stack:
            u, i = stack.pop()
            if i < len(graph[u]):
                stack.append((u, i + 1))
                v = graph[u][i]
                if not visited[v]:
                    visited[v] = True
                    stack.append((v, 0))
            else:
                order.append(u)

    # Kosaraju pass 2: each DFS on the reversed graph is one SCC
    visited = [False] * (n + 1)
    best = 0
    for s in reversed(order):
        if visited[s]:
            continue
        visited[s] = True
        stack = [s]
        size = 0
        while stack:
            u = stack.pop()
            size += 1
            for v in reverse[u]:
                if not visited[v]:
                    visited[v] = True
                    stack.append(v)
        best = max(best, size)

    print(best)
    return best


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example"
    for path in (
        sorted(glob.glob(os.path.join(target, "*.txt"))) if os.path.isdir(target) else [target]
    ): main(path)