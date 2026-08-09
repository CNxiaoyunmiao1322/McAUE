"""顶部栏组件 - 包含标题、主题切换、用户信息（可点击登录）。"""

import flet as ft

from theme.colors import Colors


def build_topbar(
    page: ft.Page,
    title: str,
    username: str = "",
    logged_in: bool = False,
    on_toggle_theme=None,
    on_user_click=None,
) -> ft.Control:
    """构建顶部栏。username 为空且未登录时显示"点击登录"。"""
    c = Colors.from_page(page)

    display_name = username if logged_in else "点击登录"
    avatar_text = (username[:2] if username else "P").upper() if logged_in else "?"

    user_chip = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(
                        avatar_text,
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color="#FFFFFF",
                    ),
                    width=32,
                    height=32,
                    border_radius=16,
                    alignment=ft.Alignment.CENTER,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[c["gradient_start"], c["gradient_end"]],
                    ),
                ),
                ft.Text(
                    display_name,
                    size=13,
                    weight=ft.FontWeight.W_500,
                    color=c["on_surface"] if logged_in else c["primary"],
                ),
                ft.Icon(
                    ft.Icons.KEYBOARD_ARROW_DOWN,
                    color=c["on_surface_variant"],
                    size=16,
                ),
            ],
            spacing=6,
        ),
        padding=ft.Padding(left=10, right=14, top=4, bottom=4),
        border_radius=20,
        border=ft.Border.all(1, c["outline_variant"]),
        ink=True,
        on_click=lambda _: on_user_click() if on_user_click else None,
        tooltip="点击登录或切换账户",
    )

    is_dark = page.theme_mode == ft.ThemeMode.DARK
    theme_icon = ft.Icons.DARK_MODE if is_dark else ft.Icons.LIGHT_MODE
    theme_tooltip = "切换到浅色主题" if is_dark else "切换到深色主题"

    theme_btn = ft.Container(
        content=ft.Icon(theme_icon, color=c["on_surface_variant"], size=20),
        width=38,
        height=38,
        border_radius=10,
        border=ft.Border.all(1, c["outline_variant"]),
        ink=True,
        on_click=lambda _: on_toggle_theme() if on_toggle_theme else None,
        tooltip=theme_tooltip,
    )

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(
                    title,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=c["on_surface"],
                ),
                ft.Container(expand=True),
                theme_btn,
                ft.Container(width=8),
                user_chip,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=24, right=24, top=12, bottom=12),
        bgcolor=c["surface"],
        border_radius=12,
        border=ft.Border.all(1, c["outline_variant"]),
    )
