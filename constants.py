import os
from employee import Employee
from cvs_plot_into_dict_converter import csv_to_dict
from shimura import Shimura
from advance import Advance

#何世代まで行うか
NGEN = 1000
#集団の個体数
POP = 300
#個体が突然変異を起こす確率
# 世代が進むほど局所解の可能性が上がるので徐々に変異率を上げる手法はありか？
MUTPB = 0.03
#何日間のスケジュールか
DAYS = 31
#保存されるエリートの世代ごとの個体数
ELITISM = 1
ROOT_DIRECTORY = "/home/ttnk0/projects/ga_nurse_scheduling/"
DATA_DIRECTORY = os.path.join(ROOT_DIRECTORY,"data")
CASHE_DIRECTORY = os.path.join(DATA_DIRECTORY,"cashe")
OUTPUT_DIRECTORY = os.path.join(DATA_DIRECTORY,"output")
#保存するcsvファイルの名前
CSV_NAME_CACHE = os.path.join(CASHE_DIRECTORY, "schedule_cache.csv")
# CSV_NAME_LOAD = "/home/ttnk0/projects/ga_nurse_scheduling/data/_schedule_July_OB_with_metadata.csv"
CSV_NAME_LOAD = CSV_NAME_CACHE
CSV_NAME_SAVE = os.path.join(OUTPUT_DIRECTORY, "schedule_2025July")
CSV_NAME_FIXED_DATE_PLOT = os.path.join(DATA_DIRECTORY, "_fixed_plot.csv")

LOAD = True
SAVE_TO_CACHE = True

a = Employee(name="OB", able_to_cnt=4, on_duty_per_week=4, date_off_duty=[], plot_preference={"A":1,"B":2,"C":-100,"E":5,"NE":2})
b = Employee(name="MR", able_to_cnt=4, on_duty_per_week=5, date_off_duty=[], plot_preference={"A":2,"B":3,"C":-100,"E":3,"NE":5})
c = Shimura(name="SM", able_to=3, on_duty_per_week=4.5, date_off_duty=[], plot_preference={"A":4,"B":1,"C":5,"E":-100,"NE":-100})
d = Employee(name="TN", able_to_cnt=3, on_duty_per_week=5, date_off_duty=[], plot_preference={"A":5,"B":5,"C":1,"E":-100,"NE":-100})
e = Employee(name="WT", able_to_cnt=3, on_duty_per_week=4, date_off_duty=[], plot_preference={"A":3,"B":3,"C":-100,"E":-100,"NE":2})
f = Employee(name="MT", able_to_cnt=1, on_duty_per_week=2, date_off_duty=[], plot_preference={"A":-100,"B":-100,"C":-100,"E":3,"NE":-100})
g = Employee(name="KB", able_to_cnt=1, on_duty_per_week=3, date_off_duty=[], plot_preference={"A":-100,"B":3,"C":-100,"E":-100,"NE":-100})
h = Advance(name="AW", able_to=1, on_duty_per_week=1.5, date_off_duty=[], plot_preference={"A":-100,"B":-100,"C":-100,"E":-100,"NE":3})
i = Advance(name="YM", able_to=2, on_duty_per_week=0.5, date_off_duty=[], plot_preference={"A":-100,"B":3,"C":-100,"E":-100,"NE":3})
j = Advance(name="MB", able_to=3, on_duty_per_week=0.5, date_off_duty=[], plot_preference={"A":3,"B":3,"C":-100,"E":-100,"NE":3})
# i = Advance("YS",2,1,[],{"A":-100,"B":3,"C":-100,"E":-100,"NE":3})
# j = Advance("MB",3,0.5,[],{"A":3,"B":3,"C":-100,"E":-100,"NE":3})

EMPLOYEES = [a,b,c,d,e,f,g,h,i,j]
# EMPLOYEES = [a,b,c,d,e,f,g,h]

# FIXED_DATE_PLOT = {5:{3:"C",5:"C"},6:{3:"C",5:"C"},7:{3:"C",5:"C"},10:{0:"A",6:"A"},11:{0:"A",6:"A"},12:{4:"A",6:"A"}}
FIXED_DATE_PLOT = csv_to_dict(filename=CSV_NAME_FIXED_DATE_PLOT)