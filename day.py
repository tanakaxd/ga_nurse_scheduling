import random

class Day(object):
  def __init__(self):
    candidates = ["A","B","C","R","R"]
    random.shuffle(candidates)
    self.cells = candidates
  def mutate(self):
    idx1, idx2 = random.sample(range(len(self.cells)), 2)
    # 選択した2つの要素を入れ替え
    self.cells[idx1], self.cells[idx2] = self.cells[idx2], self.cells[idx1]
