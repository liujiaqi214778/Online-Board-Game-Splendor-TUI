# 2022/5/16  15:23  liujiaqi
from collections import Iterable


class Reactor:
    def __init__(self):
        self.actions = {}

    def register_action(self, item, method):
        if not isinstance(method, type(self.__init__)):
            raise ValueError(f"Value Type [{type(method)}] is not a class method")
        if isinstance(item, str):
            self.actions[item] = method
        elif isinstance(item, Iterable):
            for i in item:
                self.actions[i] = method

    def __call__(self, action: str):
        info = action.split()
        if len(info) == 0:
            raise ValueError('Empty action.')
        ins = info.pop(0)
        args = tuple(info)
        if ins not in self.actions:
            raise ValueError(f'Action [{ins}] is not exist.')
        self.actions[ins](*args)
