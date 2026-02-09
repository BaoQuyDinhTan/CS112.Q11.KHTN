import sys
import time
import random
from collections import deque

# Increase recursion depth just in case
sys.setrecursionlimit(5000)

def solve():
    start_time = time.time()
    TIME_LIMIT = 3.8  # Reduced to ensure we exit well before 5s (accounting for I/O overhead)

    # Fast I/O
    input_data = sys.stdin.read().split()
    if not input_data:
        return

    iterator = iter(input_data)
    try:
        N = int(next(iterator))
        M = int(next(iterator))
    except StopIteration:
        return

    adj = [[] for _ in range(N + 1)]
    for _ in range(M):
        u = int(next(iterator))
        v = int(next(iterator))
        adj[u].append(v)
        adj[v].append(u)

    # Check time after I/O
    if time.time() - start_time > TIME_LIMIT:
        print(0)
        return

    # BFS to find shortest distance from every node to N
    # This helps in pruning and heuristic sorting
    dist_to_N = [-1] * (N + 1)
    dist_to_N[N] = 0
    queue = deque([N])
    
    while queue:
        u = queue.popleft()
        for v in adj[u]:
            if dist_to_N[v] == -1:
                dist_to_N[v] = dist_to_N[u] + 1
                queue.append(v)

    if dist_to_N[1] == -1:
        print(0)
        return

    # Global best result
    max_len = -1
    best_path = []
    
    # We will run multiple iterations of DFS with randomization
    iteration_count = 0
    
    while time.time() - start_time < TIME_LIMIT:
        iteration_count += 1
        
        # Local state for this DFS run
        visited = [False] * (N + 1)
        visited[1] = True
        path = [1]
        
        found_better_in_this_iter = False
        
        def dfs(u):
            nonlocal max_len, best_path, found_better_in_this_iter
            
            # Time check
            if (len(path) % 50 == 0) and (time.time() - start_time > TIME_LIMIT):
                return True # Signal to stop

            if u == N:
                if len(path) - 1 > max_len:
                    max_len = len(path) - 1
                    best_path = list(path)
                    found_better_in_this_iter = True
                return False

            # Pruning:
            # 1. If current_len + max_possible_remaining <= max_len, prune.
            if (len(path) - 1) + (N - len(path)) <= max_len:
                return False
            
            neighbors = []
            for v in adj[u]:
                if not visited[v] and dist_to_N[v] != -1:
                    neighbors.append(v)
            
            # Heuristic Sort
            if neighbors:
                # Score: higher dist_to_N is better (detour), plus random noise
                neighbors.sort(key=lambda v: dist_to_N[v] + random.uniform(0, 5), reverse=True)
                
                for v in neighbors:
                    visited[v] = True
                    path.append(v)
                    if dfs(v): return True
                    path.pop()
                    visited[v] = False
            
            return False

        # Run DFS
        dfs(1)
        
        # If we are running out of time, break
        if time.time() - start_time > TIME_LIMIT:
            break

    if max_len != -1:
        print(max_len)
        print(*(best_path))
    else:
        print(0)

if __name__ == "__main__":
    solve()