import copy
import random
import sys
from day import Day

class Schedule(object):

  def __init__(self,days_cnt,mutation_prob,employees):
    self.days = [Day(date+1) for date in range(days_cnt)]
    self.fitness = 0 #0-1の値
    self.mutation_prob = mutation_prob
    self.employees = employees
    self.employees_utility = []
    self.starting_day_of_week = "日"
    self.rest_all_day_of_week = "水"

  
  def print(self):
    print(f'Schedule(fitness={self.fitness})')
    for d in self.days:
      print(d.cells)
  
  def cross(self, another):
    child = copy.deepcopy(self)
    for i, _ in enumerate(child.days):
        # 親の日のdeepcopyを子供の日に設定
        child.days[i] = copy.deepcopy(random.choice([self.days[i], another.days[i]]))
        if random.random() < self.mutation_prob:
            child.days[i].mutate()
    return child

  def calcFitness(self):
    # TODO
    # 週単位での希望勤務日数:(2)
    # 割り当て区画の幸福度:(1)
    # 出勤できない日:(10000)
    # E/NEは女性陣しかできない:(10000)
    # テーブル割当はできるだけばらけるようにする:(0.5)
    # 特定の日を固定で休日にする。連休などの計算に必要になる:(10000)

    fitness1,fitness2,fitness3,fitness4,fitness5 = 0,0,0,0,0
    weight1,weight2,weight3,weight4,weight5 = 100,1,2,10000,0.5

    for i, emp in enumerate(self.employees):
      # 週単位での希望勤務日数:(100)
      # 人ごとにRでない記号をカウントする
      l = [d.cells[i] for d in self.days] 
      l = list(filter(lambda x: x!="R", l)) 
      # 希望とカウント数の差の絶対値を合計する
      fitness1 += abs(len(l) - emp.on_duty_per_week/7*len(self.days))#TODO とりあえず固定休日は考えず月単位での出勤予定数で評価
      
      # 割り当て区画の幸福度:(1)
      # 単純に全員の幸福度をすべて合算するアプローチ
      fitness2 += sum([emp.plot_preference_normalized[plot] for plot in l])


      # 出勤できない日:(10000)
      # 一つでも当てはまったら即却下でもいいかもしれないがループを二重に抜ける必要がある
      # 即最低値にすると全個体が実践的には最低評価になってしまうので、禁止事項を満たすほどマイナスを増やしていく
      # emp一人の、つまり縦の{日付、区画}ディクショナリを作る
      list_on_duty_date = {d.date: d.cells[i] for d in self.days}
      # それがemp.date_off_dutyと被るか確認
      for d in emp.date_off_duty:
        if list_on_duty_date[d]!="R":
          fitness3 -= 1

    # 希望とのずれが大きいほどfitnessは小さくしたいのでfitness1は逆数をとる
    if fitness1!=0:
      fitness1 = 1/fitness1
    else:
      fitness1 = 1


    # print(" ")
    # print(fitness1)
    # print(fitness2)
    # print(fitness3)
    # print(fitness1 * weight1)
    # print(fitness2 * weight2)
    # print(fitness3 * weight3)

    total_fitness = fitness1 * weight1 + fitness2 * weight2 + fitness3 * weight3
    # print(f'total_fitness = {total_fitness}')
    self.fitness = max(sys.float_info.epsilon,total_fitness)
    # print(f'self.fitness = {self.fitness}')
    


    











      
