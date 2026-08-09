"""导航侧边栏组件。"""

import flet as ft

from theme.colors import Colors

NAV_ITEMS = [
    ("/home", "首页", ft.Icons.HOME_OUTLINED, ft.Icons.HOME),
    ("/download", "下载", ft.Icons.DOWNLOAD_OUTLINED, ft.Icons.DOWNLOAD),
    ("/tools", "工具", ft.Icons.BUILD_OUTLINED, ft.Icons.BUILD),
    ("/settings", "设置", ft.Icons.SETTINGS_OUTLINED, ft.Icons.SETTINGS),
    ("/about", "关于", ft.Icons.INFO_OUTLINE, ft.Icons.INFO),
]


def _build_logo(c: dict) -> ft.Control:
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Icon(ft.Icons.VIDEOGAME_ASSET, color="#FFFFFF", size=28),
                width=44,
                height=44,
                border_radius=12,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_LEFT,
                    end=ft.Alignment.BOTTOM_RIGHT,
                    colors=[c["gradient_start"], c["gradient_end"]],
                ),
            ),
            ft.Column(
                controls=[
                    ft.Text("McAUE", size=20, weight=ft.FontWeight.BOLD, color=c["on_surface"]),
                    ft.Text("Minecraft 客户端", size=11, color=c["on_surface_variant"]),
                ],
                spacing=0,
            ),
        ],
        alignment=ft.MainAxisAlignment.START,
    )


def _build_nav_item(route, label, icon, selected_icon, c, current_route, on_navigate) -> ft.Control:
    is_active = current_route == route
    icon_to_use = selected_icon if is_active else icon
    text_color = c["primary"] if is_active else c["on_surface_variant"]
    bg = c["primary_container"] if is_active else ft.Colors.TRANSPARENT

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(icon_to_use, color=text_color, size=22),
                ft.Text(label, size=14, weight=ft.FontWeight.W_500, color=text_color),
            ],
            spacing=12,
        ),
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        border_radius=10,
        bgcolor=bg,
        ink=True,
        on_click=lambda _: on_navigate(route) if on_navigate else None,
    )


def build_sidebar(page: ft.Page, current_route: str, on_navigate=None) -> ft.Control:
    """构建侧边栏。"""
    c = Colors.from_page(page)

    controls = [
        _build_logo(c),
        ft.Divider(height=1, color=c["outline_variant"]),
        ft.Text("导航", size=11, weight=ft.FontWeight.W_600, color=c["on_surface_variant"]),
    ]

    for route, label, icon, sel_icon in NAV_ITEMS:
        controls.append(
            _build_nav_item(route, label, icon, sel_icon, c, current_route, on_navigate)
        )

    controls.append(ft.Container(expand=True))

    return ft.Container(
        content=ft.Column(controls=controls, spacing=4, alignment=ft.MainAxisAlignment.START),
        width=230,
        padding=ft.Padding(16, 16, 16, 16),
        bgcolor=c["surface"],
        border_radius=ft.BorderRadius(0, 12, 12, 0),
    )
