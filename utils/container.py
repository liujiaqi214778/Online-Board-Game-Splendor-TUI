# 2022/5/8  14:44  liujiaqi
import json


class Container(object):
    def __init__(self):
        self._buffers = {}

    def __getattr__(self, item: str):
        if '_buffers' in self.__dict__:
            _buffers = self.__dict__['_buffers']
            if item in _buffers:
                return _buffers[item]
        raise AttributeError("'{}' object has no attribute '{}'".format(
            type(self).__name__, item))

    def __setattr__(self, key: str, value):
        _buffers = self.__dict__.get('_buffers')
        if _buffers is not None:
            _buffers[key] = value
        else:
            object.__setattr__(self, key, value)

    def __delattr__(self, item):
        if item in self._buffers:
            del self._buffers[item]
        else:
            object.__delattr__(self, item)

    def __str__(self):
        return json.dumps(self._buffers)
