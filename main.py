import random
from employee import Employee
from schedule import Schedule

# 乱数を固定
# random.seed(64)
#何世代まで行うか
NGEN = 50
#集団の個体数
POP = 100
#個体が突然変異を起こす確率
MUTPB = 0.03
#何日間のスケジュールか
DAYS = 7

a = Employee("OB",True,5,[1],{"A":4,"B":1,"C":1,"E":4,"NE":5})
b = Employee("T1",True,2.5,[2],{"A":3,"B":3,"C":2,"E":4,"NE":5})
c = Employee("YM",True,5,[3],{"A":3,"B":3,"C":2,"E":4,"NE":5})
d = Employee("MO",True,5,[4],{"A":2,"B":3,"C":1,"E":5,"NE":5})
e = Employee("SM",False,5,[5],{"A":5,"B":1,"C":3,"E":0,"NE":0})
f = Employee("TT",False,3,[6],{"A":3,"B":3,"C":3,"E":0,"NE":0})
g = Employee("YZ",False,5,[7],{"A":3,"B":4,"C":3,"E":0,"NE":0})

EMPLOYEES = [a,b,c,d,e,f,g]

pop = [Schedule(DAYS,MUTPB,EMPLOYEES) for _ in range(POP)]
gen_cnt = 0

for i in range(NGEN):

  print(f'GENERATION:{gen_cnt}')

  # fitness function
  for s in pop:
    s.calcFitness()
  fitness_list = [s.fitness for s in pop]
  max_fit = max(fitness_list)
  print(f'AVERAGE:{sum(fitness_list)/POP}')
  fittest_schedule = pop[fitness_list.index(max_fit)]
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


