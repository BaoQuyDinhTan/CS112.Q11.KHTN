import sys

sys.setrecursionlimit(2000)

def solve():
    input_data = sys.stdin.read().split()
    if not input_data: return
    iterator = iter(input_data)
    
    try:
        n = int(next(iterator))
        m = int(next(iterator))
    except StopIteration: return

    limit = 2 * n + 1
    
    adj = [[] for _ in range(limit)]
    
    for _ in range(m):
        t = int(next(iterator))
        u = int(next(iterator))
        v = int(next(iterator))
        
        not_u = u + n if u <= n else u - n
        not_v = v + n if v <= n else v - n
        
        if t == 2:
            adj[not_u].append(v)
            adj[not_v].append(u)
            adj[u].append(not_v)
            adj[v].append(not_u)
        else:
            adj[u].append(v)
            adj[not_v].append(not_u)
            adj[not_u].append(not_v)
            adj[v].append(u)

    
    ids = [0] * limit     
    low = [0] * limit     
    num = [0] * limit     
    on_stack = [False] * limit
    
    st = []               
    work = []             
    
    ptr = [0] * limit 
    
    timer = 0
    scc_count = 0

    for start_node in range(1, limit):
        if num[start_node]: 
            continue
            
        work.append(start_node)
        
        while work:
            u = work[-1] 
            
            if num[u] == 0:
                timer += 1
                num[u] = low[u] = timer
                st.append(u)
                on_stack[u] = True
            
            found_new_child = False

            while ptr[u] < len(adj[u]):
                v = adj[u][ptr[u]]
                ptr[u] += 1 
                
                if num[v] == 0:
                    work.append(v)
                    found_new_child = True
                    break
                elif on_stack[v]:
                    if num[v] < low[u]:
                        low[u] = num[v]
            
            if found_new_child:
                continue

            work.pop()
            
            if work:
                parent = work[-1]
                if low[u] < low[parent]:
                    low[parent] = low[u]
            
            if low[u] == num[u]:
                scc_count += 1
                while True:
                    node = st.pop()
                    on_stack[node] = False
                    ids[node] = scc_count
                    if node == u:
                        break

    answer = True
    for i in range(1, n + 1):
        if ids[i] == ids[i + n]:
            answer = False
            break
            
    sys.stdout.write("YES" if not answer else "NO")

if __name__ == '__main__':
    solve()