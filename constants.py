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
CSV_NAME_LOAD = "/home/ttnk0/projects/ga_nurse_scheduling/data/_schedule_July_OB_with_metadata.csv"
CSV_NAME_SAVE = os.path.join(OUTPUT_DIRECTORY, "schedule_2025July")
CSV_NAME_FIXED_DATE_PLOT = os.path.join(DATA_DIRECTORY, "_fixed_plot.csv")

LOAD = True
SAVE_TO_CACHE = True

a = Employee("OB",4,4,[],{"A":1,"B":2,"C":-100,"E":5,"NE":2})
b = Employee("MR",4,5,[],{"A":2,"B":3,"C":-100,"E":3,"NE":5})
c = Shimura("SM",3,4.5,[],{"A":4,"B":1,"C":5,"E":-100,"NE":-100})
d = Employee("TN",3,5,[],{"A":5,"B":5,"C":1,"E":-100,"NE":-100})
e = Employee("WT",3,4.5,[],{"A":3,"B":3,"C":-100,"E":-100,"NE":2})
f = Employee("MT",1,2,[],{"A":-100,"B":-100,"C":-100,"E":3,"NE":-100})
g = Employee("KB",1,3,[],{"A":-100,"B":3,"C":-100,"E":-100,"NE":-100})
h = Advance("AW",1,1.5,[],{"A":-100,"B":-100,"C":-100,"E":-100,"NE":3})
i = Advance("YS",2,1,[],{"A":-100,"B":3,"C":-100,"E":-100,"NE":3})
j = Advance("MB",3,0.5,[],{"A":3,"B":3,"C":-100,"E":-100,"NE":3})

EMPLOYEES = [a,b,c,d,e,f,g,h,i,j]

# FIXED_DATE_PLOT = {5:{3:"C",5:"C"},6:{3:"C",5:"C"},7:{3:"C",5:"C"},10:{0:"A",6:"A"},11:{0:"A",6:"A"},12:{4:"A",6:"A"}}
FIXED_DATE_PLOT = csv_to_dict(CSV_NAME_FIXED_DATE_PLOT)