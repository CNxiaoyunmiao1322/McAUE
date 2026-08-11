"""首页视图 - 快速启动横幅、版本信息、新闻动态、版本设置。"""

import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar
from components.card import build_info_card
from components.animation import SmoothScroll
from core.launcher import launcher
from core.updater import updater
from core.downloader import downloader
from state.config import config


def _build_launch_banner(page: ft.Page, state, on_play=None, on_download=None) -> ft.Control:
    c = Colors.from_page(page)
    username_display = state.username if state.logged_in else "未登录"
    game_version = config.get("game", "selected_version", default="1.21.4")

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
                            f"当前账户：{username_display} · 游戏版本 {game_version}",
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


def _show_launch_dialog(page: ft.Page, state):
    """显示启动进度对话框。"""
    c = Colors.from_page(page)
    progress = ft.ProgressBar(width=300, color=c["primary"], bgcolor=c["surface_variant"])
    status = ft.Text("准备启动...", size=13, color=c["on_surface_variant"])
    log_text = ft.Text("", size=11, color=c["on_surface_variant"])

    def on_progress(msg, pct):
        status.value = msg
        progress.value = pct
        try:
            status.update()
            progress.update()
        except Exception:
            pass

    def on_log(msg):
        log_text.value = msg
        try:
            log_text.update()
        except Exception:
            pass

    def on_complete(result):
        status.value = result.message
        try:
            status.update()
        except Exception:
            pass

    game_version = config.get("game", "selected_version", default="1.21.4")

    dialog = ft.AlertDialog(
        title=ft.Text("启动游戏", size=16),
        content=ft.Column(
            controls=[
                ft.Row([ft.Icon(ft.Icons.ROCKET_LAUNCH, color=c["primary"], size=24), status], spacing=8),
                progress,
                ft.Container(height=4),
                log_text,
            ],
            spacing=8,
            tight=True,
        ),
        actions=[
            ft.TextButton("关闭", on_click=lambda e: page.pop_dialog()),
        ],
    )
    page.show_dialog(dialog)

    launcher.set_callbacks(on_progress=on_progress, on_log=on_log, on_complete=on_complete)
    launcher.launch(version=game_version, username=state.username)


