"""关于视图 - 应用信息、技术栈、快捷操作、致谢、日志管理。"""

import os
import platform
import subprocess
import webbrowser
import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar
from components.animation import SmoothScroll
from core.updater import updater
from core.logger import log_manager

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


def _show_msg(page, msg):
    dialog = ft.AlertDialog(
        title=ft.Text("提示", size=16),
        content=ft.Text(msg, size=13),
        actions=[ft.TextButton("确定", on_click=lambda e: page.pop_dialog())],
    )
    page.show_dialog(dialog)


def _build_about_page(
    page: ft.Page,
    state,
    on_toggle_theme,
    on_user_click,
    go_log_view,
) -> ft.Control:
    """构建关于页面常规内容。"""
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
                    content=ft.Text(f"v{updater.VERSION}", size=12, color=c["secondary"], weight=ft.FontWeight.W_600),
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
            _build_info_row(page, "运行时", f"Python {platform.python_version()}", ft.Icons.CODE),
            _build_info_row(page, "UI 框架", f"Flet {ft.version.__version__}", ft.Icons.DASHBOARD),
        ],
        spacing=6,
    )

    def _build_card_btn(icon, label, on_click):
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
            _build_card_btn(
                ft.Icons.FEEDBACK_OUTLINED, "反馈",
                lambda _: webbrowser.open(f"{GITHUB_URL}/issues"),
            ),
            _build_card_btn(
                ft.Icons.DESCRIPTION_OUTLINED, "查看日志",
                lambda _: go_log_view(),
            ),
            _build_card_btn(
                ft.Icons.CODE, "GitHub",
                lambda _: webbrowser.open(GITHUB_URL),
            ),
        ],
        spacing=10,
    )

    credits = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("致谢", size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
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

    return SmoothScroll(
        page=page,
        controls=[
            build_topbar(page, "关于", state.username, state.logged_in, on_toggle_theme, on_user_click),
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
            ft.Text("© 2026 McAUE · 仅供学习交流使用", size=11, color=c["on_surface_variant"], text_align=ft.TextAlign.CENTER),
        ],
        spacing=8,
        expand=True,
    )


def _build_log_view(
    page: ft.Page,
    state,
    on_back,
    on_toggle_theme,
    on_user_click,
) -> ft.Control:
    """构建日志管理全页视图。"""
    c = Colors.from_page(page)
    log_files = log_manager.get_log_files()

    if not log_files:
        import time
        from core.logger import LogFileInfo
        now = time.strftime("%Y/%m/%d %H:%M:%S")
        log_dir = log_manager.get_log_dir()
        log_files = [
            LogFileInfo(
                filename="Launch-2026-8-10-171137.log",
                filepath=os.path.join(log_dir, "Launch-2026-8-10-171137.log"),
                timestamp=now,
                size=2048,
                is_current=True,
            ),
            LogFileInfo(
                filename="Launch-2026-8-10-152201.log",
                filepath=os.path.join(log_dir, "Launch-2026-8-10-152201.log"),
                timestamp="2026/8/10 15:22:01",
                size=15360,
                is_current=False,
            ),
            LogFileInfo(
                filename="Launch-2026-8-10-120533.log",
                filepath=os.path.join(log_dir, "Launch-2026-8-10-120533.log"),
                timestamp="2026/8/10 12:05:33",
                size=8192,
                is_current=False,
            ),
            LogFileInfo(
                filename="Launch-2026-8-9-201445.log",
                filepath=os.path.join(log_dir, "Launch-2026-8-9-201445.log"),
                timestamp="2026/8/9 20:14:45",
                size=12288,
                is_current=False,
            ),
        ]

    log_list_column = ft.Column(spacing=4)

    def _format_size(size):
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / 1024 / 1024:.1f} MB"

    def _build_log_file_row(info):
        is_current = info.is_current
        icon_color = c["primary"] if is_current else c["on_surface_variant"]
        name_color = c["primary"] if is_current else c["on_surface"]

        badges = []
        if is_current:
            badges.append(
                ft.Container(
                    content=ft.Text("当前", size=10, color="#FFFFFF"),
                    padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                    border_radius=4,
                    bgcolor=c["primary"],
                )
            )
        badges.append(
            ft.Container(
                content=ft.Text(_format_size(info.size), size=10, color=c["on_surface_variant"]),
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                border_radius=4,
                bgcolor=c["surface_variant"],
            )
        )

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.DESCRIPTION, color=icon_color, size=20),
                    ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Text(info.timestamp, size=13, weight=ft.FontWeight.W_500, color=name_color),
                                    *badges,
                                ],
                                spacing=6,
                            ),
                            ft.Text(
                                info.filename,
                                size=11,
                                color=c["on_surface_variant"],
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.VISIBILITY_OUTLINED, color=c["on_surface_variant"], size=18),
                        width=32,
                        height=32,
                        border_radius=6,
                        ink=True,
                        on_click=lambda e, f=info: _show_log_content(page, f),
                        alignment=ft.Alignment.CENTER,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(12, 10, 12, 10),
            border_radius=8,
            border=ft.Border.all(1, c["primary"] if is_current else c["outline_variant"]),
            bgcolor=c["primary_container"] if is_current else c["surface"],
        )

    for info in log_files:
        log_list_column.controls.append(_build_log_file_row(info))

    if not log_list_column.controls:
        log_list_column.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.DESCRIPTION_OUTLINED, color=c["on_surface_variant"], size=36),
                        ft.Text("暂无日志文件", size=14, color=c["on_surface_variant"]),
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(0, 32, 0, 32),
                alignment=ft.Alignment.CENTER,
            )
        )

    def _build_pill_btn(icon, label, on_click, is_danger=False):
        border_color = c["error"] if is_danger else c["primary"]
        text_color = c["error"] if is_danger else c["primary"]
        return ft.Container(
            content=ft.Row(
                controls=[ft.Icon(icon, size=16, color=text_color), ft.Text(label, size=13, color=text_color)],
                spacing=6,
            ),
            padding=ft.Padding(left=14, right=14, top=8, bottom=8),
            border_radius=8,
            border=ft.Border.all(1, border_color),
            ink=True,
            on_click=on_click,
        )

    action_panel = ft.Container(
        content=ft.Row(
            controls=[
                _build_pill_btn(ft.Icons.FILE_DOWNLOAD_OUTLINED, "导出日志", lambda e: _show_msg(page, "导出日志功能需要日志模块实现")),
                _build_pill_btn(ft.Icons.FOLDER_ZIP_OUTLINED, "导出全部日志", lambda e: _show_msg(page, "导出全部日志功能需要日志模块实现")),
                _build_pill_btn(ft.Icons.FOLDER_OPEN_OUTLINED, "打开日志目录", lambda e: _open_log_dir(page)),
                _build_pill_btn(ft.Icons.DELETE_SWEEP, "清理历史日志", lambda e: _clear_logs(page, log_list_column, c), is_danger=True),
                ft.Container(expand=True),
            ],
            spacing=8,
        ),
        padding=ft.Padding(14, 12, 14, 12),
        bgcolor=c["surface"],
        border_radius=10,
        border=ft.Border.all(1, c["outline_variant"]),
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

    return SmoothScroll(
        page=page,
        controls=[
            build_topbar(page, "日志管理", state.username, state.logged_in, on_toggle_theme, on_user_click),
            ft.Container(height=4),
            ft.Row(controls=[back_btn]),
            ft.Container(height=4),
            action_panel,
            ft.Container(height=4),
            ft.Text("所有日志", size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
            ft.Container(
                content=log_list_column,
                padding=ft.Padding(10, 10, 10, 10),
                bgcolor=c["surface"],
                border_radius=10,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
            ft.Container(height=4),
            ft.Text("日志文件管理功能需要日志核心模块实现，当前为示例数据。", size=11, color=c["on_surface_variant"]),
        ],
        spacing=8,
        expand=True,
    )


def _open_log_dir(page):
    log_dir = log_manager.get_log_dir()
    try:
        if os.path.exists(log_dir):
            if os.name == "nt":
                subprocess.Popen(["explorer", log_dir])
            else:
                subprocess.Popen(["xdg-open", log_dir])
        else:
            _show_msg(page, f"日志目录不存在：{log_dir}")
    except Exception:
        _show_msg(page, "无法打开日志目录")


def _clear_logs(page, list_column, c):
    result = log_manager.clear_logs()
    if result:
        list_column.controls.clear()
        list_column.controls.append(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=c["primary"], size=36),
                        ft.Text("历史日志已清理", size=14, color=c["on_surface_variant"]),
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(0, 32, 0, 32),
                alignment=ft.Alignment.CENTER,
            )
        )
        try:
            list_column.update()
        except Exception:
            pass
        _show_msg(page, "历史日志已清理")
    else:
        _show_msg(page, "日志清理功能需要日志模块实现")


def _show_log_content(page, file_info):
    """显示单个日志文件内容的对话框。"""
    c = Colors.from_page(page)
    logs = log_manager.get_logs(limit=500)

    log_list = ft.ListView(
        controls=[
            ft.Text(
                f"[{entry.timestamp}] {entry.level}: {entry.message}",
                size=11,
                color=c["on_surface_variant"],
                selectable=True,
            )
            for entry in logs
        ] if logs else [ft.Text("暂无日志记录或日志读取功能尚未实现", size=13, color=c["on_surface_variant"])],
        spacing=2,
        expand=True,
    )

    dialog = ft.AlertDialog(
        title=ft.Text(file_info.filename, size=14),
        content=ft.Container(
            content=log_list,
            width=600,
            height=400,
        ),
        actions=[
            ft.TextButton("关闭", on_click=lambda e: page.pop_dialog()),
        ],
    )
    page.show_dialog(dialog)


def build_about_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_user_click=None,
    **kwargs,
) -> list:
    """构建关于视图。通过 AppState 的 about_subview 决定显示关于页面或日志管理。"""

    def _go_log_view():
        state.about_subview = "log_view"
        if on_navigate:
            on_navigate("/about")

    def _back_to_about():
        state.about_subview = "about"
        if on_navigate:
            on_navigate("/about")

    if state.about_subview == "log_view":
        content = _build_log_view(page, state, _back_to_about, on_toggle_theme, on_user_click)
    else:
        content = _build_about_page(page, state, on_toggle_theme, on_user_click, _go_log_view)

    return [content]
