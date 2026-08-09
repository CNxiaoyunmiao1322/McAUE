"""可复用卡片组件。"""

import flet as ft

from theme.colors import Colors


def build_info_card(
    page: ft.Page,
    title: str,
    subtitle: str = "",
    icon: str = ft.Icons.INFO_OUTLINE,
    on_click=None,
) -> ft.Control:
    """信息卡片，带渐变图标标题条。"""
    c = Colors.from_page(page)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, color="#FFFFFF", size=24),
                    width=48,
                    height=48,
                    border_radius=12,
                    bgcolor=c["icon_accent"],
                ),
                ft.Container(height=4),
                ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                ft.Text(
                    subtitle,
                    size=13,
                    color=c["on_surface_variant"],
                    max_lines=3,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
            spacing=2,
        ),
        padding=ft.Padding(20, 20, 20, 20),
        bgcolor=c["surface"],
        border_radius=16,
        ink=on_click is not None,
        on_click=lambda _: on_click() if on_click else None,
        border=ft.Border.all(1, c["outline_variant"]),
    )
