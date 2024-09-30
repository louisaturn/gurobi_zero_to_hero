import gurobipy as gp
from gurobipy import GRB
from input import Problem
from results import Solution

class Weights():    
    def __init__(self, technician_cost=100, skip_customer_cost=1000, early_cost=1, late_cost=10):
        self.techinician_cost = technician_cost
        self.skip_customer_cost = skip_customer_cost
        self.early_cost = early_cost
        self.late_cost = late_cost


def solve(problem: Problem, weights: Weights) -> Solution:  
    
    # Build model
    model = gp.Model()

    combinations = {(t,c) for c in problem.customers for t in c.job.coveredBy}
    assign = model.addVars(combinations, vtype=GRB.BINARY, name="assign")
    skip = model.addVars(problem.customers, vtype=GRB.BINARY, name="skip")
    use = model.addVars(problem.technicians, vtype=GRB.BINARY, name="use")
    route = model.addVars(problem.technicians, problem.locations, problem.locations, vtype=GRB.BINARY, name="route")
    
    start = model.addVars(problem.customers, vtype=GRB.CONTINUOUS, name="start")
    depart = model.addVars(problem.technicians, vtype=GRB.CONTINUOUS, name="depart")
    return_var = model.addVars(problem.technicians, vtype=GRB.CONTINUOUS, name="return")

    early = model.addVars(problem.customers, vtype=GRB.CONTINUOUS, name="early", lb=0)
    late = model.addVars(problem.customers, vtype=GRB.CONTINUOUS, name="late", lb=0)

    for t in problem.technicians:
        for d in problem.depots:
            if t.depot != d:
                for l in problem.locations:
                    route[t,d,l].ub = 0
                    route[t,l,d].ub = 0

    for t in problem.technicians:
        for c in problem.customers:
            if (t,c) not in combinations:
                for l in problem.locations:
                    route[t,l,c].ub = 0
                    route[t,c,l].ub = 0

    model.addConstrs(route.sum(t,t.depot,'*') == use[t] for t in problem.technicians)
    model.addConstrs(route.sum(t,'*',t.depot) == use[t] for t in problem.technicians)
    model.addConstrs(route.sum(t,c,'*') == assign[t,c] for (t,c) in combinations)
    model.addConstrs(route.sum(t,'*',c) == assign[t,c] for (t,c) in combinations)
    
    model.addConstrs(assign.sum('*', c) + skip[c] == 1 for c in problem.customers)
    model.addConstrs(assign[t,c] <= use[t] for (t,c) in combinations)

    M = max(technician.capacity for technician in problem.technicians)
    model.addConstrs(start[c2] >= 
                     start[c1] + c1.job.duration + problem.distances[c1,c2] - M * (1 - route.sum('*',c1,c2))
                     for c1 in problem.customers
                     for c2 in problem.customers
                     if c1 != c2)
    model.addConstrs(start[c] >= depart[t] + problem.distances[t.depot, c] - M * (1 - route(t,t.depot,c))
                     for c in problem.customers
                     for t in problem.technicians)
    model.addConstrs(return_var[t] >= start[c] + c.job.duration + problem.distances[c,t.depot] - M * (1 - route[t,c,t.depot])
                     for t in problem.technicians
                     for c in problem.customers)

    model.addConstrs(start[c] >= c.tStart - early[c] for c in problem.customers)
    model.addConstrs(start[c] + c.job.duration <= c.tEnd + late[c] for c in problem.customers)

    for l in problem.locations:
        for t in problem.technicians:
            route[t,l,l].ub = 0
    
    edges = {(s,e) for s in problem.locations for e in problem.locations if s != e}
    model.addConstrs(gp.quicksum(c.job.duration * assign[t, c] for c in problem.customers if (t,c) in combinations)
                      + gp.quicksum(route[t,s,e] * problem.distances[s,e] for (s,e) in edges) 
                      <= t.capacity for t in problem.technicians)

    model.setObjective(gp.quicksum(weights.skip_customer_cost * c.job.priority * skip[c] for c in problem.customers) +
                        weights.techinician_cost * use.sum() +
                        weights.early_cost * early.sum() +
                        weights.late_cost * late.sum()
                        , GRB.MINIMIZE)
    # Optimize
    model.optimize()
    
    # Construct list of schedules
    solution = Solution(problem)

    for t in problem.technicians:
        for c in problem.customers:
            if (t,c) in combinations and assign[(t,c)].X == 1:
                schedule = solution.add(t)
                p = next(p for (t,p,l), var in route.items() if var.X == 1 and l == c)
                n = next(n for (t,l,n), var in route.items() if var.X == 1 and l == c)
                schedule.add(c,p,n)

    return solution
