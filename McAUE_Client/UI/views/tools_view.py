"""工具页面视图 - 皮肤库、服务器管理、我的通行证。

点击工具卡片进入对应工具详情视图，详情视图内含返回按钮。
使用 AnimatedSwitcher 实现视图切换动画。
"""

import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar
from components.animation import SmoothScroll
from state.config import config

ICON_MAP = {
    "face": ft.Icons.FACE,
    "dns": ft.Icons.DNS,
    "badge": ft.Icons.BADGE,
}

TOOL_KEYS = {
    "皮肤库": "skins",
    "服务器管理": "servers",
    "我的通行证": "pass",
}


def _build_back_button(c, on_click) -> ft.Control:
    return ft.Container(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.ARROW_BACK, size=18), ft.Text("返回", size=13)],
            spacing=4,
        ),
        padding=ft.Padding(left=12, right=16, top=8, bottom=8),
        border_radius=8,
        border=ft.Border.all(1, c["outline_variant"]),
        ink=True,
        on_click=on_click,
    )


def _build_tool_card(page: ft.Page, tool, on_click=None) -> ft.Control:
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
                ft.Text(tool.name, size=15, weight=ft.FontWeight.W_600, color=c["on_surface"]),
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
                        ft.Text("打开", size=12, color=c["primary"], weight=ft.FontWeight.W_500),
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
        on_click=on_click,
    )


def _build_skins_view(page: ft.Page, on_back) -> ft.Control:
    """皮肤库视图。"""
    c = Colors.from_page(page)

    search_field = ft.TextField(
        hint_text="搜索皮肤...",
        prefix_icon=ft.Icons.SEARCH,
        width=300,
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        text_size=13,
        content_padding=ft.Padding(left=12, right=12, top=8, bottom=8),
    )

    sample_skins = [
        {"name": "Steve", "id": "steve"},
        {"name": "Alex", "id": "alex"},
        {"name": "自定义皮肤 A", "id": "custom_a"},
        {"name": "自定义皮肤 B", "id": "custom_b"},
        {"name": "自定义皮肤 C", "id": "custom_c"},
        {"name": "自定义皮肤 D", "id": "custom_d"},
    ]

    def _show_skin_dialog(e, skin):
        dialog = ft.AlertDialog(
            title=ft.Text(skin["name"], size=16),
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.PERSON, color=c["on_surface_variant"], size=64),
                        width=120,
                        height=160,
                        border_radius=8,
                        bgcolor=c["surface_variant"],
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Text("皮肤预览需要皮肤渲染模块实现。", size=11, color=c["on_surface_variant"]),
                ],
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                tight=True,
            ),
            actions=[
                ft.TextButton("关闭", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("应用", on_click=lambda e: page.pop_dialog()),
            ],
        )
        page.show_dialog(dialog)

    skin_cards = []
    for skin in sample_skins:
        skin_cards.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.PERSON, color=c["on_surface_variant"], size=36),
                            width=80,
                            height=100,
                            border_radius=8,
                            bgcolor=c["surface_variant"],
                            alignment=ft.Alignment.CENTER,
                            ink=True,
                            on_click=lambda e, s=skin: _show_skin_dialog(e, s),
                        ),
                        ft.Text(skin["name"], size=12, color=c["on_surface"], text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                ),
                col={"sm": 6, "md": 3, "lg": 2},
            )
        )

    return SmoothScroll(
        page=page,
        controls=[
            ft.Row(
                controls=[_build_back_button(c, on_back)],
            ),
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.FACE, color=c["primary"], size=24),
                    ft.Text("皮肤库", size=20, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.Row(
                            controls=[ft.Icon(ft.Icons.UPLOAD, size=16), ft.Text("上传皮肤", size=13)],
                            spacing=6,
                        ),
                        padding=ft.Padding(left=16, right=16, top=8, bottom=8),
                        border_radius=8,
                        border=ft.Border.all(1, c["outline_variant"]),
                        ink=True,
                        on_click=lambda e: _show_msg(page, "皮肤上传功能需要皮肤服务模块实现"),
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            ft.Text("浏览和应用 Minecraft 皮肤（当前为示例数据）", size=13, color=c["on_surface_variant"]),
            ft.Container(height=4),
            search_field,
            ft.Container(height=4),
            ft.ResponsiveRow(controls=skin_cards, spacing=12, run_spacing=12),
            ft.Container(height=4),
            ft.Text("皮肤渲染和上传功能需要皮肤服务模块实现。", size=11, color=c["on_surface_variant"]),
        ],
        spacing=8,
        expand=True,
    )


