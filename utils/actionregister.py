# 2022/5/16  15:23  liujiaqi

class SimpleTransform:
    @staticmethod
    def loads(s):
        if isinstance(s, str):
            s = s.split()
        key = s[0]
        args = tuple(s[1:])
        return key, args, {}

    @staticmethod
    def dumps(key, *args, **kwargs):
        return ' '.join((key, *args))


class StructTransform:
    def __init__(self, parser):
        self.parser = parser  # json, pickle ...

    def loads(self, s):
        obj = self.parser.loads(s)
        key = obj['key']
        args = tuple(obj['args'])
        kwargs = dict(obj['kwargs'])  # 如果不是dict请实现 keys() 和 __getitem__()
        return key, args, kwargs

    def dumps(self, key, *args, **kwargs):
        return self.parser.dumps({'key': key, 'args': args, 'kwargs': kwargs})


class ActionRegister:
    def __init__(self, transform=SimpleTransform):
        self._actions = {}
        self._desc = []
        self._transform = transform

    def register_action(self, item, func, action_desc=None):
        if not callable(func):
            raise TypeError(f"{type(self).__name__}: '{func}' object is not callable")
        if isinstance(item, tuple) or isinstance(item, list):
            for i in item:
                self._actions[i] = func
        else:
            self._actions[item] = func

        if action_desc is not None:
            self._desc.append((item, action_desc))

    def __call__(self, action):
        key, args, kwargs = self.parse_action(action)
        self._actions[key](*args, **kwargs)

    def all_actions(self):
        desc_all = ''
        for item, desc in self._desc:
            if isinstance(item, tuple) or isinstance(item, list):
                msg = ''
                for i in item:
                    msg += f"[{i}],"
                msg = msg[:-1] + f'. {desc}\n'
            else:
                msg = f"[{item}]. {desc}\n"
            desc_all += msg
        return desc_all

    def try_action(self, action, **kwargs):
        try:
            key, args, kwargs = self.parse_action(action, **kwargs)
            self._actions[key](*args, **kwargs)
            return True
        except:
            return False

    '''def parse_action(self, action):
        if isinstance(action, str):
            action = action.split()
            if len(action) == 0:
                raise ValueError('Empty action.')
        elif not isinstance(action, tuple):
            raise TypeError(f'class {type(self).__name__}: action [{action}] is not a str or a tuple.')
        ins = action[0]
        args = action[1:]
        if ins not in self._actions:
            raise ValueError(f'class {type(self).__name__}: action [{ins}] not registered.')
        return ins, args, {}'''

    def parse_action(self, action, transform=None):
        if transform is None:
            transform = self._transform
        key, args, kwargs = transform.loads(action)
        if key not in self._actions:
            raise Warning(f'{type(self).__name__}: action [{key}] not registered.')
        return key, args, kwargs

    def __str__(self):
        return self.all_actions()
