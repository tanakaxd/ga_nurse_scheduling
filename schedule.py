import copy
import random
from day import Day

class Schedule(object):

  def __init__(self,days_cnt,mutation_prob,employees,wishes):
    self.days = [Day() for _ in range(days_cnt)]
    self.fitness = 0 #0-1の値
    self.mutation_prob = mutation_prob
    self.employees = employees
    self.employees_utility = []
    self.wishes = wishes
  
  def print(self):
    print(f'Schedule(fitness={self.fitness})')
    for d in self.days:
      print(d.cells)

  # 以下のメソッドは親のdaysの参照をコピーしているため一度突然変異が発生すると親が生む次の個体まで影響を与えてしまう。
  # def cross(self,another):
  #   child = Schedule()
  #   for i, d in enumerate(child.days):
  #     child.days[i] = random.choice([self.days[i],another.days[i]])
  #     if random.random()<MUTPB:
  #       # child.print()
  #       child.days[i].mutate()
  #       # child.print()
  # # 本来遺伝子が長くなればなるほど突然変異が起こりやすくなる？その場合、個体ごとに確率判定するのではなく、遺伝子のある単位ごとに判定すべきかも
  # # if random.random()<MUTPB:
  # #   child.days[random.randint(0,len(child.days)-1)].mutate()
  # return child
  
  # bingによって修正されたメソッド
  def cross(self, another):
    child = copy.deepcopy(self)
    for i, d in enumerate(child.days):
        # 親の日のコピーを子供の日に設定
        child.days[i] = copy.deepcopy(random.choice([self.days[i], another.days[i]]))
        if random.random() < self.mutation_prob:
            child.days[i].mutate()
    return child

  def calcFitness(self):
    raw_total_fitness = 0
    for i, wish in enumerate(self.wishes):
      # 人ごとにRでない記号をカウントする
      l = [d.cells[i] for d in self.days] # ["R","A","R","A","C","A","R"]
      l = list(filter(lambda x: x!="R", l)) # ["A","A","C","A"]
      # 希望とカウント数の差の絶対値を合計する
      raw_total_fitness += abs(len(l) - self.wishes[i])
      # 希望とのずれが大きいほどfitnessは小さくするために逆数をとる
    if raw_total_fitness!=0:
      self.fitness = 1/raw_total_fitness
    else:
      self.fitness = 1
      
