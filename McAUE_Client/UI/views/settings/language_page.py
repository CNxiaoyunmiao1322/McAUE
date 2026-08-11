"""语言设置页面。"""

import flet as ft

from components.animation import SmoothScroll
from state.config import config
from ._common import build_section_title, build_setting_row, make_dropdown


def build_language_page(page):
    lc = config.get("language")
    lang_dropdown = make_dropdown(page, lc.get("interface", "简体中文"), [
        ft.dropdown.Option("简体中文"),
        ft.dropdown.Option("English"),
        ft.dropdown.Option("日本語"),
    ])
    lang_dropdown.on_select = lambda e: config.set("language", "interface", e.control.value)

    region_dd = make_dropdown(page, lc.get("region", "zh_cn"), [
        ft.dropdown.Option("zh_cn", "简体中文"),
        ft.dropdown.Option("en_us", "English (US)"),
        ft.dropdown.Option("ja_jp", "日本語"),
        ft.dropdown.Option("lzh", "文言文"),
    ])
    region_dd.on_select = lambda e: config.set("language", "region", e.control.value)

    return SmoothScroll(
        page=page,
        controls=[
            build_section_title(page, "语言", ft.Icons.LANGUAGE_OUTLINED),
            build_setting_row(page, "界面语言", "选择启动器界面显示语言", lang_dropdown),
            build_setting_row(page, "区域格式", "Minecraft 游戏内区域格式", region_dd),
        ],
        spacing=8,
        expand=True,
    )
