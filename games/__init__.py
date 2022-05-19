# 2022/5/10  19:55  liujiaqi
from utils.registry import Registry

GAME_REGISTRY = Registry("GAMES")
GAME_REGISTRY.__doc__ = """
Registry for games
It must returns an instance of :class:`Game`.
"""

from .splendor import Splendor
