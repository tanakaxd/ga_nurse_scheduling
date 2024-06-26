import os
import random
from employee import Employee
from shimura import Shimura
from schedule import Schedule
from constants import CSV_NAME_CACHE, CSV_NAME_LOAD, CSV_NAME_SAVE, DAYS, ELITISM, EMPLOYEES, FIXED_DATE_PLOT, LOAD, MUTPB, NGEN, DATA_DIRECTORY, POP, SAVE_TO_CACHE

import matplotlib.pyplot as plt

#TODO
# スケジュール部分固定の実装 
# => 交配結果を部分的に固定する？fitness計算では配慮しないのであれば、突然変異処理の後でなければならない
# 休日希望日のようにインスタンス化の際に固定で作り、交配には関与せず、fitnessで評価するのがGAとして一貫していてよさそう
# 問題点
# キャッシュされたスケジュールが固定区画条件を満たしていなかった場合
# それにもかかわらずランダムに生成されたスケジュールよりはるかに高いfitnessをもっているため交配時に支配的になり、固定区画条件を満たしているスケジュールを淘汰してしまうこと
# 解決策
# mutation
# そもそも「固定する」ということはそれ以外を許さないのだからfitnessでいうならば無限大といえるので、ほかの要素と比較できるような形態にするのが間違っているのかもしれない
# 固定区画が存在する日は要望通りの区画数割当にしたうえで、ランダムに変異交配させるという手もある。
# 多分一番妥当なのが、FIXED_DATE_PLOTに固定区画と休日希望を両方反映したうえで、交配後のスケジュールをそれに基づいて書き換えることか？
# そしてfitnessの計算式から除外すべきかもしれない

# 労働者相性の実装
# LONGの実装
# preferenceの再ロード => fitnessの計算部分を作り替えると構造上かなり抜本的変更が必要になるが、wishで個別に別レイヤーを使って実現は可能。とりあえずは固定シフトで様子見

# 乱数を固定
# random.seed(64)
pop = []

if LOAD and os.path.exists(CSV_NAME_LOAD):
  loaded_sche = Schedule.load_from_csv(DAYS,MUTPB,EMPLOYEES,FIXED_DATE_PLOT,CSV_NAME_LOAD)
  loaded_sche.calcFitness()
  loaded_sche.print()
  pop.append(loaded_sche)

while len(pop)<POP:
  pop.append(Schedule(DAYS,MUTPB,EMPLOYEES,FIXED_DATE_PLOT))
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
if SAVE_TO_CACHE:
  hall_of_fame.save_to_csv(CSV_NAME_CACHE) 

# 出力したいファイル名
if not os.path.exists(DATA_DIRECTORY):
    os.makedirs(DATA_DIRECTORY)
base_filename = CSV_NAME_SAVE
extension = '.csv'
filename = base_filename + extension

# 同名のファイルが存在する場合、末尾の番号を増加
counter = 1
while os.path.exists(filename):
    filename =  f"{base_filename}_{counter}{extension}"
    counter += 1
hall_of_fame.save_to_csv(filename) 
print(f'saved to :{filename}')


plt.plot(average_fitness_history)
plt.plot(gen_max_fit_history)
plt.title("MAX/AVE FITNESS to GENERATION")
plt.xlabel("Gen")
plt.ylabel("Fit")
# 出力したいファイル名
base_filename = 'ga_nurse_scheduling\\data\\charts\\fitness_graph'
extension = '.png'
filename = base_filename + extension

# 同名のファイルが存在する場合、末尾の番号を増加
counter = 1
while os.path.exists(filename):
    filename = f"{base_filename}_{counter}{extension}"
    counter += 1

# グラフを画像ファイルとして保存
plt.savefig(filename)
# plt.show()