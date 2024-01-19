import random

from weekday import Weekday

class Day(object):
  def __init__(self,date,starting_weekday_of_month,closed_weekday):
    candidates = ["A","B","C","E","NE","R","R"]
    random.shuffle(candidates)
    self.cells = candidates
    self.date = date
    self.weekday = Weekday.weekday_from_date(starting_weekday_of_month,self.date)
    self.is_closed_day = False
    if(self.weekday == closed_weekday):
      self.is_closed_day = True
      self.cells = ["R" for _ in candidates]
  def mutate(self):
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
