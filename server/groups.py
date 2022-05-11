# 2022/5/12  0:38  liujiaqi
from group import Group


class Groups:
    MaxN = 30

    def __init__(self):
        self.groups = [Group(i, Board) for i in range(4)]

    def create(self):
        if len(self.groups) == self.MaxN:
            return -1
        self.groups.append(Group(len(self.groups), Board))
        return 0

    def __getitem__(self, item):
        return self.groups[item]

    def __len__(self):
        return len(self.groups)