def _show_launch_selector(page: ft.Page, state, on_version_settings=None):
    """显示启动前选择对话框：版本选择 + 账户信息 + 启动按钮。"""
    c = Colors.from_page(page)
    saved_version = getattr(page, "_launch_selector_version", None)
    current_version = saved_version or config.get("game", "selected_version", default="1.21.4")

    installed_versions = downloader.get_installed_versions()
    version_options = []
    if installed_versions:
        for v in installed_versions:
            version_options.append(ft.DropdownOption(v, text=v))
    else:
        for v in ["1.21.4", "1.20.6", "1.16.5", "1.12.2", "1.8.9", "1.7.10"]:
            version_options.append(ft.DropdownOption(v, text=v))

    version_dropdown = ft.Dropdown(
        label="游戏版本",
        width=320,
        text_size=13,
        label_style=ft.TextStyle(size=13),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        options=version_options,
        value=current_version,
    )

    username_display = state.username if state.logged_in else "未登录（离线模式）"
    login_type = config.get("account", "login_type", default="")
    login_type_map = {"offline": "离线模式", "microsoft": "微软账户", "thirdparty": "第三方验证"}
    login_type_label = login_type_map.get(login_type, "未登录")

    account_card = ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.ACCOUNT_CIRCLE, color="#FFFFFF", size=24),
                    width=44,
                    height=44,
                    border_radius=10,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=[c["gradient_start"], c["gradient_end"]],
                    ),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    controls=[
                        ft.Text(username_display, size=14, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                        ft.Text(login_type_label, size=12, color=c["on_surface_variant"]),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(12, 10, 12, 10),
        bgcolor=c["surface_variant"],
        border_radius=10,
    )

    def _clear_dialog_rebuild():
        page._dialog_rebuild = None
        page._launch_selector_version = None

    def _do_launch(e):
        selected_ver = version_dropdown.value or current_version
        config.set("game", "selected_version", selected_ver)
        _clear_dialog_rebuild()
        page.pop_dialog()
        _show_launch_dialog(page, state)

    def _open_version_settings(e):
        selected_ver = version_dropdown.value or current_version
        _clear_dialog_rebuild()
        page.pop_dialog()
        if on_version_settings:
            on_version_settings(selected_ver)

    def _cancel(e):
        _clear_dialog_rebuild()
        page.pop_dialog()

    def _rebuild():
        page._launch_selector_version = version_dropdown.value
        try:
            page.pop_dialog()
        except Exception:
            pass
        _show_launch_selector(page, state, on_version_settings)

    page._dialog_rebuild = _rebuild

    version_settings_btn = ft.Container(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.SETTINGS, size=16), ft.Text("版本设置", size=13)],
            spacing=6,
        ),
        padding=ft.Padding(left=12, right=12, top=8, bottom=8),
        border_radius=8,
        border=ft.Border.all(1, c["outline_variant"]),
        ink=True,
        on_click=_open_version_settings,
    )

    dialog = ft.AlertDialog(
        title=ft.Row(
            controls=[ft.Icon(ft.Icons.ROCKET_LAUNCH, color=c["primary"], size=22), ft.Text("启动游戏", size=16)],
            spacing=8,
        ),
        content=ft.Column(
            controls=[
                ft.Text("选择要启动的游戏版本", size=13, color=c["on_surface_variant"]),
                version_dropdown,
                ft.Container(height=4),
                ft.Text("当前账户", size=13, color=c["on_surface_variant"]),
                account_card,
                ft.Container(height=4),
                ft.Row(
                    controls=[version_settings_btn, ft.Container(expand=True)],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
            ],
            spacing=10,
            tight=True,
        ),
        actions=[
            ft.TextButton("取消", on_click=_cancel),
            ft.FilledButton("启动", on_click=_do_launch),
        ],
    )
    page.show_dialog(dialog)


# ===== 版本设置（全页视图）=====

def _get_version_setting(version: str, key: str, default=None):
    """读取单个版本的配置项。"""
    vs = config.get("version_settings", default={})
    ver_cfg = vs.get(version, {})
    return ver_cfg.get(key, default)


def _set_version_setting(version: str, key: str, value):
    """保存单个版本的配置项。"""
    vs = config.get("version_settings", default={})
    if version not in vs:
        vs[version] = {}
    vs[version][key] = value
    config.set("version_settings", None, vs)


def _build_version_settings_page(
    page: ft.Page,
    state,
    version: str,
    on_back,
    on_toggle_theme=None,
    on_user_click=None,
) -> ft.Control:
    """构建版本设置全页视图（非对话框），使用 SmoothScroll。"""
    c = Colors.from_page(page)

    java_installations = config.get("java", "installations", default=[])
    java_options = [ft.DropdownOption("auto", text="自动选择")]
    for j in java_installations:
        label = f"{j['type']} {j['version']} ({j['vendor']})"
        java_options.append(ft.DropdownOption(j["id"], text=label))

    java_dropdown = ft.Dropdown(
        label="Java 版本",
        width=320,
        text_size=13,
        label_style=ft.TextStyle(size=13),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        options=java_options,
        value=_get_version_setting(version, "java", "auto"),
        on_select=lambda e: _set_version_setting(version, "java", e.control.value or "auto"),
    )

    mem_auto = _get_version_setting(version, "mem_auto", True)
    mem_auto_switch = ft.Switch(
        value=mem_auto,
        active_color=c["primary"],
        on_change=lambda e: _set_version_setting(version, "mem_auto", e.control.value),
    )

    mem_value = _get_version_setting(version, "mem_value", 4)
    mem_slider = ft.Slider(
        min=1, max=32, divisions=31, value=mem_value,
        label=f"{int(mem_value)} GB",
        active_color=c["primary"], width=200,
        on_change=lambda e: _set_version_setting(version, "mem_value", int(e.control.value)),
    )

    jvm_args_field = ft.TextField(
        label="JVM 参数",
        width=320,
        text_size=13,
        label_style=ft.TextStyle(size=13),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        value=_get_version_setting(version, "jvm_args", ""),
        hint_text="留空使用默认参数",
        on_blur=lambda e: _set_version_setting(version, "jvm_args", jvm_args_field.value or ""),
    )

    game_args_field = ft.TextField(
        label="游戏参数",
        width=320,
        text_size=13,
        label_style=ft.TextStyle(size=13),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        value=_get_version_setting(version, "game_args", ""),
        hint_text="留空使用默认参数",
        on_blur=lambda e: _set_version_setting(version, "game_args", game_args_field.value or ""),
    )

    renderer_dropdown = ft.Dropdown(
        label="渲染器",
        width=320,
        text_size=13,
        label_style=ft.TextStyle(size=13),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        options=[
            ft.DropdownOption("default", text="默认"),
            ft.DropdownOption("opengl", text="OpenGL"),
            ft.DropdownOption("directx", text="DirectX"),
            ft.DropdownOption("angle", text="ANGLE"),
        ],
        value=_get_version_setting(version, "renderer", "default"),
        on_select=lambda e: _set_version_setting(version, "renderer", e.control.value or "default"),
    )

    width_field = ft.TextField(
        label="窗口宽度", width=150, text_size=13,
        label_style=ft.TextStyle(size=13),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        value=_get_version_setting(version, "window_width", ""),
        hint_text="1280",
        keyboard_type=ft.KeyboardType.NUMBER,
        on_blur=lambda e: _set_version_setting(version, "window_width", width_field.value or ""),
    )
    height_field = ft.TextField(
        label="窗口高度", width=150, text_size=13,
        label_style=ft.TextStyle(size=13),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        value=_get_version_setting(version, "window_height", ""),
        hint_text="720",
        keyboard_type=ft.KeyboardType.NUMBER,
        on_blur=lambda e: _set_version_setting(version, "window_height", height_field.value or ""),
    )

    fullscreen_switch = ft.Switch(
        value=_get_version_setting(version, "fullscreen", False),
        active_color=c["primary"],
        on_change=lambda e: _set_version_setting(version, "fullscreen", e.control.value),
    )

    back_btn = ft.Container(
        content=ft.Row(
            controls=[ft.Icon(ft.Icons.ARROW_BACK, size=18), ft.Text("返回", size=13)],
            spacing=4,
        ),
        padding=ft.Padding(left=12, right=16, top=8, bottom=8),
        border_radius=8,
        border=ft.Border.all(1, c["outline_variant"]),
        ink=True,
        on_click=lambda _: on_back(),
    )

    def _setting_row(label, subtitle, control):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text(label, size=13, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                            ft.Text(subtitle, size=11, color=c["on_surface_variant"]),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    control,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=c["surface"],
            border_radius=8,
            border=ft.Border.all(1, c["outline_variant"]),
        )

    return SmoothScroll(
        page=page,
        controls=[
            build_topbar(
                page,
                f"版本设置 — {version}",
                state.username,
                state.logged_in,
                on_toggle_theme,
                on_user_click,
            ),
            ft.Container(height=4),
            ft.Row(controls=[back_btn]),
            ft.Container(height=4),
            _setting_row("Java 版本", "选择此版本使用的 Java", java_dropdown),
            _setting_row("自动分配内存", "根据系统内存自动分配", mem_auto_switch),
        ] + (
            [_setting_row("手动内存限制", "自动分配关闭时生效", mem_slider)] if not mem_auto else []
        ) + [
            _setting_row("渲染器", "游戏图形渲染方式", renderer_dropdown),
            _setting_row("JVM 参数", "覆盖默认 JVM 启动参数", jvm_args_field),
            _setting_row("游戏参数", "覆盖默认游戏启动参数", game_args_field),
            _setting_row("全屏模式", "启动时进入全屏", fullscreen_switch),
            ft.Text("窗口大小", size=13, weight=ft.FontWeight.W_500, color=c["on_surface"]),
            ft.Row(controls=[width_field, height_field], spacing=10),
            ft.Container(height=8),
        ],
        spacing=8,
        expand=True,
    )


# ===== 主视图 =====

def build_home_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_user_click=None,
    **kwargs,
) -> list:
    """构建首页视图。通过 AppState 的 home_subview 决定显示首页或版本设置。"""

    def _go_version_settings(version):
        state.home_subview = "version_settings"
        state.home_vs_version = version
        if on_navigate:
            on_navigate("/home")

    def _back_to_home():
        state.home_subview = "home"
        state.home_vs_version = ""
        if on_navigate:
            on_navigate("/home")

    if state.home_subview == "version_settings" and state.home_vs_version:
        content = _build_version_settings_page(
            page, state, state.home_vs_version, _back_to_home, on_toggle_theme, on_user_click,
        )
    else:
        content = _build_home_page(
            page, state, on_navigate, on_toggle_theme, on_user_click, _go_version_settings,
        )

    return [content]


def _build_home_page(
    page: ft.Page,
    state,
    on_navigate,
    on_toggle_theme,
    on_user_click,
    go_version_settings,
) -> ft.Control:
    """构建首页常规内容（启动横幅 + 新闻），使用 SmoothScroll。"""

    def on_play():
        _show_launch_selector(page, state, on_version_settings=go_version_settings)

    return SmoothScroll(
        page=page,
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
                on_play=on_play,
                on_download=lambda: on_navigate("/download") if on_navigate else None,
            ),
            ft.Container(height=8),
            _build_news_section(page, state),
        ],
        spacing=12,
        expand=True,
    )
