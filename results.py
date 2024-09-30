from input import Problem, Technician, Customer, Location

class Task:
    customer: Customer
    schedule: 'Schedule'
    previous: Location
    next: Location

    def __init__(self, schedule: 'Schedule', customer: Customer, previous: Location, next: Location):
        self.schedule = schedule
        self.customer = customer
        self.previous = previous
        self.next = next   

class Schedule:
    solution: 'Solution'
    technician: Technician
    tasks: list[Task]

    def __init__(self, solution: 'Solution', technician: Technician):
        self.tasks = []
        self.solution = solution
        self.technician = technician

    def add(self, customer: Customer, previous: Location, next: Location) -> Task:
        task = Task(self, customer, previous, next)
        self.tasks.append(task)
        self.solution.tasks[customer] = task
        return task

class Solution:
    schedules: dict[Technician, Schedule] = dict()
    tasks: dict[Customer, Task] = dict()

    def __init__(self, problem: Problem):
        self.problem = problem
        
    def add(self, technician: Technician) -> Schedule:
        schedule = Schedule(self, technician)
        self.schedules[technician] = schedule
        return schedule
