from input import readExcel
from model import solve, Weights
from analyze import getTaskFrame

problem = readExcel('data.xls')
weights = Weights(10, 1)
solution = solve(problem, weights)
df = getTaskFrame(solution)
df.to_excel('solution.xlsx')
print(df)
print(f'Technicians: {df["technician"].nunique()}')
print(f'Customers: {df["customer"].nunique()}')
print(df.groupby('technician')['duration'].sum())