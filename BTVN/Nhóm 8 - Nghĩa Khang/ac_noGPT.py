import sys
import random
import time
from typing import List, Tuple

INF = 10 ** 9


def read_input() -> Tuple[int, int, int, List[Tuple[int, int, int]]]:
    data = sys.stdin.read().strip().split()
    if not data:
        return 0, 0, 0, []
    it = iter(data)
    n = int(next(it))
    m = int(next(it))
    r = int(next(it))
    sensors = []
    for _ in range(m):
        x = int(next(it))
        y = int(next(it))
        c = int(next(it))
        sensors.append((x, y, c))
    return n, m, r, sensors


class Solver:
    def __init__(self, n: int, m: int, r: int, sensors: List[Tuple[int, int, int]]):
        self.n = n
        self.m = m
        self.r = r
        self.sensors = [(0, 0, 0)] + sensors  # 1-index
        self.pref = [[0] * (n + 2) for _ in range(n + 2)]
        self.cover_sets: List[List[Tuple[int, int]]] = [[] for _ in range(m + 1)]
        for idx in range(1, m + 1):
            x, y, _ = self.sensors[idx]
            for cx in range(max(1, x - r), min(n, x + r) + 1):
                for cy in range(max(1, y - r), min(n, y + r) + 1):
                    self.cover_sets[idx].append((cx, cy))
        self.rng = random.Random(time.time_ns())

    def reset_pref(self) -> None:
        for i in range(1, self.n + 1):
            row = self.pref[i]
            for j in range(1, self.n + 1):
                row[j] = 0

    def trau(self) -> Tuple[int, List[int]]:
        n = self.n
        m = self.m
        r = self.r
        diff = [[0] * (n + 3) for _ in range(n + 3)]
        grid = [[0] * (n + 3) for _ in range(n + 3)]
        best_cost = INF
        best_choice: List[int] = []
        for mask in range(1 << m):
            cost = 0
            choice = []
            for i in range(1, m + 1):
                if mask >> (i - 1) & 1:
                    cost += self.sensors[i][2]
                    choice.append(i)
            if cost >= best_cost:
                continue
            for idx in choice:
                x, y, _ = self.sensors[idx]
                x1 = max(1, x - r)
                x2 = min(n, x + r)
                y1 = max(1, y - r)
                y2 = min(n, y + r)
                diff[x1][y1] += 1
                diff[x1][y2 + 1] -= 1
                diff[x2 + 1][y1] -= 1
                diff[x2 + 1][y2 + 1] += 1
            ok = True
            for i in range(1, n + 1):
                running = 0
                for j in range(1, n + 1):
                    running += diff[i][j]
                    grid[i][j] = grid[i - 1][j] + running
                    if grid[i][j] == 0:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                best_cost = cost
                best_choice = choice[:]
            for i in range(1, n + 2):
                for j in range(1, n + 2):
                    diff[i][j] = 0
                    grid[i][j] = 0
        return best_cost, best_choice

    def best_ratio(self, trick_lord: bool = False) -> Tuple[int, List[int]]:
        self.reset_pref()
        n = self.n
        pref = self.pref
        ans = 0
        ans_set = set()

        unused = set()
        for i in range(1, self.m + 1):
            if trick_lord:
                if self.rng.randint(0, 2):
                    unused.add(i)
            else:
                unused.add(i)

        num_uncovered = n * n
        while num_uncovered > 0:
            best_id = -1
            best_gain = 0
            for idx in unused:
                gain = 0
                for x, y in self.cover_sets[idx]:
                    if pref[x][y] == 0:
                        gain += 1
                if best_id == -1 or self.sensors[best_id][2] * gain > self.sensors[idx][2] * best_gain:
                    best_id = idx
                    best_gain = gain
            if best_id == -1 or best_gain == 0:
                self.reset_pref()
                return INF, []
            for x, y in self.cover_sets[best_id]:
                pref[x][y] += 1
            num_uncovered -= best_gain
            ans += self.sensors[best_id][2]
            ans_set.add(best_id)
            unused.discard(best_id)

        drop_delta = [[0] * (n + 2) for _ in range(n + 2)]

        def try_drop(group: List[int]) -> bool:
            touched = []
            for idx in group:
                for x, y in self.cover_sets[idx]:
                    if drop_delta[x][y] == 0:
                        touched.append((x, y))
                    drop_delta[x][y] += 1
            ok = True
            for x, y in touched:
                if pref[x][y] - drop_delta[x][y] <= 0:
                    ok = False
                    break
            if ok:
                for x, y in touched:
                    pref[x][y] -= drop_delta[x][y]
            for x, y in touched:
                drop_delta[x][y] = 0
            return ok

        improved = True
        while improved:
            improved = False
            for idx in sorted(ans_set):
                if try_drop([idx]):
                    ans -= self.sensors[idx][2]
                    ans_set.remove(idx)
                    improved = True
                if improved:
                    break

        result = sorted(ans_set)
        self.reset_pref()
        return ans, result

    def solve(self) -> Tuple[int, List[int]]:
        best_cost, best_choice = self.best_ratio(False)
        # if max(self.n, self.m) <= 20:
        #     best_cost, best_choice = self.trau()
        # else:
        for _ in range(80):
            cand_cost, cand_choice = self.best_ratio(True)
            if cand_cost < best_cost:
                best_cost, best_choice = cand_cost, cand_choice
        return best_cost, best_choice


def main() -> None:
    n, m, r, sensors = read_input()
    if n == 0 and m == 0:
        return
    solver = Solver(n, m, r, sensors)
    cost, choice = solver.solve()
    sys.stdout.write(str(len(choice)) + "\n")
    if choice:
        sys.stdout.write(" ".join(map(str, choice)) + "\n")
    else:
        sys.stdout.write("\n")
    sys.stdout.write(str(cost) + "\n")


if __name__ == "__main__":
    main()
