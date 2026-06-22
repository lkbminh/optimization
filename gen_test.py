import random
import math
import os

def generate_normal_tsptw_test_cases():
    """Sinh test cases vừa và nhỏ: N = 10, 50, 100, ..., 950"""
    output_dir = "generated_test_cases"
    os.makedirs(output_dir, exist_ok=True)
    
    N_values = [10] + [i * 50 for i in range(1, 21)]
    
    for idx, N in enumerate(N_values):
        filename = os.path.join(output_dir, f"test_{idx+1:02d}_N_{N}.txt")
        _write_test_case(filename, N, grid_size=1000)

def generate_large_tsptw_test_cases():
    """Sinh test cases cực lớn: N = 1500, 2000, 2500, ..., 5000"""
    output_dir = "generated_large_test_cases"
    os.makedirs(output_dir, exist_ok=True)
    
    # Sinh giá trị N: 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000
    N_values = [1500 + i * 500 for i in range(8)]
    
    for idx, N in enumerate(N_values):
        filename = os.path.join(output_dir, f"test_large_{idx+1:02d}_N_{N}.txt")
        _write_test_case(filename, N, grid_size=10000)

def _write_test_case(filename, N, grid_size):
    """Hàm lõi để xử lý logic ghi file giúp code không bị lặp lại"""
    with open(filename, 'w') as f:
        # 1. Ghi N (chắc chắn là số nguyên)
        f.write(f"{int(N)}\n")
        
        # 2. Sinh tọa độ nguyên ngẫu nhiên trên lưới (grid_size x grid_size)
        coords = [(random.randint(0, grid_size), random.randint(0, grid_size)) for _ in range(N + 1)]
        
        # 3. Khởi tạo ma trận t
        t = [[0] * (N + 1) for _ in range(N + 1)]
        for i in range(N + 1):
            for j in range(N + 1):
                if i != j:
                    # Tính khoảng cách, làm tròn và ép kiểu int
                    dist = math.hypot(coords[i][0] - coords[j][0], coords[i][1] - coords[j][1])
                    t[i][j] = int(round(dist))
        
        # 4. Ghi e(i), l(i), d(i) cho N khách hàng
        for i in range(1, N + 1):
            d_i = random.randint(5, 30)
            min_arrival = t[0][i]
            e_i = min_arrival + random.randint(0, 200)
            l_i = e_i + d_i + random.randint(50, 500)
            
            f.write(f"{int(e_i)} {int(l_i)} {int(d_i)}\n")
        
        # 5. Ghi ma trận t
        for row in t:
            f.write(" ".join(map(str, row)) + "\n")
            
    print(f"Đã tạo thành công: {filename} (N = {N})")

if __name__ == "__main__":
    print("Bắt đầu sinh test cases bình thường (N: 10 -> 950)...")
    generate_normal_tsptw_test_cases()
    print("-" * 40)
    
    