def _build_servers_view(page: ft.Page, on_back) -> ft.Control:
    """服务器管理视图。"""
    c = Colors.from_page(page)
    servers = config.get("multiplayer", "servers", default=[])

    server_list = ft.Column(spacing=6)

    def _refresh():
        server_list.controls.clear()
        if not servers:
            server_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.DNS_OUTLINED, color=c["on_surface_variant"], size=36),
                            ft.Text("暂无服务器", size=14, color=c["on_surface_variant"]),
                            ft.Text("前往 设置 → 联机 添加服务器", size=12, color=c["on_surface_variant"]),
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
            for srv in servers:
                server_list.controls.append(
                    ft.Container(
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
                                    content=ft.Row(
                                        controls=[ft.Icon(ft.Icons.PLAY_ARROW, color="#FFFFFF", size=16), ft.Text("连接", size=12, color="#FFFFFF")],
                                        spacing=4,
                                    ),
                                    padding=ft.Padding(left=12, right=12, top=6, bottom=6),
                                    border_radius=6,
                                    bgcolor=c["primary"],
                                    ink=True,
                                    on_click=lambda e: _show_msg(page, "服务器连接功能需要联机核心模块实现"),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.Padding(12, 10, 12, 10),
                        border_radius=8,
                        border=ft.Border.all(1, c["outline_variant"]),
                    )
                )
        try:
            server_list.update()
        except Exception:
            pass

    _refresh()

    return SmoothScroll(
        page=page,
        controls=[
            ft.Row(controls=[_build_back_button(c, on_back)]),
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.DNS, color=c["primary"], size=24),
                    ft.Text("服务器管理", size=20, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                ],
            ),
            ft.Text("管理游戏服务器（服务器列表与设置→联机同步）", size=13, color=c["on_surface_variant"]),
            ft.Container(height=4),
            ft.Container(
                content=server_list,
                padding=ft.Padding(12, 12, 12, 12),
                bgcolor=c["surface"],
                border_radius=10,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
            ft.Text("服务器连接功能需要联机核心模块实现。", size=11, color=c["on_surface_variant"]),
        ],
        spacing=8,
        expand=True,
    )


