import sys
from bisect import bisect_left, bisect_right

# Tối ưu hóa I/O
input = sys.stdin.read

def solve():
    # Đọc toàn bộ dữ liệu 1 lần
    data = input().split()
    if not data: return
    iterator = iter(data)
    
    try:
        n = int(next(iterator))
        q = int(next(iterator))
    except StopIteration:
        return

    # 1. Chuẩn bị dữ liệu
    a = [0] * n
    positions = {} # Map lưu vị trí các số: value -> [index1, index2...]
    
    for i in range(n):
        val = int(next(iterator))
        a[i] = val
        if val not in positions:
            positions[val] = []
        positions[val].append(i)

    # 2. Xây dựng Segment Tree (Iterative)
    # Tìm kích thước lũy thừa của 2 để build cây
    size = 1
    while size < n:
        size *= 2
    
    # Mảng lưu Candidate và Count cho thuật toán Boyer-Moore
    tree_cand = [-1] * (2 * size)
    tree_cnt = [0] * (2 * size)
    
    # Init lá (leaves)
    for i in range(n):
        tree_cand[size + i] = a[i]
        tree_cnt[size + i] = 1
        
    # Init các nút cha (internal nodes)
    for i in range(size - 1, 0, -1):
        c1, k1 = tree_cand[2*i], tree_cnt[2*i]
        c2, k2 = tree_cand[2*i+1], tree_cnt[2*i+1]
        
        # Merge logic (Boyer-Moore)
        if c1 == c2:
            tree_cand[i] = c1
            tree_cnt[i] = k1 + k2
        elif k1 > k2:
            tree_cand[i] = c1
            tree_cnt[i] = k1 - k2
        else:
            tree_cand[i] = c2
            tree_cnt[i] = k2 - k1

    results = []
    
    # 3. Xử lý truy vấn
    for _ in range(q):
        l = int(next(iterator)) - 1
        r = int(next(iterator)) - 1
        
        # Segment Tree Query trong khoảng [l, r]
        # Chuyển sang index của cây
        L = l + size
        R = r + size
        
        res_c, res_k = -1, 0
        
        while L <= R:
            if L % 2 == 1:
                # Merge nút L vào kết quả hiện tại
                c_node, k_node = tree_cand[L], tree_cnt[L]
                if res_c == c_node:
                    res_k += k_node
                elif res_k > k_node:
                    res_k -= k_node
                else:
                    res_c = c_node
                    res_k = k_node - res_k
                L += 1
            
            if R % 2 == 0:
                # Merge nút R vào kết quả hiện tại
                c_node, k_node = tree_cand[R], tree_cnt[R]
                if res_c == c_node:
                    res_k += k_node
                elif res_k > k_node:
                    res_k -= k_node
                else:
                    res_c = c_node
                    res_k = k_node - res_k
                R -= 1
            
            L //= 2
            R //= 2
            
        # 4. Kiểm tra ứng viên (Verification)
        candidate = res_c
        found = False
        
        # Nếu count trả về > 0 thì mới có hy vọng, nhưng vẫn phải check
        if candidate != -1: 
            # Check nhanh bằng danh sách vị trí
            if candidate in positions:
                idxs = positions[candidate]
                # Đếm số lượng thực tế trong đoạn [l, r]
                count_real = bisect_right(idxs, r) - bisect_left(idxs, l)
                if count_real > (r - l + 1) // 2:
                    results.append(str(candidate))
                    found = True
        
        if not found:
            results.append("-1")
            
    sys.stdout.write(' '.join(results))

if __name__ == '__main__':
    solve()