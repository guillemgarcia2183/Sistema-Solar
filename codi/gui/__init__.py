# -*- coding: utf-8 -*- noqa
"""
Created on Tue Oct 22 15:55:23 2024

@author: Joel Tapia Salvador
"""
import sys

from .button_manager import ButtonManager

if sys.version_info[0] < 3:
    raise RuntimeError("Python version lower than 3.")

if sys.version_info[1] < 9:
    raise RuntimeError("Pythoin version lower than 3.9.")
