import sys
import time
import random
import math

# Increase recursion depth for Subtask 1
sys.setrecursionlimit(5000)

class Task:
    def __init__(self, id, r, t, p):
        self.id = id
        self.r = r
        self.t = t
        self.p = p

# ---------------------------------------------------------
# SOLVER 1: EXACT BACKTRACKING (N <= 20)
# ---------------------------------------------------------
best_profit_exact = -1
best_path_exact = []

def run_exact_solver(tasks, N):
    tasks.sort(key=lambda x: x.t)
    global best_profit_exact, best_path_exact
    best_profit_exact = -1
    best_path_exact = []

    def backtrack(idx, current_time, current_profit, current_path):
        global best_profit_exact, best_path_exact
        if idx == N:
            if current_profit > best_profit_exact:
                best_profit_exact = current_profit
                best_path_exact = list(current_path)
            return

        task = tasks[idx]
        if current_time + task.r <= task.t:
            current_path.append(task.id)
            backtrack(idx + 1, current_time + task.r, current_profit + task.p, current_path)
            current_path.pop()

        backtrack(idx + 1, current_time, current_profit, current_path)

    backtrack(0, 0, 0, [])
    print(best_profit_exact)
    print(*(best_path_exact))

# ---------------------------------------------------------
# SOLVER 2: HIGH-PERFORMANCE ALNS (N > 20)
# ---------------------------------------------------------
def solve_large(tasks, start_time):
    # 1. DATA TRANSFORMATION (Speed Hack)
    # Convert objects to simple tuples: (id, r, t, p, eff)
    # We work with these tuples exclusively in the loop for speed.
    
    # ID=0, R=1, T=2, P=3, EFF=4
    task_tuples = []
    for t in tasks:
        eff = t.p / t.r if t.r > 0 else 0
        task_tuples.append((t.id, t.r, t.t, t.p, eff))
    
    # Pre-calculate sorting lists to avoid repeated sorting
    # Sorted by Efficiency
    sorted_eff = sorted(task_tuples, key=lambda x: x[4], reverse=True)
    # Sorted by Profit
    sorted_profit = sorted(task_tuples, key=lambda x: x[3], reverse=True)
    # Sorted by Deadline (ascending) - Needed for output validity
    sorted_deadline = sorted(task_tuples, key=lambda x: x[2])
    
    # Initial Solution: Efficiency Greedy
    current_sched = []
    current_profit = 0
    
    # Fast Greedy Construction
    for task in sorted_eff:
        # Linear Insert
        # Since we use tuples, accessing task[2] (deadline) is fast
        pos = len(current_sched)
        for i, existing in enumerate(current_sched):
            if task[2] < existing[2]:
                pos = i
                break
        current_sched.insert(pos, task)
        
        # Check Validity inline
        valid = True
        t_time = 0
        for t in current_sched:
            t_time += t[1] # t.r
            if t_time > t[2]: # t.t
                valid = False
                break
        
        if valid:
            current_profit += task[3]
        else:
            current_sched.pop(pos)

    # Global State
    best_profit = current_profit
    best_sched = list(current_sched)
    
    # Pools for reconstruction
    # We maintain a set of IDs for O(1) lookup
    all_map = {t[0]: t for t in task_tuples}
    
    iteration = 0
    
    # Weights for adaptive selection
    # [Efficiency, Profit, Duration, Balanced]
    strat_weights = [50, 20, 10, 20]
    
    while True:
        iteration += 1
        # Check time less often to save overhead (every 200 iters)
        if iteration % 200 == 0:
            if time.time() - start_time > 4.85:
                break
        
        # --- RUIN ---
        # 30% chance to restart from best
        if random.random() < 0.3:
            work_sched = list(best_sched)
            work_profit = best_profit
        else:
            work_sched = list(current_sched)
            work_profit = current_profit
            
        # Removal logic
        # Optimize: Avoid random.choice overhead. Use direct index.
        ln = len(work_sched)
        if ln > 2:
            # 70% Random Scatter, 30% Burst
            if random.random() < 0.7:
                # Random Scatter removal (3 to 12 items)
                cnt = random.randint(3, 12)
                for _ in range(cnt):
                    if not work_sched: break
                    idx = int(random.random() * len(work_sched))
                    rem = work_sched.pop(idx)
                    work_profit -= rem[3]
            else:
                # Burst removal (Slice)
                cnt = random.randint(3, 15)
                start = int(random.random() * (ln - 2))
                end = min(ln, start + cnt)
                # Calculate profit loss efficiently
                for k in range(start, end):
                    work_profit -= work_sched[k][3]
                del work_sched[start:end]

        # --- RECREATE ---
        # Identify current IDs
        curr_ids = {t[0] for t in work_sched}
        
        # Strategy Select
        rnd = random.random() * sum(strat_weights)
        strat = 0
        acc = 0
        for i, w in enumerate(strat_weights):
            acc += w
            if rnd <= acc:
                strat = i
                break
        
        # Candidate Selection
        # Instead of sorting fresh every time (slow), use pre-sorted lists and filter
        # Only take top K valid candidates to speed up
        
        candidates = []
        limit = 30 # Only try inserting top 30 candidates
        found = 0
        
        source_list = sorted_eff # Default
        if strat == 1: source_list = sorted_profit
        elif strat == 2: source_list = sorted_deadline # Proxy for duration/earliness
        
        # Add some randomization to the source list traversal?
        # A full shuffle is too slow. 
        # We skip items with probability to simulate randomness.
        
        for t in source_list:
            if t[0] not in curr_ids:
                # 20% chance to skip good candidate to allow variety
                if random.random() < 0.2: continue
                
                candidates.append(t)
                found += 1
                if found >= limit: break
        
        # Insertion Loop
        for cand in candidates:
            # Insert maintaining sorted order (Deadline)
            # Binary search is faster than linear scan for larger lists? 
            # N is small (500), linear is fine, but let's optimize.
            # Just scan.
            
            pos = len(work_sched)
            cand_t = cand[2]
            
            # Fast scan
            for i, existing in enumerate(work_sched):
                if cand_t < existing[2]:
                    pos = i
                    break
            
            work_sched.insert(pos, cand)
            
            # Inline Validity Check
            valid = True
            acc_time = 0
            for t in work_sched:
                acc_time += t[1]
                if acc_time > t[2]:
                    valid = False
                    break
            
            if valid:
                work_profit += cand[3]
            else:
                work_sched.pop(pos)

        # --- UPDATE ---
        if work_profit > best_profit:
            best_profit = work_profit
            best_sched = list(work_sched)
            
            # Reward strategy
            strat_weights[strat] += 5
            
            current_profit = work_profit
            current_sched = list(work_sched)
            
        elif work_profit >= current_profit:
            current_profit = work_profit
            current_sched = list(work_sched)
        
        # Late game catch: if we are close to global best, accept it sometimes
        elif work_profit > best_profit * 0.99 and random.random() < 0.05:
             current_profit = work_profit
             current_sched = list(work_sched)

    print(best_profit)
    print(*(t[0] for t in best_sched))

# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
def solve():
    start_time = time.time()
    try:
        input_data = sys.stdin.read().split()
    except Exception: return
    if not input_data: return

    iterator = iter(input_data)
    try:
        N = int(next(iterator))
    except StopIteration: return

    tasks = []
    for i in range(1, N + 1):
        r = int(next(iterator))  
        t = int(next(iterator))
        p = int(next(iterator))
        tasks.append(Task(i, r, t, p))
   
    if N <= 20:
        run_exact_solver(tasks, N)
    else:
        solve_large(tasks, start_time)

if __name__ == "__main__":
    solve()