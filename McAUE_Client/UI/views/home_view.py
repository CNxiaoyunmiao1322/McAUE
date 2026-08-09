"""首页视图 - 快速启动横幅、版本信息、新闻动态。"""

import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar
from components.card import build_info_card


def _build_launch_banner(page: ft.Page, state, on_play=None, on_download=None) -> ft.Control:
    c = Colors.from_page(page)
    username_display = state.username if state.logged_in else "未登录"

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            "McAUE 启动器",
                            size=26,
                            weight=ft.FontWeight.BOLD,
                            color="#FFFFFF",
                        ),
                        ft.Text(
                            f"当前账户：{username_display} · 游戏版本 1.21.4",
                            size=13,
                            color="#FFFFFF" + "CC",
                        ),
                        ft.Container(height=14),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.PLAY_ARROW, color="#FFFFFF", size=20),
                                            ft.Text(
                                                "启动游戏",
                                                size=15,
                                                weight=ft.FontWeight.W_600,
                                                color="#FFFFFF",
                                            ),
                                        ],
                                        spacing=8,
                                    ),
                                    padding=ft.Padding(left=28, right=28, top=12, bottom=12),
                                    border_radius=10,
                                    bgcolor=c["button_accent"],
                                    ink=True,
                                    on_click=lambda _: on_play() if on_play else None,
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.DOWNLOAD_FOR_OFFLINE,
                                                color="#FFFFFF",
                                                size=18,
                                            ),
                                            ft.Text("下载游戏", size=14, color="#FFFFFF"),
                                        ],
                                        spacing=6,
                                    ),
                                    padding=ft.Padding(left=20, right=20, top=12, bottom=12),
                                    border_radius=10,
                                    bgcolor=c["gradient_start"],
                                    ink=True,
                                    on_click=lambda _: on_download() if on_download else None,
                                ),
                            ],
                            spacing=10,
                        ),
                    ],
                    spacing=4,
                ),
                ft.Container(expand=True),
                ft.Container(
                    content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, color=c["gradient_start"], size=72),
                    alignment=ft.Alignment.CENTER,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(28, 28, 28, 28),
        border_radius=20,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=[c["gradient_start"], c["gradient_end"]],
        ),
    )


def _build_news_section(page: ft.Page, state) -> ft.Control:
    c = Colors.from_page(page)

    news_cards = []
    for item in state.news:
        icon_map = {
            "更新": ft.Icons.NEWSPAPER,
            "公告": ft.Icons.CAMPAIGN,
            "Mod": ft.Icons.CODE,
        }
        news_cards.append(
            build_info_card(
                page,
                title=item.title,
                subtitle=item.summary,
                icon=icon_map.get(item.tag, ft.Icons.NEWSPAPER),
            )
        )

    return ft.Column(
        controls=[
            ft.Text("最新动态", size=18, weight=ft.FontWeight.W_600, color=c["on_surface"]),
            ft.ResponsiveRow(
                controls=[
                    ft.Container(content=card, col={"sm": 6, "md": 4}) for card in news_cards
                ],
                spacing=16,
                run_spacing=16,
            ),
        ],
        spacing=12,
    )


def build_home_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_user_click=None,
    **kwargs,
) -> list:
    """构建首页视图，返回控件列表。"""

    content = ft.Column(
        controls=[
            build_topbar(
                page,
                "首页",
                state.username,
                state.logged_in,
                on_toggle_theme,
                on_user_click,
            ),
            ft.Container(height=4),
            _build_launch_banner(
                page,
                state,
                on_play=None,
                on_download=lambda: on_navigate("/download") if on_navigate else None,
            ),
            ft.Container(height=8),
            _build_news_section(page, state),
        ],
        spacing=12,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    return [content]
