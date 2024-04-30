import copy
import csv
import random
import sys
from day import Day
from weekday import Weekday

class Schedule(object):

  def __init__(self,days_cnt,mutation_prob,employees,days_data=None):
    self.fitness = 0 #0-1の値
    self.days_cnt = days_cnt
    self.mutation_prob = mutation_prob
    self.employees = employees
    self.employees_utility = []
    self.employees_on_duty_cnt = []
    self.starting_weekday_of_month = Weekday.WEDNESDAY
    # 特定の日を固定で休日にする。連休などの計算に必要になる:
    self.closed_weekday = Weekday.WEDNESDAY
    if days_data is not None:
      self.days = [Day(i+1,self.starting_weekday_of_month,self.closed_weekday,len(self.employees),day_data) for i,day_data in enumerate(days_data)]
    else:
      self.days = [Day(i+1,self.starting_weekday_of_month,self.closed_weekday,len(self.employees)) for i in range(self.days_cnt)]
      # 日にち:休み希望者というディクショナリをつくる。日にちをkeyにするのは、同日はemp単位ではなくまとめて書き換えたいから
      day_off_dict = {}
      for emp_index,emp in enumerate(employees):
        for date in emp.date_off_duty:
          if date not in day_off_dict:
              day_off_dict[date] = [emp_index]
          else:
              day_off_dict[date].append(emp_index)
      # ディクショナリをループし、dayのcellsを書き換える
      # ただし、cellsの割り当てバランスを崩してはいけないので、固定してシャッフルする必要がある
      # その責任はdayクラスに持たせる
      for key,value in day_off_dict.items():
        self.days[key-1].fixed_R_shuffle(value)
  
  def print(self):
    print(f'Schedule(fitness={self.fitness})')
    for d in self.days:
      print(f'{d.date}:{d.cells}')
    # 労働者ごとの幸福度、勤務日数
    print(self.employees_on_duty_cnt)
    # リストAの各要素を同じインデックスのリストBの各要素で割る
    # result = [a / b for a, b in zip(A, B)]
    utility_normalized = [a / b for a, b in zip(self.employees_utility, self.employees_on_duty_cnt)]
    print([round(u,2) for u in utility_normalized])
  
  def cross(self, another):
    child = Schedule(len(self.days),self.mutation_prob,self.employees)
    for i, _ in enumerate(child.days):
        # 親の日のdeepcopyを子供の日に設定
        child.days[i] = copy.deepcopy(random.choice([self.days[i], another.days[i]]))
        if random.random() < self.mutation_prob:
            child.days[i].mutate()
    return child

  def calcFitness(self):
    # TODO
    # 週単位での希望勤務日数:
    # 割り当て区画の幸福度:
    # 出勤できない日:
    # E/NEは女性陣しかできない:
    # 個人の希望を取り入れる
    # 連勤をできるだけ防ぐ。希望勤務日数に比例するようにする。希望出勤数が多ければ連勤もやむなし

    #TODO テーブル割当はできるだけばらけるようにする:

    fitness1,fitness2,fitness3,fitness4,fitness5,fitness6 = 0,0,0,0,0,0
    weight1,weight2,weight3,weight4,weight5,weight6 = 100,3,30,10,1,10

    for i, emp in enumerate(self.employees):
      # 週単位での希望勤務日数:(100)
      # empごとにRでない記号をカウントする
      l = [d.cells[i] for d in self.days] 
      ll = list(filter(lambda x: x!="R", l)) 
      self.employees_on_duty_cnt.append(len(ll))
      # 希望とカウント数の差の絶対値を合計する
      fitness1 += abs(len(ll) - emp.on_duty_per_week/7*len(self.days))#TODO とりあえず週単位ではなく月単位での出勤予定数で評価
      
      # 割り当て区画の幸福度:(1)
      # 単純に全員の幸福度をすべて合算するアプローチ
      utility = sum([emp.plot_preference_normalized[plot] for plot in ll])
      self.employees_utility.append(utility)
      fitness2 += utility


      # 出勤できない日:(10000)
      # 一つでも当てはまったら即却下でもいいかもしれないがループを二重に抜ける必要がある
      # 即最低値にすると全個体が実践的には最低評価になってしまうので、禁止事項を満たすほどマイナスを増やしていく
      # emp一人の、つまり縦の{日付、区画}ディクショナリを作る
      list_on_duty_date = {d.date: d.cells[i] for d in self.days}
      # それがemp.date_off_dutyと被るか確認
      for d in emp.date_off_duty:
        if list_on_duty_date[d]!="R":
          fitness3 -= 1

      # E/NEは女性陣しかできない:(10000)
      # if not(emp.able_to):
      #   for d in self.days:
      #     if d.cells[i]=="E" or d.cells[i]=="NE":
      #       fitness4 -= 1

      # TODO それぞれ独自のwishを満たしているか評価
      fitness5 += emp.wish(self,i)

      # 連勤をできるだけ防ぐ。
      seq = 0
      for p in l:
        if p!="R":
          seq+=1
        else:
          fitness6 = fitness6 - (max(0,seq - emp.on_duty_per_week))**2
          seq=0



    # print(" ")
    # print(fitness1)
    # 希望とのずれが大きいほどfitnessは小さくしたいのでfitness1は逆数をとる
    if fitness1!=0:
      fitness1 = 1/fitness1
    else:
      fitness1 = 1
    # シミュレートする日数の長さに応じて補正をかける
    fitness1 = fitness1 * len(self.days)/7
    # print(fitness1)
    # print(fitness2)
    # print(fitness3)
    # print(fitness1 * weight1)
    # print(fitness2 * weight2)
    # print(fitness3 * weight3)

    total_fitness = fitness1 * weight1 + fitness2 * weight2 + fitness3 * weight3 + fitness4 * weight4 + fitness5 * weight5 + fitness6 * weight6
    # total_fitness = total_fitness * total_fitness
    # print(f'total_fitness = {total_fitness}')
    self.fitness = max(sys.float_info.epsilon,total_fitness)
    # print(f'self.fitness = {self.fitness}')
    

  def clear(self):
    self.fitness = 0
    self.employees_utility = []
    self.employees_on_duty_cnt = []



  def save_to_csv(self, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for day in self.days:
            writer.writerow(day.cells)

  @classmethod
  def load_from_csv(cls,days_cnt,mutation_prob,employees,filename):
      days_data = []
      with open(filename, 'r') as file:
          reader = csv.reader(file)
          for row in reader:
              days_data.append(row)
      return cls(days_cnt,mutation_prob,employees,days_data)