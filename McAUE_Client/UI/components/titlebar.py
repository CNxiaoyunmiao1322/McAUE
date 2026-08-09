"""PCL2 风格自定义标题栏 - 替代系统标题栏。"""

import os
import flet as ft

from theme.colors import Colors


def _win_btn(icon, tooltip, on_click, icon_color="#FFFFFF", hover_color=None) -> ft.Control:
    state = {"hover": False}

    btn = ft.Container(
        content=ft.Icon(icon, color=icon_color, size=16),
        width=40,
        height=36,
        alignment=ft.Alignment.CENTER,
        ink=True,
        tooltip=tooltip,
        on_click=on_click,
    )

    def on_hover(e):
        state["hover"] = e.data == "true"
        btn.bgcolor = hover_color if state["hover"] else None
        btn.update()

    btn.on_hover = on_hover
    return btn


def build_titlebar(page: ft.Page) -> ft.Control:
    """构建自定义标题栏（随主题切换颜色）。"""
    c = Colors.from_page(page)
    is_light = page.theme_mode == ft.ThemeMode.LIGHT
    icon_color = c["on_surface"]
    hover_color = "#00000010" if is_light else "#FFFFFF20"
    win_state = {"maximized": page.window.maximized if hasattr(page.window, "maximized") else False}

    # 左侧：Logo + 名称
    left_area = ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, color=icon_color, size=18),
                width=32,
                height=32,
                border_radius=8,
                alignment=ft.Alignment.CENTER,
            ),
            ft.Text(
                "McAUE",
                size=14,
                weight=ft.FontWeight.BOLD,
                color=icon_color,
            ),
        ],
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # 可拖拽区域：左侧 logo + 中间空白区，整条标题栏均可拖动
    drag_area = ft.WindowDragArea(
        content=ft.Container(
            content=ft.Row(
                controls=[
                    left_area,
                    ft.Container(expand=True),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, right=8, top=0, bottom=0),
            expand=True,
        ),
        maximizable=True,
        expand=True,
    )

    # 右侧：窗口控制按钮
    def do_minimize(e):
        page.window.minimized = True
        page.update()

    def do_maximize(e):
        win_state["maximized"] = not win_state["maximized"]
        page.window.maximized = win_state["maximized"]
        max_btn.content.icon = (
            ft.Icons.FILTER_NONE_OUTLINED
            if win_state["maximized"]
            else ft.Icons.SQUARE_OUTLINED
        )
        page.update()

    async def _do_close_async():
        try:
            await page.window.close()
        except Exception:
            pass
        os._exit(0)

    def do_close(e):
        page.run_task(_do_close_async)

    min_btn = _win_btn(
        ft.Icons.HORIZONTAL_RULE,
        "最小化",
        do_minimize,
        icon_color=icon_color,
        hover_color=hover_color,
    )

    max_btn = _win_btn(
        ft.Icons.SQUARE_OUTLINED,
        "最大化",
        do_maximize,
        icon_color=icon_color,
        hover_color=hover_color,
    )

    close_btn = _win_btn(
        ft.Icons.CLOSE,
        "关闭",
        do_close,
        icon_color=icon_color,
        hover_color="#E53935",
    )

    # 窗口事件：同步最大化状态
    def on_window_event(e):
        if e.data == "maximize":
            win_state["maximized"] = True
            max_btn.content.icon = ft.Icons.FILTER_NONE_OUTLINED
            page.update()
        elif e.data == "unmaximize":
            win_state["maximized"] = False
            max_btn.content.icon = ft.Icons.SQUARE_OUTLINED
            page.update()

    page.window.on_event = on_window_event

    return ft.Container(
        content=ft.Row(
            controls=[
                drag_area,
                min_btn,
                max_btn,
                close_btn,
            ],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        height=36,
        bgcolor=c["surface"],
        border=ft.Border(
            bottom=ft.BorderSide(1, c["outline_variant"]),
        ),
    )