def _build_pass_view(page: ft.Page, state, on_back) -> ft.Control:
    """我的通行证视图。"""
    c = Colors.from_page(page)
    account = config.get("account")

    login_type_map = {
        "offline": "离线模式",
        "microsoft": "微软账户",
        "thirdparty": "第三方验证",
    }
    login_type_label = login_type_map.get(account.get("login_type", ""), "未登录")

    def _build_info_card(label, value, icon):
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
            padding=ft.Padding(16, 14, 16, 14),
            bgcolor=c["surface"],
            border_radius=10,
            border=ft.Border.all(1, c["outline_variant"]),
        )

    stats_cards = [
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.SPORTS_ESPORTS, color=c["primary"], size=28),
                    ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=c["on_surface"]),
                    ft.Text("游戏时长", size=11, color=c["on_surface_variant"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            padding=ft.Padding(16, 16, 16, 16),
            bgcolor=c["surface"],
            border_radius=12,
            border=ft.Border.all(1, c["outline_variant"]),
            expand=True,
        ),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.DOWNLOAD, color=c["primary"], size=28),
                    ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=c["on_surface"]),
                    ft.Text("已安装版本", size=11, color=c["on_surface_variant"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            padding=ft.Padding(16, 16, 16, 16),
            bgcolor=c["surface"],
            border_radius=12,
            border=ft.Border.all(1, c["outline_variant"]),
            expand=True,
        ),
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.EXTENSION, color=c["primary"], size=28),
                    ft.Text("0", size=20, weight=ft.FontWeight.BOLD, color=c["on_surface"]),
                    ft.Text("已安装模组", size=11, color=c["on_surface_variant"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
            ),
            padding=ft.Padding(16, 16, 16, 16),
            bgcolor=c["surface"],
            border_radius=12,
            border=ft.Border.all(1, c["outline_variant"]),
            expand=True,
        ),
    ]

    return SmoothScroll(
        page=page,
        controls=[
            ft.Row(controls=[_build_back_button(c, on_back)]),
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.BADGE, color=c["primary"], size=24),
                    ft.Text("我的通行证", size=20, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                ],
            ),
            ft.Container(height=4),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color="#FFFFFF", size=40),
                            width=64,
                            height=64,
                            border_radius=16,
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment.TOP_LEFT,
                                end=ft.Alignment.BOTTOM_RIGHT,
                                colors=[c["gradient_start"], c["gradient_end"]],
                            ),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(state.username or "未登录", size=18, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                                ft.Text(login_type_label, size=13, color=c["on_surface_variant"]),
                            ],
                            spacing=2,
                        ),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(20, 20, 20, 20),
                bgcolor=c["surface"],
                border_radius=16,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
            ft.Container(height=4),
            ft.Text("账户信息", size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
            _build_info_card("用户名", state.username or "未设置", ft.Icons.PERSON),
            _build_info_card("登录方式", login_type_label, ft.Icons.LOCK_OUTLINE),
            _build_info_card("游戏版本", config.get("game", "selected_version", default="1.21.4"), ft.Icons.VIDEOGAME_ASSET),
            ft.Container(height=4),
            ft.Text("游戏统计", size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
            ft.Row(controls=stats_cards, spacing=10),
            ft.Container(height=4),
            ft.Text("统计数据需要游戏日志分析模块实现。", size=11, color=c["on_surface_variant"]),
        ],
        spacing=8,
        expand=True,
    )


def _show_msg(page, msg):
    """显示消息提示。"""
    dialog = ft.AlertDialog(
        title=ft.Text("提示", size=16),
        content=ft.Text(msg, size=13),
        actions=[ft.TextButton("确定", on_click=lambda e: page.pop_dialog())],
    )
    page.show_dialog(dialog)


def build_tools_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_user_click=None,
    **kwargs,
) -> list:
    """构建工具页面视图。通过 AppState 的 tools_subview 决定显示网格或详情。"""

    def _show_detail(tool_key):
        state.tools_subview = tool_key
        if on_navigate:
            on_navigate("/tools")

    def _back_to_grid():
        state.tools_subview = "grid"
        if on_navigate:
            on_navigate("/tools")

    sub = state.tools_subview
    if sub == "skins":
        content = _build_skins_view(page, lambda _: _back_to_grid())
    elif sub == "servers":
        content = _build_servers_view(page, lambda _: _back_to_grid())
    elif sub == "pass":
        content = _build_pass_view(page, state, lambda _: _back_to_grid())
    else:
        content = _build_grid_view(page, state, _show_detail)

    return [
        build_topbar(page, "工具", state.username, state.logged_in, on_toggle_theme, on_user_click),
        ft.Container(height=4),
        content,
    ]


def _build_grid_view(page: ft.Page, state, on_tool_click=None) -> ft.Control:
    """构建工具卡片网格视图。"""
    c = Colors.from_page(page)

    tool_cards = [
        ft.Container(
            content=_build_tool_card(
                page,
                tool,
                on_click=lambda e, t=tool: on_tool_click(TOOL_KEYS.get(t.name, "")) if on_tool_click else None,
            ),
            col={"sm": 6, "md": 4},
        )
        for tool in state.tools
    ]

    return SmoothScroll(
        page=page,
        controls=[
            ft.Text(f"共 {len(state.tools)} 个工具", size=14, color=c["on_surface_variant"]),
            ft.Container(height=4),
            ft.ResponsiveRow(controls=tool_cards, spacing=16, run_spacing=16),
        ],
        spacing=10,
        expand=True,
    )
