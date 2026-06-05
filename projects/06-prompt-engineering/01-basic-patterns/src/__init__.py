"""
基础Prompt模式包
"""
from .zero_shot import ZeroShotPattern
from .few_shot import FewShotPattern
from .role_playing import RolePlayingPattern
from .chain_of_thought import ChainOfThoughtPattern

__all__ = [
    "ZeroShotPattern",
    "FewShotPattern",
    "RolePlayingPattern",
    "ChainOfThoughtPattern",
]
