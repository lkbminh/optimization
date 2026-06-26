import numpy as np
import sys
import math

def ALNS(N, e, l, d, c, max_no_improvements=100):
    # Convert all inputs to NumPy arrays for C-level speed
    e, l, d, c = map(np.array, (e, l, d, c))
    
    # ---------------------------------------------------------
    # 1. Fast Evaluation
    # ---------------------------------------------------------
    def evaluate_route(route):
        if not route:
            return float('inf')
        
        route = np.concatenate(([0], route, [0]))
        current_time = 0.0
        total_violation = 0.0
        total_travel = 0.0
        
        for i in range(len(route) - 1):
            u, v = route[i], route[i+1]
            arr_time = current_time + d[u] + c[u, v]
            start_time = max(arr_time, e[v])
            
            total_violation += max(0.0, arr_time - l[v])
            total_travel += c[u, v]
            current_time = start_time
            
        return total_travel + total_violation * 1000000

    # ---------------------------------------------------------
    # 2. Vectorized Destroy Operators
    # ---------------------------------------------------------
    def destroy_random(route, q):
        # Numpy random choice without replacement
        removed = np.random.choice(route, q, replace=False).tolist()
        new_route = [x for x in route if x not in removed]
        return new_route, removed

    def destroy_segment(route, q):
        start_idx = np.random.randint(0, max(1, len(route) - q + 1))
        removed = route[start_idx : start_idx + q]
        new_route = route[:start_idx] + route[start_idx + q:]
        return new_route, removed

    def destroy_worst(route, q):
        if not route: return [], []
        
        # 100% Vectorized spatial contribution calculation
        prev_n = np.array([0] + route[:-1])
        curr_n = np.array(route)
        next_n = np.array(route[1:] + [0])
        
        contributions = c[prev_n, curr_n] + c[curr_n, next_n] - c[prev_n, next_n]
        
        # Get indices of the 'q' largest contributions
        worst_indices = np.argsort(contributions)[-q:]
        worst_nodes = set(curr_n[worst_indices])
        
        removed = [x for x in route if x in worst_nodes]
        new_route = [x for x in route if x not in worst_nodes]
        return new_route, removed

    # ---------------------------------------------------------
    # 3. Vectorized Repair Operators
    # ---------------------------------------------------------
    def repair_greedy(route, unassigned):
        for node in unassigned:
            prev_n = np.array([0] + route)
            next_n = np.array(route + [0])
            
            # Vectorized lookup for all insertion points simultaneously
            deltas = c[prev_n, node] + c[node, next_n] - c[prev_n, next_n]
            
            best_idx = np.argmin(deltas)
            route.insert(best_idx, node)
        return route

    def repair_regret_2(route, unassigned):
        while unassigned:
            prev_n = np.array([0] + route)
            next_n = np.array(route + [0])
            U = np.array(unassigned)
            
            # Broadcasting Magic: Calculate distance for ALL unassigned nodes 
            # at ALL possible indices in a single matrix operation.
            # Shape: (len(route) + 1, len(unassigned))
            c_prev_u = c[prev_n[:, None], U[None, :]] 
            c_u_next = c[U[None, :], next_n[:, None]] 
            c_prev_next = c[prev_n, next_n][:, None]
            
            deltas = c_prev_u + c_u_next - c_prev_next
            
            if deltas.shape[0] >= 2:
                # Fast numpy partition to find the 2 smallest values in each column
                sorted_2 = np.partition(deltas, 1, axis=0)[:2, :]
                regrets = sorted_2[1, :] - sorted_2[0, :]
            else:
                regrets = np.zeros(len(U))
                
            best_u_idx = np.argmax(regrets)
            best_node = unassigned[best_u_idx]
            best_insert_idx = np.argmin(deltas[:, best_u_idx])
            
            route.insert(best_insert_idx, best_node)
            unassigned.pop(best_u_idx)
            
        return route

    def repair_random(route, unassigned):
        for node in unassigned:
            insert_idx = np.random.randint(0, len(route) + 1)
            route.insert(insert_idx, node)
        return route

    # ---------------------------------------------------------
    # 4. ALNS Initialization
    # ---------------------------------------------------------
    destroy_ops = [destroy_random, destroy_segment, destroy_worst]
    repair_ops = [repair_greedy, repair_regret_2, repair_random]
    
    # Use numpy arrays for weights
    w_d = np.ones(len(destroy_ops))
    w_r = np.ones(len(repair_ops))

    # Initial greedy sorting by earliest deadline
    current_route = sorted(range(1, N + 1), key=lambda x: e[x])
    current_cost = evaluate_route(current_route)
    
    best_route, best_cost = current_route[:], current_cost
    
    T = 10000.0
    cooling_rate = 0.995
    q_size = max(5, int(N * 0.15))
    not_improved = 0
    
    SCORE_GLOBAL_BEST = 33
    SCORE_IMPROVED = 9
    SCORE_ACCEPTED = 13
    DECAY = 0.8

    # ---------------------------------------------------------
    # 5. Main Loop
    # ---------------------------------------------------------
    while not_improved < max_no_improvements:
        # Numpy probability distribution selection
        p_d = w_d / w_d.sum()
        p_r = w_r / w_r.sum()
        
        d_idx = np.random.choice(len(destroy_ops), p=p_d)
        r_idx = np.random.choice(len(repair_ops), p=p_r)

        temp_route, removed_nodes = destroy_ops[d_idx](current_route[:], q_size)
        new_route = repair_ops[r_idx](temp_route, removed_nodes)
        new_cost = evaluate_route(new_route)

        score = 0
        if new_cost < best_cost:
            best_cost = new_cost
            best_route = new_route[:]
            current_cost = new_cost
            current_route = new_route[:]
            score = SCORE_GLOBAL_BEST
            not_improved = 0
            
        elif new_cost < current_cost:
            current_cost = new_cost
            current_route = new_route[:]   
            score = SCORE_IMPROVED
            not_improved += 1
            
        else:
            acceptance_prob = math.exp(-(new_cost - current_cost) / T)
            if np.random.rand() < acceptance_prob:            
                current_cost = new_cost
                current_route = new_route[:]
                score = SCORE_ACCEPTED
            not_improved += 1

        w_d[d_idx] = w_d[d_idx] * DECAY + score * (1 - DECAY)
        w_r[r_idx] = w_r[r_idx] * DECAY + score * (1 - DECAY)
        
        T *= cooling_rate

    return best_route, best_cost

# ---------------------------------------------------------
# aco.py Style Main Function
# ---------------------------------------------------------
def main():
    inp = sys.stdin.read().strip().splitlines()
    if not inp:
        return

    N = int(inp[0])
    e, l, d = [0], [999999999], [0]
    c = []

    for i in range(N):
        e_i, l_i, d_i = inp[i + 1].split()
        e.append(int(e_i))
        l.append(int(l_i))
        d.append(int(d_i))

    for i in range(N + 1):
        c.append([int(x) for x in inp[i + N + 1].split()])

    # Dynamically adjust l[0] based on furthest possible return trip
    l[0] = max(l[i] + d[i] + c[i][0] for i in range(1, N + 1))

    # Run the solver
    route, cost = ALNS(N, e, l, d, c, max_no_improvements=100)
    
    print(N)
    if route is not None:
        print(*(route))

if __name__ == "__main__":
    main()