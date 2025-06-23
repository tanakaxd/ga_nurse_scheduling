import os
import random
from employee import Employee
from shimura import Shimura
from advance import Advance
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

def print_system_initialization():
    """
    システム初期化時の設定情報を表示
    """
    print("=" * 80)
    print("🤖 遺伝的アルゴリズム看護師スケジューリングシステム")
    print("=" * 80)
    
    # GAパラメータ情報
    print("\n📊 GAアルゴリズム設定:")
    print(f"   世代数:     {NGEN:,} 世代")
    print(f"   個体数:     {POP:,} 個体")
    print(f"   突然変異率: {MUTPB*100:.1f}%")
    print(f"   エリート数: {ELITISM} 個体")
    print(f"   日数:       {DAYS} 日")
    
    # 従業員情報
    print(f"\n👥 従業員情報 (計 {len(EMPLOYEES)} 名):")
    
    # カテゴリ別分類
    regular_employees = [emp for emp in EMPLOYEES if isinstance(emp, Employee) and not isinstance(emp, (Shimura, Advance))]
    shimura_employees = [emp for emp in EMPLOYEES if isinstance(emp, Shimura)]
    advance_employees = [emp for emp in EMPLOYEES if isinstance(emp, Advance)]
    
    print(f"   通常従業員: {len(regular_employees)} 名")
    print(f"   Shimura:   {len(shimura_employees)} 名")
    print(f"   Advance:   {len(advance_employees)} 名")
    
    # 詳細情報
    print("\n📋 従業員詳細:")
    total_desired_hours = 0
    total_regular_hours = 0
    
    for emp in EMPLOYEES:
        emp_type = ""
        if isinstance(emp, Advance):
            emp_type = "[Advance]"
        elif isinstance(emp, Shimura):
            emp_type = "[Shimura]"
        else:
            emp_type = "[通常]"
            
        # 希望勤務日数を計算（月単位）
        monthly_desired = emp.on_duty_per_week / 7 * DAYS
        total_desired_hours += monthly_desired
        
        # Advanceクラス以外の希望勤務時間を別途計算
        if not isinstance(emp, Advance):
            total_regular_hours += monthly_desired
            
        print(f"   {emp.name:8} {emp_type:10} 希望: {emp.on_duty_per_week:4.1f}日/週 ({monthly_desired:5.1f}日/月)")
    
    # 勤務日数統計
    print(f"\n📈 勤務日数統計:")
    print(f"   全従業員希望勤務日数合計:     {total_desired_hours:6.1f} 日/月")
    print(f"   通常従業員希望勤務日数合計:   {total_regular_hours:6.1f} 日/月")
    print(f"   Advance従業員希望勤務日数:    {total_desired_hours - total_regular_hours:6.1f} 日/月")
    
    # 必要勤務日数の計算
    required_daily_staff = 5  # A,B,C,E,NEの5区画
    closed_days = sum(1 for d in range(DAYS) if (d % 7) == 2)  # 水曜日（閉店日）
    working_days = DAYS - closed_days
    total_required = required_daily_staff * working_days
    
    print(f"   必要勤務日数 ({required_daily_staff}人×{working_days}営業日): {total_required:6} 日/月")
    print(f"   需給バランス:                   {total_desired_hours - total_required:+6.1f} 日/月")
    
    # 区画制約情報
    unavailable_constraints = 0
    for emp in EMPLOYEES:
        unavailable_count = sum(1 for pref in emp.plot_preference.values() if pref == -100)
        unavailable_constraints += unavailable_count
    
    print(f"\n🚫 制約情報:")
    print(f"   区画制約総数: {unavailable_constraints} 個 (従業員が担当できない区画)")
    
    # 固定区画情報
    fixed_assignments = sum(len(day_dict) for day_dict in FIXED_DATE_PLOT.values())
    print(f"   固定区画数:   {fixed_assignments} 個")
    
    # キャッシュとファイル情報
    print(f"\n💾 ファイル設定:")
    print(f"   キャッシュ読込: {'有効' if LOAD else '無効'}")
    print(f"   キャッシュ保存: {'有効' if SAVE_TO_CACHE else '無効'}")
    print(f"   読込ファイル:   {CSV_NAME_LOAD if LOAD and os.path.exists(CSV_NAME_LOAD) else '無し'}")
    print(f"   出力ディレクトリ: {DATA_DIRECTORY}")
    
    print("=" * 80)
    print("🚀 最適化開始\n")

