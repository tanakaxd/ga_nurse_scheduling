from schedule import Schedule
from constants import CSV_NAME, DAYS, EMPLOYEES, MUTPB

saved_sche = Schedule.load_from_csv(DAYS,MUTPB,EMPLOYEES,CSV_NAME)
saved_sche.calcFitness()
print(CSV_NAME)
saved_sche.print()
