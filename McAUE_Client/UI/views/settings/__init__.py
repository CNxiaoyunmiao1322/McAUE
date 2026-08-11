"""设置视图包 - 二级菜单导航，含启动/Java/管理/联机/个性化/语言/杂项/软件更新。

所有设置控件与 config.py 集成，自动持久化到 JSON 配置文件。
按钮点击处理器已实现 UI 层功能，核心模块接口预留。
"""

import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar
from components.animation import tab_switcher
from state.config import config

from ._common import get_memory_info
from .launch_page import build_launch_page
from .java_page import build_java_page
from .manage_page import build_manage_page
from .multiplayer_page import build_multiplayer_page
from .personalize_page import build_personalize_page
from .language_page import build_language_page
from .misc_page import build_misc_page
from .update_page import build_update_page


SETTINGS_TABS = [
    ("launch", "启动", ft.Icons.ROCKET_LAUNCH_OUTLINED),
    ("java", "Java", ft.Icons.COFFEE_OUTLINED),
    ("manage", "管理", ft.Icons.FOLDER_OUTLINED),
    ("multiplayer", "联机", ft.Icons.WIFI_OUTLINED),
    ("personalize", "个性化", ft.Icons.PALETTE_OUTLINED),
    ("language", "语言", ft.Icons.LANGUAGE_OUTLINED),
    ("misc", "杂项", ft.Icons.TUNE_OUTLINED),
    ("update", "软件更新", ft.Icons.SYSTEM_UPDATE_ALT_OUTLINED),
]


def _build_tab_content(page, tab_id, state, total_mem, used_mem, theme_mode, on_set_theme, on_logout) -> ft.Control:
    """根据当前选中的标签页构建内容。"""
    if tab_id == "launch":
        return build_launch_page(page, total_mem, used_mem)
    elif tab_id == "java":
        return build_java_page(page)
    elif tab_id == "manage":
        return build_manage_page(page, state, on_logout)
    elif tab_id == "multiplayer":
        return build_multiplayer_page(page)
    elif tab_id == "personalize":
        return build_personalize_page(page, theme_mode, on_set_theme)
    elif tab_id == "language":
        return build_language_page(page)
    elif tab_id == "misc":
        return build_misc_page(page)
    elif tab_id == "update":
        return build_update_page(page)
    return ft.Container()


def build_settings_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_set_theme=None,
    on_user_click=None,
    on_logout=None,
    theme_mode="dark",
    **kwargs,
) -> list:
    """构建设置视图 - 左侧二级菜单 + 右侧内容区。"""
    c = Colors.from_page(page)
    total_mem, used_mem = get_memory_info()

    current_tab = {"value": state.settings_tab}

    nav_items = []
    nav_icons = {}

    def select_tab(tab_id):
        if current_tab["value"] == "launch" and tab_id != "launch":
            if hasattr(page, "_mem_stop") and page._mem_stop:
                page._mem_stop["active"] = False
                page._mem_stop = None
        current_tab["value"] = tab_id
        state.settings_tab = tab_id
        for tid, icon in nav_icons.items():
            active = tid == tab_id
            icon.color = "#FFFFFF" if active else c["on_surface_variant"]
            try:
                icon.update()
            except Exception:
                pass
        for tid, btn in nav_containers.items():
            active = tid == tab_id
            btn.bgcolor = c["primary"] if active else c["surface_variant"]
            try:
                btn.update()
            except Exception:
                pass
        new_content = _build_tab_content(page, tab_id, state, total_mem, used_mem, theme_mode, on_set_theme, on_logout)
        new_content.key = f"tab_{tab_id}"
        content_switcher.content = new_content
        try:
            content_switcher.update()
        except Exception:
            pass

    nav_containers = {}
    for tab_id, label, icon_name in SETTINGS_TABS:
        active = tab_id == current_tab["value"]
        ic = ft.Icon(icon_name, color="#FFFFFF" if active else c["on_surface_variant"], size=18)
        txt = ft.Text(label, size=13, color="#FFFFFF" if active else c["on_surface"], weight=ft.FontWeight.W_500)
        nav_icons[tab_id] = ic
        btn = ft.Container(
            content=ft.Row([ic, txt], spacing=8),
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            border_radius=8,
            bgcolor=c["primary"] if active else c["surface_variant"],
            ink=True,
            on_click=lambda e, tid=tab_id: select_tab(tid),
        )
        nav_containers[tab_id] = btn
        nav_items.append(btn)

    sidebar = ft.Container(
        content=ft.Column(
            controls=nav_items,
            spacing=4,
        ),
        padding=ft.Padding(8, 8, 8, 8),
        bgcolor=c["surface"],
        border_radius=12,
        width=140,
    )

    _initial_content = _build_tab_content(page, current_tab["value"], state, total_mem, used_mem, theme_mode, on_set_theme, on_logout)
    _initial_content.key = f"tab_{current_tab['value']}"

    content_switcher = tab_switcher(_initial_content, key=f"tab_{current_tab['value']}")

    body = ft.Row(
        controls=[sidebar, content_switcher],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,
        expand=True,
    )

    content = ft.Column(
        controls=[
            build_topbar(
                page,
                "设置",
                state.username,
                state.logged_in,
                on_toggle_theme,
                on_user_click,
            ),
            ft.Container(height=4),
            body,
        ],
        spacing=8,
        expand=True,
    )

    return [content]
