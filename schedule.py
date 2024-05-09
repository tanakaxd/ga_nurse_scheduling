import copy
import csv
import random
import sys
from day import Day
from weekday import Weekday
import numpy as np

class Schedule(object):

  def __init__(self,days_cnt,mutation_prob,employees,fixed_date_plot,days_data=None):
    self.fitness = 0 #0-1の値
    self.weighted_fitness_list = []
    self.days_cnt = days_cnt
    self.mutation_prob = mutation_prob
    self.employees = employees
    self.employees_utility = []
    self.employees_on_duty_cnt = []
    self.fixed_date_plot = fixed_date_plot
    self.starting_weekday_of_month = Weekday.WEDNESDAY
    self.closed_weekday = Weekday.WEDNESDAY# 特定の日を固定で休日にする。連休などの計算に必要になる
    
    if days_data is not None:
      self.days = [Day(i+1,self.starting_weekday_of_month,self.closed_weekday,len(self.employees),day_data) for i,day_data in enumerate(days_data)]
    else:
      self.days = [Day(i+1,self.starting_weekday_of_month,self.closed_weekday,len(self.employees)) for i in range(self.days_cnt)]
      self.genetically_modify()


  def print(self):
    print(f'Schedule(fitness={self.fitness})')
    for d in self.days:
      print(f'{d.date}:{d.cells}')
    # 労働者ごとの幸福度、勤務日数
    print(f'Days_on_Duty{self.employees_on_duty_cnt})')
    print(f'Plot_Hapiness{[round(u,2) for u in self.employees_utility]})')
    print(f'Utilities_Fraction{[round(u,1) for u in self.weighted_fitness_list]})')
  
  def cross(self, another):
    # そもそもランダムな子供を生成してそれを親の遺伝子で上書きしているので、上書きをしないことは突然変異と同義
    # また、インスタンス化時点でg_modify()されているので固定区画は満たしている
    child = Schedule(len(self.days),self.mutation_prob,self.employees,self.fixed_date_plot)
    for i, _ in enumerate(child.days):
        if not random.random() < self.mutation_prob:# 突然変異したときは何もしない
            # 親の日のdeepcopyを子供の日に設定
            child.days[i] = copy.deepcopy(random.choice([self.days[i], another.days[i]]))
    return child
  
  def genetically_modify(self):
    # ディクショナリをループし、dayのcellsを書き換える
    # 固定割り当てを満たしているならばfitnessの計算を邪魔したくないので何もしない。現状はインスタンス化段階でのみの使用なので考慮しない
    # 満たしていない場合改変するがcellsの割り当てバランスを崩してはいけないので、一部固定した上でシャッフルする必要がある
    # その責任はdayクラスに持たせる
    for date,emp_plot_dict in self.fixed_date_plot.items():
      self.days[date-1].fixed_merge_shuffle(emp_plot_dict) 

  def calcFitness(self):
      # TODO
      # 週単位での希望勤務日数:
      # 割り当て区画の幸福度:
      # 出勤できない日:
      # E/NEは女性陣しかできない:
      # 個人の希望を取り入れる
      # 連勤をできるだけ防ぐ。希望勤務日数に比例するようにする。希望出勤数が多ければ連勤もやむなし
      # 全員の功利を等しく最大化したいのであれば全体のfitnessは和ではなく積で求めるべきか？
      # 全体の問題として、マイナスのfitnessとはどういう働きをするのか
      # 満たせたらうれしいことをプラスで、満たせなければならないことをマイナスで評価するのが自然ではあるが必要なことなのか

      #TODO テーブル割当はできるだけばらけるようにする:

      fitness1,fitness2,fitness3,fitness4,fitness5,fitness6,fitness7,fitness8 = 0,1,0,0,0,0,0,0
      weight1,weight2,weight3,weight4,weight5,weight6,weight7,weight8 = 50,80,30,0,10,10,10,100

      for i, emp in enumerate(self.employees):
        # 1.週単位での希望勤務日数:(100)
        # empごとにRでない記号をカウントする
        l = [d.cells[i] for d in self.days] 
        ll = list(filter(lambda x: x!="R", l)) 
        self.employees_on_duty_cnt.append(len(ll))
        # 希望とカウント数の差の絶対値を合計する
        fitness1 += abs(len(ll) - emp.on_duty_per_week/7*len(self.days))#TODO とりあえず週単位ではなく月単位での出勤予定数で評価
        
        # 2.割り当て区画の幸福度:(100)
        # 単純に全員の幸福度をすべて合算するアプローチ
        # 担当できない区画をどう表すかが課題
        # 例えば単純な和だと[0,0,5]と[1,2,2]が同価値になってしまう
        # この場合0が担当できない区画だとすると不適切になる
        # 積にしたらどうなる？
        # =>指数関数的にfitnessが増大しすぎてしまい、ほかのutilityの価値が低くなってしまう。
        # 解決策としては、plot_preference_normalizedをfraction的にする。1を基準にする？
        # 積ではなく和のままで、担当できない区画にマイナスをつける（シンプルな和ができず美しい解決法ではない）
        # また、weightを重くするのは別fitnessより優先度を重くすることはできるが、同カテゴリー内での序列付けとしては機能しないことを留意せよ
        # [0,0,5][1,2,2]を[0,0,10][2,4,4]としても全体の功利には変化がない
        utility = np.prod([emp.plot_preference_normalized[plot] for plot in ll])
        self.employees_utility.append(utility)
        fitness2 *= utility

        # # 3.出勤できない日:(30)
        # # scheduleインスタンスがインスタンス化されるときに休み希望を考慮している。
        # # そのあと交配時に突然変異で塗り替えられる可能性はあるが、ここでつまりfitness計算時にネガティブな補正がつけられる。
        # # 二重に処理しているともいえるが、初期化時の処理は進化の促進ととらえることもできる。
        # # 
        # # 一つでも当てはまったら即却下でもいいかもしれないがループを二重に抜ける必要がある
        # # 即最低値にすると全個体が実践的には最低評価になってしまうので、禁止事項を満たすほどマイナスを増やしていく
        # # emp一人の、つまり縦の{日付、区画}ディクショナリを作る
        # list_on_duty_date = {d.date: d.cells[i] for d in self.days}
        # # それがemp.date_off_dutyと被るか確認
        # for d in emp.date_off_duty:
        #   if list_on_duty_date[d]!="R":
        #     fitness3 -= 1

        # 4.

        # 5.それぞれ独自のwishを満たしているか評価:(1)TODO 
        fitness5 += emp.wish(self,i)

        # 6.連勤をできるだけ防ぐ:(10)
        seq = 0
        for p in l:
          if p!="R":
            seq+=1
          else:
            fitness6 -= (max(0,seq - emp.on_duty_per_week))**2
            seq=0
        
        # 7.bored system 同じ区画の連続をできるだけ防ぐ:(0.5)
        bored = 0
        threshold = 3
        previous = None
        for p in ll:
          if previous == p:
            bored+=1
            fitness7 -= max(0,bored-threshold)
          else:
            bored=0
          previous = p

      # 8.固定区画を満たしているか評価：
      # シフト全体で一度に見ることができるので、empループ内で処理する必要はない
      # {5:{3:"C",5:"C"},6:{3:"C",5:"C"},7:{3:"C",5:"C"}}
      for date,emp_plot_dict in self.fixed_date_plot.items():
        for emp_index, plot in emp_plot_dict.items():
          if self.days[date-1].cells[emp_index] != plot:
            fitness8 -= 1


      # 希望とのずれが大きいほどfitnessは小さくしたいのでfitness1は逆数をとる
      if fitness1!=0:
        fitness1 = 1/fitness1
      else:
        fitness1 = 1
      # シミュレートする日数の長さに応じて補正をかける
      fitness1 = fitness1 * len(self.days)/7

      fitness_list = [fitness1,fitness2,fitness3,fitness4,fitness5,fitness6,fitness7,fitness8]
      weight_list = [weight1,weight2,weight3,weight4,weight5,weight6,weight7,weight8]
      self.weighted_fitness_list = [f*w for f,w in zip(fitness_list,weight_list)]
      total_fitness = sum(self.weighted_fitness_list)
      # print(f'total_fitness = {total_fitness}')
      self.fitness = max(sys.float_info.epsilon,total_fitness)#0以下にならないように処理。全個体が０以下になると子孫を残せなくなる
      # print(f'self.fitness = {self.fitness}')
    

  def clear(self):
    self.fitness = 0
    self.weighted_fitness_list = []
    self.employees_utility = []
    self.employees_on_duty_cnt = []


  def save_to_csv(self, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        for day in self.days:
            writer.writerow(day.cells)

  @classmethod
  def load_from_csv(cls,days_cnt,mutation_prob,employees,fixed_date_plot,filename):
      days_data = []
      with open(filename, 'r') as file:
          reader = csv.reader(file)
          for row in reader:
              days_data.append(row)
      print("loaded successfully")
      return cls(days_cnt,mutation_prob,employees,fixed_date_plot,days_data)