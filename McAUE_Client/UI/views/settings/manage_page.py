"""管理设置页面。"""

import flet as ft

from theme.colors import Colors
from components.animation import SmoothScroll
from state.config import config
from ._common import build_section_title, build_setting_row, make_dropdown, make_switch


def build_manage_page(page, state, on_logout):
    c = Colors.from_page(page)
    mc = config.get("manage")

    logout_button = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOGOUT, color="#FFFFFF", size=18),
                ft.Text("退出登录", size=14, weight=ft.FontWeight.W_500, color="#FFFFFF"),
            ],
            spacing=8,
        ),
        padding=ft.Padding(left=24, right=24, top=12, bottom=12),
        border_radius=10,
        bgcolor=c["error"],
        ink=True,
        on_click=lambda _: on_logout() if on_logout else None,
    )

    file_dl_source = make_dropdown(page, mc.get("file_dl_source", "mirror_prefer"), [
        ft.dropdown.Option("mirror_prefer", "尽量使用镜像源"),
        ft.dropdown.Option("official_fallback", "优先使用官方源，在加载缓慢时换用镜像源"),
        ft.dropdown.Option("official_prefer", "尽量使用官方源"),
    ], width=280)
    file_dl_source.on_select = lambda e: config.set("manage", "file_dl_source", e.control.value)

    version_list_source = make_dropdown(page, mc.get("version_list_source", "mirror_prefer"), [
        ft.dropdown.Option("mirror_prefer", "尽量使用镜像源（可能缺少刚刚更新的版本）"),
        ft.dropdown.Option("official_fallback", "优先使用官方源，在加载缓慢时换用镜像源"),
        ft.dropdown.Option("official_prefer", "尽量使用官方源"),
    ], width=280)
    version_list_source.on_select = lambda e: config.set("manage", "version_list_source", e.control.value)

    thread_slider = ft.Slider(
        min=1, max=512, divisions=511, value=mc.get("max_threads", 8),
        label="{value} 线程",
        active_color=c["primary"], width=180,
    )
    thread_slider.on_change = lambda e: config.set("manage", "max_threads", int(thread_slider.value))

    speed_slider = ft.Slider(
        min=0, max=20, divisions=200, value=mc.get("speed_limit", 0),
        label="不限速" if mc.get("speed_limit", 0) == 0 else f"{mc.get('speed_limit', 0):g} MiB/s",
        active_color=c["primary"], width=180,
    )

    def on_speed_change(e):
        val = float(speed_slider.value)
        speed_slider.label = "不限速" if val == 0 else f"{val:g} MiB/s"
        config.set("manage", "speed_limit", val)
        try:
            speed_slider.update()
        except Exception:
            pass

    speed_slider.on_change = on_speed_change

    community_dl_source = make_dropdown(page, mc.get("community_dl_source", "mirror_prefer"), [
        ft.dropdown.Option("mirror_prefer", "尽量使用镜像源"),
        ft.dropdown.Option("official_fallback", "仅在官方源加载缓慢时改用镜像源"),
        ft.dropdown.Option("official_prefer", "尽量使用官方源"),
    ], width=280)
    community_dl_source.on_select = lambda e: config.set("manage", "community_dl_source", e.control.value)

    filename_format = make_dropdown(page, mc.get("filename_format", "modname_bracket"), [
        ft.dropdown.Option("modname_bracket", "【模组名】文件名"),
        ft.dropdown.Option("modname_square", "[模组名]文件名"),
        ft.dropdown.Option("modname_dash", "模组名-文件名"),
        ft.dropdown.Option("filename_dash", "文件名-模组名"),
        ft.dropdown.Option("filename_only", "文件名"),
    ], width=280)
    filename_format.on_select = lambda e: config.set("manage", "filename_format", e.control.value)

    mod_manage_style = make_dropdown(page, mc.get("mod_manage_style", "translated"), [
        ft.dropdown.Option("translated", "标题显示译名，详情显示文件名"),
        ft.dropdown.Option("filename", "标题显示文件名，详情显示译名"),
    ], width=280)
    mod_manage_style.on_select = lambda e: config.set("manage", "mod_manage_style", e.control.value)

    quick_download = make_dropdown(page, mc.get("quick_download", "ask"), [
        ft.dropdown.Option("ask", "总是询问"),
        ft.dropdown.Option("current_instance", "下载到当前选中实例"),
        ft.dropdown.Option("ask_select_instance", "询问并下载到选择的实例"),
        ft.dropdown.Option("ask_select_path", "询问并下载到一个路径"),
    ], width=280)
    quick_download.on_select = lambda e: config.set("manage", "quick_download", e.control.value)

    def _cfg_switch(key, default):
        sw = make_switch(page, mc.get(key, default))
        sw.on_change = lambda e, k=key: config.set("manage", k, e.control.value)
        return sw

    return SmoothScroll(
        page=page,
        controls=[
            build_section_title(page, "管理", ft.Icons.FOLDER_OUTLINED),

            ft.Text("用户", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                (state.username[:2] if state.username else "P").upper(),
                                size=18, weight=ft.FontWeight.BOLD, color="#FFFFFF",
                            ),
                            width=56, height=56, border_radius=16,
                            alignment=ft.Alignment.CENTER,
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment.TOP_LEFT,
                                end=ft.Alignment.BOTTOM_RIGHT,
                                colors=[c["gradient_start"], c["gradient_end"]],
                            ),
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(
                                    state.username if state.logged_in else "未登录",
                                    size=16, weight=ft.FontWeight.W_600, color=c["on_surface"],
                                ),
                                ft.Text(
                                    "已登录" if state.logged_in else "点击右上角登录",
                                    size=12, color=c["on_surface_variant"],
                                ),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        logout_button if state.logged_in else ft.Container(),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(16, 16, 16, 16),
                bgcolor=c["surface"],
                border_radius=12,
                border=ft.Border.all(1, c["outline_variant"]),
            ),

            ft.Text("游戏资源获取行为", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "文件下载源", "选择游戏文件下载源", file_dl_source),
            build_setting_row(page, "版本列表源", "选择版本列表数据源", version_list_source),
            build_setting_row(page, "最大线程数", "下载文件时的最大并发线程数", thread_slider),
            build_setting_row(page, "速度限制", "0 = 不限速，单位 MiB/s", speed_slider),
            build_setting_row(page, "安装新实例后自动选定", "", _cfg_switch("auto_select_new", True)),
            build_setting_row(page, "升级部分版本的 Authlib", "", _cfg_switch("upgrade_authlib", True)),

            ft.Text("社区资源获取行为", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "下载源", "社区资源文件下载源", community_dl_source),
            build_setting_row(page, "文件名格式", "下载文件的命名格式", filename_format),
            build_setting_row(page, "模组管理样式", "模组列表的显示方式", mod_manage_style),
            build_setting_row(page, "快速下载行为", "快速下载时的操作", quick_download),
            build_setting_row(page, "不显示 Quilt 加载器", "", _cfg_switch("hide_quilt", False)),
            build_setting_row(page, "自动安装模组前置", "下载模组时自动检查并安装必需前置", _cfg_switch("auto_install_deps", True)),

            ft.Text("辅助功能", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "游戏语言", "自动设置为启动器语言", _cfg_switch("auto_game_language", True)),
            build_setting_row(page, "识别剪贴板资源链接", "自动检测并跳转剪贴板中的社区资源链接", _cfg_switch("detect_clipboard", False)),
        ],
        spacing=8,
        expand=True,
    )
