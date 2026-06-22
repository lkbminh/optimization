import sys
from ortools.sat.python import cp_model

def CP(N, e, l, d, c):
    nodes = list(range(N + 1))
    
    model = cp_model.CpModel()

    x = {}
    t = {}
    A = []

    #Graph sparsification
    for i in nodes:
        for j in nodes:
            if i != j:
                if j == 0 or e[i] + d[i] + c[i][j] <= l[j]:
                    x[i, j] = model.new_bool_var(f'x[{i}][{j}]')
                    A.append((i, j, x[i, j]))

    #Hamiltonian circuit
    model.add_circuit(A)

    #Time constraints
    for i in nodes:
        t[i] = model.new_int_var(e[i], l[i], f't[{i}]')
        
    for i, j, _ in A:
        if j != 0:
            model.add(t[j] >= t[i] + d[i] + c[i][j]).only_enforce_if(x[i, j])

    #Objective
    obj = sum(c[i][j] * x[i, j] for i, j, _ in A)

    model.minimize(obj)

    solver = cp_model.CpSolver()
    status = solver.solve(model)

    if status == cp_model.OPTIMAL:
        cost = solver.objective_value
        
        route = []
        curr = 0

        while True:
            for j in nodes:
                if (curr, j) in x and solver.boolean_value(x[curr, j]):
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

    route, cost = CP(N, e, l, d, c)

    print(N)
    for i in route:
        print(i, end=' ')
    print()

if __name__ == "__main__":
    main()
