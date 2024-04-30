import random
from employee import Employee
from shimura import Shimura
from schedule import Schedule

import matplotlib.pyplot as plt

#TODO
# average fitnessの推移をグラフ化
# エリート保存

# utilityの最適化、担当可能区画の数に応じて標準化する仕様。とりあえず女性かどうかを考慮しないことにする

# 保存したスケジュールからインスタンス化
# スケジュール部分固定の実装
# 労働者相性の実装
# 交配確率の最適化

# 乱数を固定
# random.seed(64)
#何世代まで行うか
NGEN = 500
#集団の個体数
POP = 300
#個体が突然変異を起こす確率
# 世代が進むほど局所解の可能性が上がるので徐々に変異率を上げる手法はありか？
MUTPB = 0.03
#何日間のスケジュールか
DAYS = 31
#保存されるエリートの世代ごとの個体数
ELITISM = 1
#保存するcsvファイルの名前
CSV_NAME = "schedule.csv"

a = Employee("OB",4,5,[],{"A":3,"B":1,"C":0,"E":5,"NE":3})
b = Employee("T1",4,3,[],{"A":3,"B":5,"C":0,"E":1,"NE":3})
c = Employee("MO",4,5,[],{"A":1,"B":3,"C":0,"E":3,"NE":5})
d = Shimura("SM",3,5,[],{"A":3,"B":1,"C":5,"E":0,"NE":0})
e = Employee("TT",3,4,[],{"A":4,"B":2,"C":3,"E":0,"NE":0})
f = Employee("ON",2,5,[],{"A":0,"B":2,"C":4,"E":0,"NE":0})
g = Employee("HK",2,3.5,[19],{"A":4,"B":0,"C":0,"E":0,"NE":2})

EMPLOYEES = [a,b,c,d,e,f,g]

saved_sche = Schedule.load_from_csv(DAYS,MUTPB,EMPLOYEES,CSV_NAME)
saved_sche.calcFitness()
saved_sche.print()
