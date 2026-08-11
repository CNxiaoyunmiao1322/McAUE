"""联机设置页面。"""

import flet as ft

from theme.colors import Colors
from components.animation import SmoothScroll
from state.config import config
from ._common import build_section_title, show_msg


def _build_server_row(page, srv, index, servers, list_column):
    """构建单个服务器行。"""
    c = Colors.from_page(page)

    def _remove_server(e):
        servers.pop(index)
        config.set("multiplayer", "servers", servers)
        list_column.controls.clear()
        if not servers:
            list_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.DNS_OUTLINED, color=c["on_surface_variant"], size=36),
                            ft.Text("暂无服务器", size=14, color=c["on_surface_variant"]),
                        ],
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(0, 32, 0, 32),
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                )
            )
        else:
            for i, s in enumerate(servers):
                list_column.controls.append(_build_server_row(page, s, i, servers, list_column))
        try:
            list_column.update()
        except Exception:
            pass

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.DNS, color=c["primary"], size=20),
                    width=36,
                    height=36,
                    border_radius=8,
                    bgcolor=c["primary_container"],
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    controls=[
                        ft.Text(srv.get("name", "未命名"), size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                        ft.Text(
                            f"{srv.get('address', '')}:{srv.get('port', '25565')}",
                            size=12,
                            color=c["on_surface_variant"],
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.DELETE_OUTLINE, color=c["on_surface_variant"], size=18),
                    width=32,
                    height=32,
                    border_radius=6,
                    ink=True,
                    on_click=_remove_server,
                    alignment=ft.Alignment.CENTER,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(12, 10, 12, 10),
        border_radius=8,
        border=ft.Border.all(1, c["outline_variant"]),
    )


def build_multiplayer_page(page):
    c = Colors.from_page(page)
    servers = config.get("multiplayer", "servers", default=[])

    server_list_column = ft.Column(spacing=6)

    def _refresh_server_list():
        server_list_column.controls.clear()
        if not servers:
            server_list_column.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.DNS_OUTLINED, color=c["on_surface_variant"], size=36),
                            ft.Text("暂无服务器", size=14, color=c["on_surface_variant"]),
                            ft.Text("点击上方按钮添加服务器", size=12, color=c["on_surface_variant"]),
                        ],
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.Padding(0, 32, 0, 32),
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                )
            )
        else:
            for i, srv in enumerate(servers):
                server_list_column.controls.append(_build_server_row(page, srv, i, servers, server_list_column))
        try:
            server_list_column.update()
        except Exception:
            pass

    def _show_add_server_dialog(e):
        name_field = ft.TextField(
            label="服务器名称", hint_text="我的服务器", width=320,
            border_color=c["outline_variant"], focused_border_color=c["primary"],
            text_size=13, label_style=ft.TextStyle(size=13),
        )
        addr_field = ft.TextField(
            label="服务器地址", hint_text="play.example.com", width=320,
            border_color=c["outline_variant"], focused_border_color=c["primary"],
            text_size=13, label_style=ft.TextStyle(size=13),
        )
        port_field = ft.TextField(
            label="端口", hint_text="25565", width=320,
            border_color=c["outline_variant"], focused_border_color=c["primary"],
            text_size=13, label_style=ft.TextStyle(size=13),
            keyboard_type=ft.KeyboardType.NUMBER,
        )

        def _on_confirm(ev):
            name = name_field.value.strip() if name_field.value else ""
            addr = addr_field.value.strip() if addr_field.value else ""
            port = port_field.value.strip() if port_field.value else "25565"
            if not name:
                name = addr or "未命名服务器"
            if not addr:
                show_msg(page, "请输入服务器地址")
                return
            servers.append({"name": name, "address": addr, "port": port})
            config.set("multiplayer", "servers", servers)
            page.pop_dialog()
            _refresh_server_list()

        dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[ft.Icon(ft.Icons.DOMAIN_ADD, color=c["primary"], size=22), ft.Text("添加服务器", size=16)],
                spacing=8,
            ),
            content=ft.Column(
                controls=[name_field, addr_field, port_field],
                spacing=12,
                tight=True,
            ),
            actions=[
                ft.TextButton("取消", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("添加", on_click=_on_confirm),
            ],
        )
        page.show_dialog(dialog)

    add_btn = ft.Container(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.ADD, size=18), ft.Text("添加服务器", size=13, weight=ft.FontWeight.W_500)],
            spacing=6,
        ),
        padding=ft.Padding(left=16, right=16, top=8, bottom=8),
        border_radius=8,
        bgcolor=c["primary"],
        ink=True,
        on_click=_show_add_server_dialog,
    )

    _refresh_server_list()

    return SmoothScroll(
        page=page,
        controls=[
            build_section_title(page, "联机", ft.Icons.WIFI_OUTLINED),
            ft.Row(
                controls=[
                    ft.Text("服务器列表", size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                    ft.Container(expand=True),
                    add_btn,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Container(
                content=server_list_column,
                padding=ft.Padding(12, 12, 12, 12),
                bgcolor=c["surface"],
                border_radius=10,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
            ft.Text(
                "服务器连接功能需要联机核心模块实现，当前仅支持服务器信息管理。",
                size=11,
                color=c["on_surface_variant"],
            ),
        ],
        spacing=8,
        expand=True,
    )
