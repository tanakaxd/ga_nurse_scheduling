import random

from weekday import Weekday

class Day(object):
  def __init__(self,date,starting_weekday_of_month,closed_weekday,emp_cnt,cells=None):
    self.date = date
    self.weekday = Weekday.weekday_from_date(starting_weekday_of_month,self.date)
    self.is_closed_day = self.weekday == closed_weekday
    self.emp_cnt = emp_cnt
    if cells is not None:
      self.cells = cells
    elif self.is_closed_day:
      self.cells = ["R" for _ in range(self.emp_cnt)]
    else:
      candidates = ["A","B","C","E","NE"]
      while len(candidates)<self.emp_cnt:
        candidates.append("R")
      random.shuffle(candidates)
      self.cells = candidates

  def mutate(self):
    # mutationをもっと革新的にする必要があるかも
    # 1.全く新しいcellsを生み出すこと
    # 2.オーソドックスなcells以外の例えばダブり持ちcellsがほしい => 現時点では実装しない。ダブりなどは固定上書きでfitness度外視で絶対実現する方針
    idx1, idx2 = random.sample(range(len(self.cells)), 2)
    # 選択した2つの要素を入れ替え
    self.cells[idx1], self.cells[idx2] = self.cells[idx2], self.cells[idx1]

  def fixed_R_shuffle(self,fixed_indeces):
    # cellsから固定するR要素を休み希望人数分除去する
    for _ in range(len(fixed_indeces)):
      self.cells.remove("R")
    # リストをシャッフル
    random.shuffle(self.cells)
    # シャッフルしたリストに固定する要素を挿入
    for i in sorted(fixed_indeces):
        self.cells.insert(i, "R")

  def fixed_plot_shuffle(self,fixed_indeces,plot):
    self.dup_plot(plot)
    while plot in self.cells:
      self.cells.remove(plot)
    random.shuffle(self.cells)
    for i in sorted(fixed_indeces):
        self.cells.insert(i, plot)

  def fixed_merge_shuffle(self,emp_plot_dict):#{3:"C",5:"C",6:"R"}
    
    # cellsの最低要件は区画ごとに最低一人の担当者が存在すること
    elements = ["A", "B", "C", "E", "NE"]
    array = ["X"] * self.emp_cnt
    # 指定されたインデックスに要素を配置
    for emp_index, plot in emp_plot_dict.items():
        array[emp_index] = plot
        if plot in elements:
            elements.remove(plot)

    # 残りの要素をランダムに配置
    for plot in elements:
        while True:
            index = random.randint(0, self.emp_cnt-1)
            if array[index] == "X":
                array[index] = plot
                break
    
    # Xが残っていた場合Rで置換
    for i,e in enumerate(array):
        if e == "X":
            array[i]="R"

    self.cells = array
    
    
  def dup_plot(self,plot):
    while len([cell for cell in self.cells if cell==plot])<2:
      self.cells.remove("R")
      self.cells.append(plot)