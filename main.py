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
NGEN = 100
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

loaded_sche = Schedule.load_from_csv(DAYS,MUTPB,EMPLOYEES,CSV_NAME)
loaded_sche.print()

pop = []
pop.append(loaded_sche)
while len(pop)<POP:
  pop.append(Schedule(DAYS,MUTPB,EMPLOYEES))
# pop = [Schedule(DAYS,MUTPB,EMPLOYEES) for _ in range(POP)]
gen_cnt = 0
average_fitness_history = []
gen_max_fit_history = []
hall_of_fame = None
hof_gen = 0

for i in range(NGEN):

  print(f'GENERATION:{gen_cnt}')

  # fitness function
  for s in pop:
    s.calcFitness()
  fitness_list = [s.fitness for s in pop]
  max_fit = max(fitness_list)
  gen_max_fit_history.append(max_fit)
  ave = sum(fitness_list)/POP
  average_fitness_history.append(ave)
  print(f'AVERAGE:{ave}')
  fittest_schedule = pop[fitness_list.index(max_fit)]

  # 殿堂入りの更新
  if hall_of_fame==None:
    hall_of_fame = fittest_schedule
    hof_gen = gen_cnt
  elif hall_of_fame.fitness<fittest_schedule.fitness:
    hall_of_fame = fittest_schedule
    hof_gen = gen_cnt

  fittest_schedule.print()

  # intercourse
  probabilities = [s.fitness**2 for s in pop]
  probabilities = [p/sum(probabilities) for p in probabilities]
  new_pop = []
  hall_of_fame.clear()
  new_pop.append(hall_of_fame)# エリートを直接引き継ぐ
  for j in range(POP-ELITISM):# エリートを除外
    pairs = random.choices(pop, weights=probabilities, k=2)
    child = pairs[0].cross(pairs[1])
    new_pop.append(child)
  pop = new_pop
  gen_cnt+=1

print("HALL OF FAME")
print(f'GENERATION:{hof_gen}')
hall_of_fame.calcFitness()
hall_of_fame.print()
hall_of_fame.save_to_csv(CSV_NAME)

plt.plot(average_fitness_history)
plt.plot(gen_max_fit_history)
plt.show()
