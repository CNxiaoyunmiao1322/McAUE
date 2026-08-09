"""关于视图 - 应用信息、技术栈、快捷操作、致谢。"""

import webbrowser
import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar

GITHUB_URL = "https://github.com/CNxiaoyunmiao1322/McAUE"


def _build_info_row(page: ft.Page, label: str, value: str, icon: str) -> ft.Control:
    c = Colors.from_page(page)
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon, color=c["primary"], size=20),
                ft.Text(label, size=14, color=c["on_surface_variant"]),
                ft.Container(expand=True),
                ft.Text(value, size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        bgcolor=c["surface"],
        border_radius=10,
        border=ft.Border.all(1, c["outline_variant"]),
    )


def build_about_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_user_click=None,
    **kwargs,
) -> list:
    """构建关于视图。"""
    c = Colors.from_page(page)

    logo_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, color="#FFFFFF", size=48),
                    width=96,
                    height=96,
                    border_radius=24,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[c["gradient_start"], c["gradient_end"]],
                    ),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Text("McAUE", size=28, weight=ft.FontWeight.BOLD, color=c["on_surface"]),
                ft.Text("Minecraft 客户端启动器", size=14, color=c["on_surface_variant"]),
                ft.Container(
                    content=ft.Text("v1.0.0", size=12, color=c["secondary"], weight=ft.FontWeight.W_600),
                    padding=ft.Padding(left=12, right=12, top=4, bottom=4),
                    border_radius=20,
                    bgcolor=c["secondary_container"],
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
        ),
        padding=ft.Padding(28, 28, 28, 28),
        bgcolor=c["surface"],
        border_radius=16,
        border=ft.Border.all(1, c["outline_variant"]),
        alignment=ft.Alignment.CENTER,
    )

    tech_section = ft.Column(
        controls=[
            _build_info_row(page, "运行时", "Python 3.14.6", ft.Icons.CODE),
            _build_info_row(page, "UI 框架", "Flet 0.86.5", ft.Icons.DASHBOARD),
        ],
        spacing=6,
    )

    def _build_action_btn(icon, label, on_click):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(icon, color=c["icon_accent"], size=28),
                    ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
            padding=ft.Padding(16, 16, 16, 16),
            bgcolor=c["surface"],
            border_radius=12,
            border=ft.Border.all(1, c["outline_variant"]),
            ink=True,
            on_click=on_click,
            alignment=ft.Alignment.CENTER,
            expand=True,
        )

    actions_section = ft.Row(
        controls=[
            _build_action_btn(
                ft.Icons.FEEDBACK_OUTLINED, "反馈",
                lambda _: webbrowser.open(f"{GITHUB_URL}/issues"),
            ),
            _build_action_btn(
                ft.Icons.DESCRIPTION_OUTLINED, "查看日志",
                lambda _: None,
            ),
            _build_action_btn(
                ft.Icons.CODE, "GitHub",
                lambda _: webbrowser.open(GITHUB_URL),
            ),
        ],
        spacing=10,
    )

    credits = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(
                    "致谢",
                    size=16,
                    weight=ft.FontWeight.W_600,
                    color=c["on_surface"],
                ),
                ft.Text(
                    "感谢 Flet 社区提供的优秀 UI 框架，以及所有开源贡献者。",
                    size=13,
                    color=c["on_surface_variant"],
                ),
            ],
            spacing=6,
        ),
        padding=ft.Padding(16, 16, 16, 16),
        bgcolor=c["surface"],
        border_radius=12,
        border=ft.Border.all(1, c["outline_variant"]),
    )

    content = ft.Column(
        controls=[
            build_topbar(
                page,
                "关于",
                state.username,
                state.logged_in,
                on_toggle_theme,
                on_user_click,
            ),
            ft.Container(height=4),
            logo_section,
            ft.Container(height=4),
            ft.Text("技术信息", size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
            tech_section,
            ft.Container(height=4),
            ft.Text("快捷操作", size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
            actions_section,
            ft.Container(height=4),
            credits,
            ft.Container(height=8),
            ft.Text(
                "© 2026 McAUE · 仅供学习交流使用",
                size=11,
                color=c["on_surface_variant"],
                text_align=ft.TextAlign.CENTER,
            ),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )

    return [content]
