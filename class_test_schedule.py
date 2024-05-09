import os
from schedule import Schedule
from constants import CSV_NAME_CACHE, DATA_DIRECTORY, DAYS, EMPLOYEES, MUTPB, FIXED_DATE_PLOT

csv_name = os.path.join(DATA_DIRECTORY,"_schedule_May_OB.csv")
saved_sche = Schedule.load_from_csv(DAYS,MUTPB,EMPLOYEES,FIXED_DATE_PLOT,csv_name)
saved_sche.calcFitness()
print(csv_name)
saved_sche.print()
