import glob, os, sys


# minimum number of coins, with 2-D DP table
INF = float("inf")

# above this many combinations, don't actually enumerate/print them -- the count alone
# can be astronomical (e.g. ~1.17e24 for the 9036-amount/149-coin "extra" case) and plain
# backtracking would never finish walking that many paths.
MAX_WAYS_TO_LIST = 2000

# above this many table cells, skip printing the full grid -- it's still computed
# correctly and used for the answer, just not dumped as unreadable megabytes of text.
MAX_TABLE_CELLS = 20000

# count ways in polynomial time, same recurrence as min_coins but summing instead of min-ing:
#   count[i][j] = count[i-1][j] + count[i][j-coins[i-1]]
# needed because for large inputs the number of ways is astronomically big (e.g. ~1.17e24)
# for the 9036/149-coin "extra" case -- backtracking alone would never finish counting them,
# let alone printing them.
def cways(amount, coins):
    m = len(coins)
    count = [[0] * (amount + 1) for _ in range(m + 1)]
    for i in range(m + 1): count[i][0] = 1
    for i in range(1, m + 1):
        c = coins[i - 1]
        for j in range(1, amount + 1):
            count[i][j] = count[i - 1][j]
            if j >= c: count[i][j] += count[i][j - c]
    return count[m][amount]


# list all ways to make change
# backtrack
def ways(amount: int, coins: list[int]) -> list[str]:
    results = []

    def _(remaining: int, start: int, current: list[int]):
        if remaining == 0:
            results.append(list(current))
            return
        for i in range(start, len(coins)):
            c = coins[i]
            if c > remaining: break  # coins is sorted, nothing further will fit
            current.append(c)
            _(remaining - c, i, current)
            current.pop()

    # Da fucking, it js fuxking set recursion limit.
    # the longest possible combination is all-smallest-coin, amount // min(coins) coins
    # deep -- raise the recursion limit to cover that (restored after) so a valid but
    # deep chain (e.g. large amount, small min coin) doesn't hit RecursionError even
    # when the total number of ways is small enough to be worth listing.
    needed_depth = amount // min(coins) + 100
    old_limit = sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(max(old_limit, needed_depth))
        _(amount, 0, [])
    finally: sys.setrecursionlimit(old_limit)
    return results


def minCoin(amount: int, coins: list[int], /) -> tuple[list[list[float]], float, list[int]]:
    m = len(coins)
    dp = [[INF] * (amount + 1) for _ in range(m + 1)]
    for i in range(m + 1): dp[i][0] = 0

    for i in range(1, m + 1):
        coin = coins[i - 1] # i coins
        for j in range(1, amount + 1): # move j
            dp[i][j] = dp[i - 1][j] # not takes

            # takes
            if j >= coin \
                and dp[i][j - coin] + 1 < dp[i][j]:  # [after use this coins] it using less than [not use]?
                    dp[i][j] = dp[i][j - coin] + 1

    # backtrack to recover one optimal set of coins
    chosen = []
    i, j = m, amount # start at last track
    while i > 0 and j > 0:
        # if above and same as value means it didn't takes this coins. move up!
        if dp[i][j] == dp[i - 1][j]: i -= 1  # coin i-1 not used at this step
        # if not move left side at coins value index
        else:
            chosen.append(coins[i - 1])
            j -= coins[i - 1]  # stay on row i, coin reused

    return dp, dp[m][amount], chosen


def printt(dp: list[list[float]], coins: list[int], amount: int, /) -> None:
    header = "   j:     " + "".join(f"{j:4d}" for j in range(amount + 1))
    print(header)
    for i, row in enumerate(dp):
        label = "i=0 (-)" if i == 0 else f"i={i} ({coins[i-1]})"
        cells = "".join(f"{'INF':>4}" if v == INF else f"{v:4d}" for v in row)
        print(f"{label:>9}:{cells}")


def main(amount: int, coins: list[int], /) -> None:
    print(f"Amount = {amount}")
    print(f"Coins  = {coins}\n")

    # Part 1
    total = cways(amount, coins)
    print(f"Ways to make change = {total}")
    if total <= MAX_WAYS_TO_LIST: print(", ".join("{" + ",".join(map(str, w)) + "}" for w in ways(amount, coins)))
    else: print(f"(too many combinations to list individually -- {total:,} of them)")

    # Part 2
    dp, best, chosen = minCoin(amount, coins)
    if (amount + 1) * (len(coins) + 1) <= MAX_TABLE_CELLS:
        print("\n2-D lookup table (dp[i][j] = min coins to make amount j using first i coins):")
        printt(dp, coins, amount)
    else: print(f"\n(2-D table is {len(coins)+1} x {amount+1} -- too large to print, computed but omitted)")

    if best == INF: print(f"\nAmount {amount} cannot be made with the given coins.")
    else:
        combo = ",".join(map(str, sorted(chosen)))
        print(f"\nThe minimum number of coins is {best}, which is {{{combo}}}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "example"
    files = sorted(glob.glob(os.path.join(target, "*.txt"))) if os.path.isdir(target) else [target]

    for path in files:
        with open(path, 'r') as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip() != ""]
            amount = int(lines[0].strip())
        
            # dedupe + drop non-positive values: a repeated denomination would otherwise make
            # all_ways count the same combination once per duplicate, and a coin <= 0 never
            # shrinks `remaining` in the backtracking search below, which recurses forever.
            coins = sorted({int(x) for x in lines[1].split() if int(x) > 0})

            main(amount, coins)