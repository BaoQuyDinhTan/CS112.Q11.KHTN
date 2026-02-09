import random

N = 100000
M = N # N edges
print(f"{N} {M}")

# Chain 1-2-3-...-N with 'different' (type 2)
# 1 is A, 2 is B, 3 is A, 4 is B...
# i is A if i%2 != 0, B if i%2 == 0.

for i in range(1, N):
    print(f"2 {i} {i+1}")

# Add one more edge
# 1 (odd) and 3 (odd) -> Same color.
# Constraint: 1 and 3 DIFFERENT (type 2).
# This should be a CONTRADICTION.
print(f"2 1 3")
