import sys
from ortools.linear_solver import pywraplp

def MIP(N, e, l, d, c):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return None, None

    nodes = list(range(N + 1))
    x = {}
    t = {}
    u = {}
    A = []

    # Graph sparsification
    for i in nodes:
        for j in nodes:
            if i != j:
                if j == 0 or e[i] + d[i] + c[i][j] <= l[j]:
                    x[i, j] = solver.BoolVar(f'x[{i}][{j}]')
                    A.append((i, j, x[i, j]))

    # Hamiltonian circuit constraints
    for i in nodes:
        solver.Add(solver.Sum(x[i, j] for j in nodes if (i, j) in x) == 1)
        solver.Add(solver.Sum(x[j, i] for j in nodes if (j, i) in x) == 1)

    # Time constraints
    for i in nodes:
        t[i] = solver.NumVar(e[i], l[i], f't[{i}]')
    for i, j, _ in A:
        if j != 0:
            M = max(0, l[i] - e[j] + d[i] + c[i][j])
            solver.Add(t[j] >= t[i] + d[i] + c[i][j] - M * (1 - x[i, j]))

    #Subtour elimination constraints
    for i in range(1, N + 1):
        u[i] = solver.IntVar(1, N, f'u[{i}]')

    for i, j, _ in A:
        if i != 0 and j != 0:
            solver.Add(u[i] - u[j] + N * x[i, j] <= N - 1)
    
    #Objective
    obj = sum(c[i][j] * x[i, j] for i, j, _ in A)

    solver.Minimize(obj)
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        cost = solver.Objective().Value()
        route = []
        curr = 0

        while True:
            for j in nodes:
                if (curr, j) in x and x[curr, j].solution_value() > 0.5:
                    if j != 0:
                        route.append(j)
                    curr = j
                    break
            if curr == 0:
                break

        return route, cost
    
    else:
        print('No optimal solution')
        return None, None
    
def main():
    inp = sys.stdin.read().strip().splitlines()

    N = int(inp[0])
    nodes = [i for i in range(N + 1)]
    e = [0]      
    l = [99999]  
    d = [0]
    c = []

    for i in range(N):
        e_i, l_i, d_i = inp[i + 1].split()
        e.append(int(e_i))
        l.append(int(l_i))
        d.append(int(d_i))

    for i in nodes:
        c.append([int(x) for x in inp[i + N + 1].split()])
    
    l[0] = max(l[i] + d[i] + c[i][0] for i in range(1, N + 1))

    route, cost = MIP(N, e, l, d, c)

    print(N)
    for i in route:
        print(i, end=' ')
    print()

if __name__ == "__main__":
    main()