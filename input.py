import xlrd

def rep(name: str):
    return name.replace(' ', '_')

class Location():
    city: str

    def __init__(self, city):
        self.city = city    

class Depot(Location):
    def __init__(self, city):
        super().__init__(city)

    def __repr__(self):
        return f'Depot#{rep(self.city)}'

class Technician():
    name: str
    capacity: float
    depot: Depot

    def __init__(self, name: str, capacity: float, depot: Depot):
        self.name = name
        self.capacity = capacity
        self.depot = depot

    def __repr__(self):
        return f'Technician#{rep(self.name)}'

class Job():
    name: str
    priority: int
    duration: float
    coveredBy: list[Technician]

    def __init__(self, name: str, priority: int, duration: float, coveredBy: list[Technician]):
        self.name = name
        self.priority = priority
        self.duration = duration
        self.coveredBy = coveredBy

    def __repr__(self):
        return f'Job#{rep(self.name)}'

class Customer(Location):
    name: str
    job: Job
    tStart: float
    tEnd: float

    def __init__(self, name: str, city: str, job: Job, tStart: float, tEnd: float):
        super().__init__(city)
        self.name = name
        self.job = job
        self.tStart = tStart
        self.tEnd = tEnd

    def __repr__(self):
        return f'Customer#{rep(self.city)}'

class Problem():
    depots: set[Depot]
    jobs: set[Job]
    technicians: set[Technician]
    customers: set[Customer]
    locations: set[Location]
    distances: dict[(Location,Location),float]

    def __init__(self, depots: set[Depot], technicians: set[Technician], jobs: set[Job], customers: set[Customer], distances: dict[(Location,Location),float]):
        self.depots = depots
        self.technicians = technicians
        self.jobs = jobs        
        self.customers = customers
        self.locations = customers.union(depots)
        self.distances = distances            

def readExcel(filename) -> Problem:
    # Open Excel workbook
    wb = xlrd.open_workbook(filename)

    # Read technician data
    depots: dict[str, Depot] = {}
    ws = wb.sheet_by_name('Technicians')
    technicians = []
    for i,t in enumerate(ws.col_values(0)[3:]):
        # Create Technician object
        data = ws.row_values(3+i)[:3]
        if(not data[2] in depots):
            depots[data[2]] = Depot(data[2])
        data[2] = depots[data[2]]
        thisTech = Technician(*data)
        technicians.append(thisTech)
    
    # Read job data
    jobs = {}
    for j,b in enumerate(ws.row_values(0)[3:]):
        coveredBy = [t for i,t in enumerate(technicians) if ws.cell_value(3+i,3+j) == 1]
        # Create Job object
        thisJob = Job(*ws.col_values(3+j)[:3], coveredBy)
        jobs[thisJob.name] = thisJob

    # Read customer data
    ws = wb.sheet_by_name('Customers')
    customers = set()
    for i,c in enumerate(ws.col_values(0)[1:]):
        b = jobs[ws.cell_value(1+i, 2)]
        # Create Customer object using corresponding Job object
        rowVals = ws.row_values(1+i)    
        thisCustomer = Customer(*rowVals[:2], b, *rowVals[3:])
        customers.add(thisCustomer)

    # Read location data
    ws = wb.sheet_by_name('Locations')
    locationNames = ws.col_values(0)[1:]
    locations = { loc.city: loc for loc in set(depots.values()).union(customers) }
    dist = {(l, l) : 0 for l in locations}
    for i,l1 in enumerate(locationNames):
        for j,l2 in enumerate(locationNames):
            dist[locations[l1],locations[l2]] = ws.cell_value(1+i, 1+j)

    return Problem(set(depots.values()), technicians, jobs.values(), customers, dist)