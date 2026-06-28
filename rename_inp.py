import os
import glob
import time
import re

# ==========================================
# 1. IMPORT OR DEFINE YOUR FUNCTIONS HERE
# ==========================================
def my_input_parser(filepath):
    """
    Replace this with your actual parsing logic.
    Reads the .inp file and returns the data needed for the target function.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()

def my_algorithm(parsed_data):
    """
    Replace this with your actual function.
    Takes the parsed input, runs the logic, and returns the cost.
    """
    time.sleep(0.05) 
    return 142  

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

    # Sort files naturally (n5 -> n10 -> n100) instead of alphabetically
    def extract_file_number(filepath):
        filename = os.path.basename(filepath)
        # Look for the number between 'n' and '.inp'
        match = re.search(r'n(\d+)\.inp', filename)
        # If it finds a number, return it as an integer for proper sorting
        # If no number is found (e.g., test.inp), send it to the back
        return int(match.group(1)) if match else float('inf')

    inp_files.sort(key=extract_file_number)

    print(f"Found {len(inp_files)} test case(s). Starting benchmark...\n")

    for filepath in inp_files:
        filename = os.path.basename(filepath)
        
        try:
            parsed_input = parser_func(filepath)
            
            start_time = time.perf_counter()
            cost = target_func(parsed_input)
            end_time = time.perf_counter()
            
            runtime = end_time - start_time
            
            # Removed function_name from the tuple
            result_tuple = (filename, runtime, cost)
            results.append(result_tuple)
            
            print(f"Processed {filename}: Time = {runtime:.6f}s, Cost = {cost}")
            
        except Exception as e:
            print(f"Error processing '{filename}': {e}")

    # ==========================================
    # 3. WRITE RESULTS TO 'results' FOLDER NEXT TO SCRIPT
    # ==========================================
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(script_dir, 'results')
    
    os.makedirs(results_dir, exist_ok=True)
    
    output_filename = f"{function_name}_results.out"
    output_path = os.path.join(results_dir, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as out_file:
        # Adjusted header to remove Function Name
        out_file.write("File | Runtime (s) | Cost\n")
        out_file.write("-" * 40 + "\n")
        
        for res in results:
            # res[0] = filename, res[1] = runtime, res[2] = cost
            out_file.write(f"{res[0]} | {res[1]:.6f} | {res[2]}\n")

    print(f"\nBenchmarking complete. All tuples saved to '{output_path}'.")


if __name__ == '__main__':
    TARGET_FOLDER = '.' 
    
    run_benchmark(TARGET_FOLDER, my_input_parser, my_algorithm)