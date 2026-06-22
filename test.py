import glob
import io
import os
import sys
import time

from tsptw import cp, mip, greedy, local_search

STRATEGIES = {
    "Greedy":        lambda nodes, e, l, d, c: greedy(nodes, e, l, d, c, mode=3),
    "Local Search":  lambda nodes, e, l, d, c: local_search(nodes, e, l, d, c),
    "CP-SAT":        lambda nodes, e, l, d, c: cp(nodes, e, l, d, c),
    "MIP (SCIP)":    lambda nodes, e, l, d, c: mip(nodes, e, l, d, c),
    # "ACO Meta":    lambda nodes, e, l, d, c: aco(nodes, e, l, d, c), <-- Adding a new way is this easy!
}

def parse_input_from_string(raw_data):
    inp = raw_data.strip().splitlines()
    if not inp:
        return

    N = int(inp[0])
    nodes = [i for i in range(N + 1)]
    e = [0]      # Node 0 is the depot, so its earliest time is 0
    l = [99999]  # Node 0 is the depot, so its latest time can be set to infinity
    d = [0]      # Node 0 is the depot, so its service time is 0
    c = []

    for i in range(N):
        e_i, l_i, d_i = inp[i + 1].split()
        e.append(int(e_i))
        l.append(int(l_i))
        d.append(int(d_i))

    for i in nodes:
        c.append([int(x) for x in inp[i + N + 1].split()])

    return N, nodes, e, l, d, c

def run_batch_tests():
    file_paths = sorted(glob.glob(os.path.join("test_cases", "*.txt")))
    if not file_paths:
        print("No test files found in 'test_cases/'.")
        return

    algo_names = list(STRATEGIES.keys())
    all_results = []

    print("=" * 60)
    print("PHASE 1: DATA COLLECTION")
    print("=" * 60)

    # --- PHASE 1: Execution and Storage ---
    for path in file_paths:
        file_name = os.path.basename(path)
        
        with open(path, "r") as file:
            file_content = file.read()
        
        original_stdin = sys.stdin
        sys.stdin = io.StringIO(file_content)
        raw_data = sys.stdin.read()
        sys.stdin = original_stdin
        
        n, nodes, e, l, d, c = parse_input_from_string(raw_data)
        
        print(f"Crunching {file_name} (N={n})...")
        
        # Create a dictionary to store the metrics for this specific file
        file_data = {
            "file_name": file_name,
            "n": n,
            "costs": {},
            "times": {}
        }
        
        for name, algo_func in STRATEGIES.items():
            try:
                # Start the high-precision timer
                start_time = time.perf_counter()
                cost, route = algo_func(nodes, e, l, d, c)
                end_time = time.perf_counter()
                
                elapsed = end_time - start_time
                
                if route is None or len(route) == 0 or cost == float('inf'):
                    file_data["costs"][name] = "Infeasible"
                    file_data["times"][name] = f"{elapsed:.4f}"
                else:
                    file_data["costs"][name] = f"{cost:.1f}"
                    file_data["times"][name] = f"{elapsed:.4f}"
                    
            except Exception as err:
                # Catches Out of Memory (OOM) or other solver crashes
                file_data["costs"][name] = "Crash/OOM"
                file_data["times"][name] = "N/A"
                
        all_results.append(file_data)
        
    print("\nEvaluations complete. Generating tables...\n")

    # --- PHASE 2: Table Generation ---
    # Dynamically build the header layout
    header = f"{'File Name':<15} | {'N':<5} | " + " | ".join([f"{name:<12}" for name in algo_names])
    divider = "=" * len(header)
    sub_divider = "-" * len(header)

    # Print Table 1: Solution Costs
    print(divider)
    print("TABLE 1: SOLUTION COSTS".center(len(header)))
    print(divider)
    print(header)
    print(sub_divider)
    for res in all_results:
        row = [f"{res['costs'][name]:<12}" for name in algo_names]
        print(f"{res['file_name']:<15} | {res['n']:<5} | " + " | ".join(row))
    print(divider + "\n")

    # Print Table 2: Computation Times
    print(divider)
    print("TABLE 2: COMPUTATION TIMES (Seconds)".center(len(header)))
    print(divider)
    print(header)
    print(sub_divider)
    for res in all_results:
        row = [f"{res['times'][name]:<12}" for name in algo_names]
        print(f"{res['file_name']:<15} | {res['n']:<5} | " + " | ".join(row))
    print(divider)


if __name__ == "__main__":
    run_batch_tests()