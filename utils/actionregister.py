# 2022/5/16  15:23  liujiaqi
from collections import Iterable


class ActionRegister:  # 改个名 ActionRegister
    def __init__(self):
        self.actions = {}
        self.desc = []

    def register_action(self, item, method, action_desc=None):
        if not isinstance(method, type(self.__init__)):
            raise ValueError(f"Value Type [{type(method)}] is not a class method")
        if isinstance(item, str):
            self.actions[item] = method
        elif isinstance(item, Iterable):
            for i in item:
                self.actions[i] = method

        if action_desc is not None:
            self.desc.append((item, action_desc))

    def __call__(self, action: str):
        ins, args = self.parse_action(action)
        self.actions[ins](*args)

    def all_actions(self):
        desc_all = ''
        for item, desc in self.desc:
            if isinstance(item, str):
                msg = f"[{item}]. {desc}\n"
            else:
                msg = ''
                for i in item:
                    msg += f"[{i}],"
                msg = msg[:-1] + f'. {desc}\n'
            desc_all += msg
        return desc_all

    def try_parse_action(self, action):
        try:
            self.parse_action(action)
            return True
        except:
            return False

    def try_action(self, action):
        try:
            ins, args = self.parse_action(action)
            self.actions[ins](*args)
            return True
        except:
            return False

    def parse_action(self, action):
        info = action.split()
        if len(info) == 0:
            raise ValueError('Empty action.')
        ins = info.pop(0)
        args = tuple(info)
        if ins not in self.actions:
            raise ValueError(f'class {type(self).__name__}: action [{ins}] is not exist.')
        return ins, args

    def __str__(self):
        return self.all_actions()
