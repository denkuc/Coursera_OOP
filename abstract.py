import math
from abc import ABC, abstractmethod


class Base(ABC):
    def __init__(self, data, result):
        self.data = data
        self.result = result

    def get_answer(self):
        return [int(x >= 0.5) for x in self.data]

    def _get_common_sum(self, data, function):
        return sum([function(x, y) for (x, y) in zip(data, self.result)])

    def _get_sum_for_score(self):
        return self._get_common_sum(self.get_answer(), self._score_function)

    @abstractmethod
    def get_loss(self):
        return self._get_common_sum(self.data, self._loss_function)

    @abstractmethod
    def get_score(self):
        ...

    @abstractmethod
    def _loss_function(self, x, y):
        ...

    @abstractmethod
    def _score_function(self, x, y):
        ...


class A(Base):
    def get_score(self):
        return self._get_sum_for_score() / len(self.get_answer())

    def get_loss(self):
        return super().get_loss()

    def _loss_function(self, x, y):
        return (x - y) * (x - y)

    def _score_function(self, x, y):
        return int(x == y)


class B(Base):
    def _loss_function(self, x, y):
        return y * math.log(x) + (1 - y) * math.log(1 - x)

    def _score_function(self, x, y):
        return int(x == 1 and y == 1)

    def get_pre(self):
        return self._get_sum_for_score() / sum(self.get_answer())

    def get_rec(self):
        return self._get_sum_for_score() / sum(self.result)

    def get_loss(self):
        return -super().get_loss()

    def get_score(self):
        pre = self.get_pre()
        rec = self.get_rec()
        return 2 * pre * rec / (pre + rec)


class C(A):
    def get_loss(self):
        return super().get_loss()

    def _loss_function(self, x, y):
        return abs(x - y)

    def get_score(self):
        return super().get_score()
