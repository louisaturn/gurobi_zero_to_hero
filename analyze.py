import pandas as pd
from results import Solution, Schedule, Task

def getTaskAsDict(task: Task):
    return {
        'customer': task.customer.name,
        'technician': task.schedule.technician.name,
        'priority': task.customer.job.priority,
        'job_type': task.customer.job.name,
        'duration': task.customer.job.duration,
        'city': task.customer.city,
        'city_before': task.previous.city,
        'city_after': task.next.city
    }

def getTaskFrame(solution: Solution):
    tasks = map(getTaskAsDict, solution.tasks.values())
    return pd.DataFrame(tasks)