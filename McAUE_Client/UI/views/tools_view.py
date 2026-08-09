"""工具页面视图。"""

import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar

ICON_MAP = {
    "search": ft.Icons.SEARCH,
    "explore": ft.Icons.EXPLORE,
    "auto_awesome": ft.Icons.AUTO_AWESOME,
    "grid_view": ft.Icons.GRID_VIEW,
    "code": ft.Icons.CODE,
    "face": ft.Icons.FACE,
}


def _build_tool_card(page: ft.Page, tool) -> ft.Control:
    c = Colors.from_page(page)
    icon = ICON_MAP.get(tool.icon, ft.Icons.BUILD)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, color="#FFFFFF", size=26),
                    width=52,
                    height=52,
                    border_radius=14,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[c["gradient_start"], c["gradient_end"]],
                    ),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Container(height=6),
                ft.Text(
                    tool.name,
                    size=15,
                    weight=ft.FontWeight.W_600,
                    color=c["on_surface"],
                ),
                ft.Text(
                    tool.description,
                    size=12,
                    color=c["on_surface_variant"],
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Container(height=4),
                ft.Row(
                    controls=[
                        ft.Text(
                            "打开",
                            size=12,
                            color=c["primary"],
                            weight=ft.FontWeight.W_500,
                        ),
                        ft.Icon(ft.Icons.ARROW_FORWARD, color=c["primary"], size=14),
                    ],
                    spacing=4,
                ),
            ],
            spacing=2,
        ),
        padding=ft.Padding(20, 20, 20, 20),
        bgcolor=c["surface"],
        border_radius=14,
        border=ft.Border.all(1, c["outline_variant"]),
        ink=True,
    )


def build_tools_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_user_click=None,
    **kwargs,
) -> list:
    """构建工具页面视图。"""
    c = Colors.from_page(page)

    tool_cards = [
        ft.Container(content=_build_tool_card(page, tool), col={"sm": 6, "md": 4})
        for tool in state.tools
    ]

    content = ft.Column(
        controls=[
            build_topbar(
                page,
                "工具",
                state.username,
                state.logged_in,
                on_toggle_theme,
                on_user_click,
            ),
            ft.Container(height=4),
            ft.Text(
                f"共 {len(state.tools)} 个工具",
                size=14,
                color=c["on_surface_variant"],
            ),
            ft.Container(height=4),
            ft.ResponsiveRow(
                controls=tool_cards,
                spacing=16,
                run_spacing=16,
            ),
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return [content]
