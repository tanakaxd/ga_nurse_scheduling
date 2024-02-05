import random
from employee import Employee
from shimura import Shimura
from schedule import Schedule

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
DAYS = 29

a = Employee("OB",True,5,[],{"A":4,"B":1,"C":0,"E":4,"NE":5})
b = Employee("T1",True,2.5,[4,9,10,13,15,16,19,23,24,26,27,29],{"A":1,"B":4,"C":0,"E":4,"NE":4})
c = Employee("YM",True,5,[],{"A":1,"B":3,"C":0,"E":5,"NE":5})
d = Employee("MO",True,5,[],{"A":2,"B":3,"C":0,"E":5,"NE":5})
e = Shimura("SM",False,5,[3],{"A":5,"B":1,"C":3,"E":0,"NE":0})
f = Employee("TT",False,3,[],{"A":4,"B":3,"C":5,"E":0,"NE":0})
g = Employee("YZ",False,5,[8,9,10],{"A":3,"B":2,"C":5,"E":0,"NE":0})

EMPLOYEES = [a,b,c,d,e,f,g]

pop = [Schedule(DAYS,MUTPB,EMPLOYEES) for _ in range(POP)]
gen_cnt = 0
hall_of_fame = None

for i in range(NGEN):

  print(f'GENERATION:{gen_cnt}')

  # fitness function
  for s in pop:
    s.calcFitness()
  fitness_list = [s.fitness for s in pop]
  max_fit = max(fitness_list)
  print(f'AVERAGE:{sum(fitness_list)/POP}')
  fittest_schedule = pop[fitness_list.index(max_fit)]
  # 殿堂入りの更新
  if hall_of_fame==None:
    hall_of_fame = fittest_schedule
  elif hall_of_fame.fitness<fittest_schedule.fitness:
    hall_of_fame = fittest_schedule

  fittest_schedule.print()

  # intercourse
  probabilities = [s.fitness for s in pop]
  probabilities = [p/sum(probabilities) for p in probabilities]
  new_pop = []
  for j in range(POP):
    pairs = random.choices(pop, weights=probabilities, k=2)
    child = pairs[0].cross(pairs[1])
    new_pop.append(child)
  pop = new_pop
  gen_cnt+=1

print("HALL OF FAME")
hall_of_fame.print()