# システム初期化情報を表示
print_system_initialization()

# 乱数を固定
# random.seed(64)
pop = []

if LOAD and os.path.exists(CSV_NAME_LOAD):
  loaded_sche = Schedule.load_from_csv(days_cnt=DAYS, mutation_prob=MUTPB, employees=EMPLOYEES, fixed_date_plot=FIXED_DATE_PLOT, filename=CSV_NAME_LOAD)
  loaded_sche.calcFitness()
  loaded_sche.print()
  pop.append(loaded_sche)

while len(pop)<POP:
  pop.append(Schedule(days_cnt=DAYS, mutation_prob=MUTPB, employees=EMPLOYEES, fixed_date_plot=FIXED_DATE_PLOT))
gen_cnt = 0
average_fitness_history = []
gen_max_fit_history = []
hall_of_fame = None
hof_gen = 0

for i in range(NGEN):

  # 進捗表示を改善
  if gen_cnt % 100 == 0 or gen_cnt < 10:
    print(f'🔄 第{gen_cnt:4d}世代 / {NGEN}世代')
  elif gen_cnt % 50 == 0:
    print(f'   第{gen_cnt:4d}世代')

  # fitness function
  for s in pop:
    s.calcFitness()
  fitness_list = [s.fitness for s in pop]
  max_fit = max(fitness_list)
  gen_max_fit_history.append(max_fit)
  ave = sum(fitness_list)/POP
  average_fitness_history.append(ave)
  fittest_schedule = pop[fitness_list.index(max_fit)]
  
  # 詳細表示は最初の10世代と100世代ごと
  if gen_cnt % 100 == 0:
    print(f'   平均適応度: {ave:8.6f}  最大適応度: {max_fit:8.6f}')
    fittest_schedule.print()
  
  # 殿堂入りの更新
  if hall_of_fame==None:
    hall_of_fame = fittest_schedule
    hof_gen = gen_cnt
  elif hall_of_fame.fitness<fittest_schedule.fitness:
    hall_of_fame = fittest_schedule
    hof_gen = gen_cnt
    print(f'🏆 新記録！第{gen_cnt}世代で適応度 {fittest_schedule.fitness:.6f} を達成')

  # intercourse
  probabilities = [s.fitness**2 for s in pop]
  probabilities = [p/sum(probabilities) for p in probabilities]
  new_pop = []
  hall_of_fame.clear()
  new_pop.append(hall_of_fame)# エリートを直接引き継ぐ
  for j in range(POP-ELITISM):# エリートを除外
    pairs = random.choices(pop, weights=probabilities, k=2)
    child = pairs[0].cross(another=pairs[1])
    new_pop.append(child)
  pop = new_pop
  gen_cnt+=1

print("\n" + "=" * 80)
print("🏆 最終結果 - 殿堂入りスケジュール")
print("=" * 80)
print(f'最良世代: 第{hof_gen}世代')
print(f'最終適応度: {hall_of_fame.fitness:.6f}')
hall_of_fame.calcFitness()
hall_of_fame.print()
if SAVE_TO_CACHE:
  hall_of_fame.save_to_csv(filename=CSV_NAME_CACHE) 

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
hall_of_fame.save_to_csv(filename=filename) 
print(f'\n💾 スケジュール保存完了: {filename}')
print(f'📊 フィットネスグラフ保存準備中...')


plt.plot(average_fitness_history)
plt.plot(gen_max_fit_history)
plt.title("MAX/AVE FITNESS to GENERATION")
plt.xlabel("Gen")
plt.ylabel("Fit")
# 出力したいファイル名
base_filename = '/home/ttnk0/projects/ga_nurse_scheduling/data/charts/fitness_graph'
extension = '.png'
filename = base_filename + extension

# 同名のファイルが存在する場合、末尾の番号を増加
counter = 1
while os.path.exists(filename):
    filename = f"{base_filename}_{counter}{extension}"
    counter += 1

# グラフを画像ファイルとして保存
plt.savefig(filename)
print(f'📈 フィットネスグラフ保存完了: {filename}')
print("\n🎉 最適化完了！")
# plt.show()