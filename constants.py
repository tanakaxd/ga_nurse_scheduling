import os
from employee import Employee
from cvs_plot_into_dict_converter import csv_to_dict
from shimura import Shimura

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
DATA_DIRECTORY = os.path.join("ga_nurse_scheduling","data")
#保存するcsvファイルの名前
CSV_NAME_CACHE = os.path.join(DATA_DIRECTORY, "schedule_cache.csv")
CSV_NAME_LOAD = os.path.join(DATA_DIRECTORY, "schedule_cache.csv")
CSV_NAME_SAVE = os.path.join(DATA_DIRECTORY, "schedule")
CSV_NAME_FIXED_DATE_PLOT = os.path.join(DATA_DIRECTORY, "_fixed_plot.csv")

LOAD = True
SAVE_TO_CACHE = True

a = Employee("OB",4,4.5,[],{"A":4,"B":1,"C":-100,"E":5,"NE":3})
b = Employee("T1",4,3,[],{"A":3,"B":4,"C":-100,"E":1,"NE":4})
c = Employee("MO",4,5,[],{"A":1,"B":4,"C":-100,"E":3,"NE":5})
d = Shimura("SM",3,5,[],{"A":4,"B":1,"C":5,"E":-100,"NE":-100})
e = Employee("TT",3,4.5,[],{"A":4,"B":2,"C":3,"E":-100,"NE":-100})
f = Employee("ON",2,5,[],{"A":-100,"B":2,"C":4,"E":-100,"NE":-100})
g = Employee("HK",2,3.5,[],{"A":4,"B":-100,"C":-100,"E":-100,"NE":2})

EMPLOYEES = [a,b,c,d,e,f,g]

# FIXED_DATE_PLOT = {5:{3:"C",5:"C"},6:{3:"C",5:"C"},7:{3:"C",5:"C"},10:{0:"A",6:"A"},11:{0:"A",6:"A"},12:{4:"A",6:"A"}}
FIXED_DATE_PLOT = csv_to_dict(CSV_NAME_FIXED_DATE_PLOT)