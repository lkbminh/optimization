import os
import glob
import time
import re
import json
from algorithm.cp import CP
from algorithm.mip import MIP
from algorithm.heuristic import LocalSearch


# ==========================================
# 1. IMPORT OR DEFINE YOUR FUNCTIONS HERE
# ==========================================
def my_input_parser(filepath):
   
    with open(filepath, 'r', encoding='utf-8') as f:
        inp = f.readlines()

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

    l[0] = max(l[i] + d[i] + c[i][0] for i in range(1, N + 1))

    return N, e, l, d, c

# ==========================================
# 2. BENCHMARKING LOGIC
# ==========================================
def run_benchmark(folder_path, parser_func, target_func):
    function_name = target_func.__name__
    results = []

    # Find all .inp files
    search_pattern = os.path.join(folder_path, '*.inp')
    inp_files = glob.glob(search_pattern)

    if not inp_files:
        print(f"No '.inp' files found in directory: '{folder_path}'")
        return

    # Sort files naturally (n5 -> n10 -> n100)
    def extract_file_number(filepath):
        filename = os.path.basename(filepath)
        match = re.search(r'n(\d+)\.inp', filename)
        return int(match.group(1)) if match else float('inf')

    inp_files.sort(key=extract_file_number)

    print(f"Found {len(inp_files)} test case(s). Starting benchmark...\n")

    for filepath in inp_files:
        filename = os.path.basename(filepath)
        
        # Extract N 
        match = re.search(r'n(\d+)\.inp', filename)
        
        # Convert N to an integer for cleaner JSON, fallback to string if no match
        n_value = int(match.group(1)) if match else filename 
        
        try:
            N, e, l, d, c = parser_func(filepath)
            
            start_time = time.perf_counter()
            route, cost = target_func(N, e, l, d, c)
            end_time = time.perf_counter()
            
            runtime = end_time - start_time
            
            # Save as a dictionary so it's easy to parse for your LaTeX script
            result_data = {
                "N": n_value,
                "runtime": runtime,
                "cost": cost
            }
            results.append(result_data)
            
            print(f"Processed N={n_value}: Time = {runtime:.6f}s, Cost = {cost}")
            
        except Exception as e:
            print(f"Error processing N='{n_value}' ({filename}): {e}")

    # ==========================================
    # 3. DUMP RESULTS TO JSON
    # ==========================================
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')
    
    os.makedirs(results_dir, exist_ok=True)
    
    # Change extension to .json
    output_filename = f"{function_name}_results.json"
    output_path = os.path.join(results_dir, output_filename)
    
    # Dump the array of dictionaries into the JSON file
    with open(output_path, 'w', encoding='utf-8') as out_file:
        # indent=4 makes the JSON file human-readable and cleanly formatted
        json.dump(results, out_file, indent=4)

    print(f"\nBenchmarking complete. JSON dumped to '{output_path}'.")

if __name__ == '__main__':
    # Set this to the folder containing your .inp files
    TARGET_FOLDER = 'hustack_test_cases'  # Change this to your actual folder path
    run_benchmark(TARGET_FOLDER, my_input_parser, CP)