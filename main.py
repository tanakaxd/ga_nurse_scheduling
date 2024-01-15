import random
from schedule import Schedule

#乱数を固定
# random.seed(64)
#何世代まで行うか
NGEN = 50
#集団の個体数
POP = 80
#個体が突然変異を起こす確率
MUTPB = 0.1
#何日間のスケジュールか
DAYS = 6

# TODO　ラムダで各々の希望をかく？
WISHES = [5,5,5,2,1]


pop = [Schedule(DAYS,MUTPB,WISHES) for _ in range(POP)]
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


