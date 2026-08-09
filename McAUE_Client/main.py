"""McAUE - Minecraft 客户端 UI 入口。

可从项目根目录直接运行：
    python main.py
"""

import sys
import os

ui_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "UI")
sys.path.insert(0, ui_dir)

import flet as ft
from app import run_app


if __name__ == "__main__":
    ft.run(run_app)
