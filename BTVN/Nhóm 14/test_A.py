import subprocess
import random
import time
import sys

def generate_test_case(N, M):
    edges = set()
    while len(edges) < M:
        u = random.randint(1, N)
        v = random.randint(1, N)
        if u != v and (u, v) not in edges and (v, u) not in edges:
            edges.add((u, v))
    
    input_str = f"{N} {M}\n"
    for u, v in edges:
        input_str += f"{u} {v}\n"
    return input_str

def verify_path(input_str, output_str):
    lines = output_str.strip().split('\n')
    if not lines:
        return False, "No output"
    
    try:
        max_len = int(lines[0])
    except ValueError:
        return False, "Invalid max_len format"

    if max_len == 0:
        return True, "Path length 0 (valid if no path)"

    if len(lines) < 2:
        return False, "Missing path line"
        
    path = list(map(int, lines[1].split()))
    
    if len(path) != max_len + 1:
        return False, f"Path length mismatch: expected {max_len + 1} nodes, got {len(path)}"
    
    # Reconstruct graph to check edges
    input_lines = input_str.split()
    iterator = iter(input_lines)
    N = int(next(iterator))
    M = int(next(iterator))
    adj = [set() for _ in range(N + 1)]
    for _ in range(M):
        u = int(next(iterator))
        v = int(next(iterator))
        adj[u].add(v)
        adj[v].add(u)
        
    # Check connectivity and duplicates
    if len(path) != len(set(path)):
        return False, "Path contains duplicate nodes"
        
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        if v not in adj[u]:
            return False, f"Edge {u}-{v} does not exist"
            
    if path[0] != 1 or path[-1] != N:
        return False, f"Path must start at 1 and end at {N}"

    return True, "Valid path"

def run_test():
    N = 20
    M = 50
    input_data = generate_test_case(N, M)
    
    start_time = time.time()
    process = subprocess.Popen(
        [sys.executable, 'c:/Tai lieu UIT/Phan tich va thiet ke thuat toan/BTVN/Nhóm 14/A.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input=input_data)
    end_time = time.time()
    
    print(f"Execution time: {end_time - start_time:.4f}s")
    print("Output:")
    print(stdout)
    
    if stderr:
        print("Stderr:")
        print(stderr)
        
    valid, message = verify_path(input_data, stdout)
    print(f"Verification: {valid} - {message}")

if __name__ == "__main__":
    run_test()
