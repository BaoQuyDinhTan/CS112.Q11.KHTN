import sys
import time
import random

# Increase recursion depth for the Exact Solver (Subtask 1)
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
    # Sort by deadline for standard feasibility checking order
    tasks.sort(key=lambda x: x.t)
    
    global best_profit_exact, best_path_exact
    best_profit_exact = -1
    best_path_exact = []

    def backtrack(idx, current_time, current_profit, current_path):
        global best_profit_exact, best_path_exact
        
        # Base case: checked all tasks
        if idx == N:
            if current_profit > best_profit_exact:
                best_profit_exact = current_profit
                best_path_exact = list(current_path)
            return

        task = tasks[idx]
        
        # Option 1: Include this task (if time permits)
        # Because we sorted by deadline (t), valid subsets can always be 
        # executed in this order.
        if current_time + task.r <= task.t:
            current_path.append(task.id)
            backtrack(idx + 1, current_time + task.r, current_profit + task.p, current_path)
            current_path.pop()

        # Option 2: Skip this task
        backtrack(idx + 1, current_time, current_profit, current_path)

    backtrack(0, 0, 0, [])
    print(best_profit_exact)
    print(*(best_path_exact))

# ---------------------------------------------------------
# SOLVER 2: PORTFOLIO ALNS (N > 20)
# ---------------------------------------------------------
def solve_large(tasks, start_time):
    # 1. DATA TRANSFORMATION
    # ID=0, R=1, T=2, P=3, EFF=4
    task_tuples = []
    for t in tasks:
        # Avoid division by zero
        eff = t.p / t.r if t.r > 0 else 0
        task_tuples.append((t.id, t.r, t.t, t.p, eff))
    
    # 2. HELPER: GENERIC GREEDY BUILDER
    # Takes a sorted list of tasks and builds a valid schedule using linear insertion
    def run_greedy(sorted_list):
        sched = []
        prof = 0
        for task in sorted_list:
            # Linear Insert into sched sorted by Deadline (task[2])
            # This maintains the "EDD" (Earliest Due Date) property for the subset
            pos = len(sched)
            for i, existing in enumerate(sched):
                if task[2] < existing[2]:
                    pos = i
                    break
            sched.insert(pos, task)
            
            # Check Validity
            valid = True
            t_time = 0
            for t in sched:
                t_time += t[1] # r
                if t_time > t[2]: # t (deadline)
                    valid = False
                    break
            
            if valid:
                prof += task[3]
            else:
                sched.pop(pos) # Remove if invalid
        return prof, sched

    # 3. PORTFOLIO INITIALIZATION
    # We create 5 different sorted views of the data.
    # We run the greedy builder on ALL of them and pick the best start.
    strategies = [
        # Strategy 0: Efficiency (Profit / Time)
        sorted(task_tuples, key=lambda x: x[4], reverse=True),
        # Strategy 1: Highest Profit
        sorted(task_tuples, key=lambda x: x[3], reverse=True),
        # Strategy 2: Earliest Deadline
        sorted(task_tuples, key=lambda x: x[2]),
        # Strategy 3: Shortest Job First
        sorted(task_tuples, key=lambda x: x[1]),
        # Strategy 4: Least Slack (Deadline - Duration)
        sorted(task_tuples, key=lambda x: x[2] - x[1])
    ]

    best_profit = -1
    best_sched = []

    # Run Portfolio
    for s_list in strategies:
        p, s = run_greedy(s_list)
        if p > best_profit:
            best_profit = p
            best_sched = list(s)

    # Initialize ALNS with the winner of the portfolio
    current_profit = best_profit
    current_sched = list(best_sched)

    # 4. ALNS LOOP
    # Pools for reconstruction (O(1) lookup)
    all_map = {t[0]: t for t in task_tuples}
    
    # We reuse the sorted lists from our strategies for the "Recreate" phase
    sorted_eff = strategies[0]
    sorted_profit = strategies[1]
    sorted_deadline = strategies[2]
    
    iteration = 0
    # Weights: [Efficiency, Profit, Deadline, Balanced]
    strat_weights = [50, 20, 10, 20] 
    
    while True:
        iteration += 1
        # Time Check
        if iteration % 200 == 0:
            if time.time() - start_time > 4.85: # Safety buffer
                break
        
        # --- RUIN PHASE ---
        # 5% chance to reset to global best
        if random.random() < 0.05:
            work_sched = list(best_sched)
            work_profit = best_profit
        else:
            work_sched = list(current_sched)
            work_profit = current_profit
            
        ln = len(work_sched)
        if ln > 2:
            if random.random() < 0.7:
                # Random Scatter Removal
                cnt = random.randint(3, 12)
                for _ in range(cnt):
                    if not work_sched: break
                    idx = int(random.random() * len(work_sched))
                    rem = work_sched.pop(idx)
                    work_profit -= rem[3]
            else:
                # Burst Removal (Slice)
                cnt = random.randint(3, 15)
                start = int(random.random() * (ln - 2))
                end = min(ln, start + cnt)
                for k in range(start, end):
                    work_profit -= work_sched[k][3]
                del work_sched[start:end]

        # --- RECREATE PHASE ---
        curr_ids = {t[0] for t in work_sched}
        
        # Select Strategy based on weights
        rnd = random.random() * sum(strat_weights)
        strat = 0
        acc = 0
        for i, w in enumerate(strat_weights):
            acc += w
            if rnd <= acc:
                strat = i
                break
        
        candidates = []
        limit = 30 # Optimization: only try top 30 valid candidates
        found = 0
        
        source_list = sorted_eff
        if strat == 1: source_list = sorted_profit
        elif strat == 2: source_list = sorted_deadline
        
        # Filter candidates
        for t in source_list:
            if t[0] not in curr_ids:
                # Randomly skip some good candidates to add variety
                if random.random() < 0.2: continue
                candidates.append(t)
                found += 1
                if found >= limit: break
        
        # Insert candidates
        for cand in candidates:
            # Insert maintaining sorted Deadline order
            pos = len(work_sched)
            cand_t = cand[2]
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

        # --- UPDATE PHASE ---
        if work_profit > best_profit:
            best_profit = work_profit
            best_sched = list(work_sched)
            strat_weights[strat] += 5 # Reward successful strategy
            
            current_profit = work_profit
            current_sched = list(work_sched)
            
        elif work_profit >= current_profit:
            current_profit = work_profit
            current_sched = list(work_sched)
            
        # Simulated Annealing-like acceptance
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

    # Switch logic: Exact solver for small inputs, Heuristic for large
    if N <= 20:
        run_exact_solver(tasks, N)
    else:
        solve_large(tasks, start_time)

if __name__ == "__main__":
    solve()