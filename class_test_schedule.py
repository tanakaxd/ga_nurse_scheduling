import os
from schedule import Schedule
from constants import CSV_NAME_CACHE, DATA_DIRECTORY, DAYS, EMPLOYEES, MUTPB

csv_name = os.path.join(DATA_DIRECTORY,"schedule_7.csv")
saved_sche = Schedule.load_from_csv(DAYS,MUTPB,EMPLOYEES,csv_name)
saved_sche.calcFitness()
print(csv_name)
saved_sche.print()
