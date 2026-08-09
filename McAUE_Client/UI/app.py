"""应用协调器 - 管理页面布局、路由、主题切换、登录弹窗、自定义标题栏。

使用持久化布局：首次 render 构建 titlebar/sidebar/content 框架，
后续导航仅更新内容区并触发 AnimatedSwitcher 淡入淡出动画。
"""

import flet as ft

from theme.colors import Colors
from theme.theme_manager import ThemeManager
from state.app_state import AppState
from components.sidebar import build_sidebar
from components.titlebar import build_titlebar
from components.login_dialog import build_login_dialog
from views.home_view import build_home_view
from views.download_view import build_download_view
from views.tools_view import build_tools_view
from views.settings_view import build_settings_view
from views.about_view import build_about_view


class McAUEApp:
    """主应用控制器。"""

    def __init__(self):
        self.state = AppState()
        self.theme = ThemeManager()
        self._titlebar_container = None
        self._sidebar_container = None
        self._content_switcher = None
        self._layout_initialized = False
        self._login_dialog_open = False

    # ===== 主题 =====

    def apply_theme(self, page: ft.Page):
        page.theme = Colors.build_theme("light")
        page.dark_theme = Colors.build_theme("dark")
        page.theme_mode = (
            ft.ThemeMode.DARK if self.theme.is_dark else ft.ThemeMode.LIGHT
        )
        c = Colors.get("dark" if self.theme.is_dark else "light")
        page.bgcolor = c["background"]

    def toggle_theme(self, page: ft.Page):
        self.theme.toggle()
        self.apply_theme(page)
        self.render(page)

    def set_theme(self, page: ft.Page, mode: str):
        self.theme.set_mode(mode)
        self.apply_theme(page)
        self.render(page)

    # ===== 导航 =====

    def navigate(self, page: ft.Page, route: str):
        self.state.current_route = route
        self.render(page)

    def handle_user_click(self, page: ft.Page):
        if self.state.logged_in:
            self.state.settings_tab = "manage"
            self.navigate(page, "/settings")
        else:
            self.show_login(page)

    # ===== 登录弹窗 =====

    def show_login(self, page: ft.Page, initial_state=None):
        self._login_dialog_open = True
        dialog = build_login_dialog(
            page,
            self.state,
            on_login=lambda u: self._on_login_close(page),
            on_cancel=lambda: self._on_login_cancel(),
            initial_state=initial_state,
        )
        page.show_dialog(dialog)

    def _on_login_close(self, page: ft.Page):
        self._login_dialog_open = False
        self.render(page)

    def _on_login_cancel(self):
        self._login_dialog_open = False

    def _rebuild_login_dialog(self, page: ft.Page):
        """读取当前弹窗输入状态，用新主题重建弹窗。"""
        fields = getattr(page, "_login_fields", None)
        saved = None
        if fields:
            saved = {
                "login_type": fields["login_type"]["value"],
                "offline_name": fields["offline_name"].value or "",
                "official_email": fields["official_email"].value or "",
                "official_pass": fields["official_pass"].value or "",
                "third_name": fields["third_name"].value or "",
                "third_pass": fields["third_pass"].value or "",
                "third_auth": fields["third_auth"].value or "",
                "third_reg": fields["third_reg"].value or "",
                "third_sname": fields["third_sname"].value or "",
            }
        try:
            page.pop_dialog()
        except Exception:
            pass
        self.show_login(page, initial_state=saved)

    def logout(self, page: ft.Page):
        self.state.logout()
        self.render(page)

    # ===== 渲染 =====

    def _build_content(self, page: ft.Page) -> list:
        route = self.state.current_route

        nav = [
            ("/home", build_home_view),
            ("/download", build_download_view),
            ("/tools", build_tools_view),
            ("/settings", build_settings_view),
            ("/about", build_about_view),
        ]

        view_builder = build_home_view
        for r, builder in nav:
            if route == r:
                view_builder = builder
                break

        kwargs = {
            "page": page,
            "state": self.state,
            "on_navigate": lambda rt: self.navigate(page, rt),
            "on_toggle_theme": lambda: self.toggle_theme(page),
            "on_set_theme": lambda mode: self.set_theme(page, mode),
            "on_user_click": lambda: self.handle_user_click(page),
            "theme_mode": self.theme.mode,
        }
        if route == "/settings":
            kwargs["on_logout"] = lambda: self.logout(page)

        return view_builder(**kwargs)

    def _build_content_column(self, page: ft.Page) -> ft.Column:
        """构建内容区 Column，附带唯一 key 供 AnimatedSwitcher 识别切换。"""
        key = self.state.current_route
        if key == "/download":
            key += ":" + self.state.download_category
        key += ":" + ("dark" if self.theme.is_dark else "light")
        col = ft.Column(
            controls=self._build_content(page),
            spacing=12,
            expand=True,
        )
        col.key = key
        return col

    def _init_layout(self, page: ft.Page):
        """首次渲染：构建持久化页面框架。"""
        self._titlebar_container = ft.Container(content=build_titlebar(page))

        self._sidebar_container = ft.Container(
            content=build_sidebar(
                page,
                self.state.current_route,
                on_navigate=lambda rt: self.navigate(page, rt),
            ),
        )

        self._content_switcher = ft.AnimatedSwitcher(
            content=self._build_content_column(page),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=300,
            reverse_duration=200,
            expand=True,
        )

        content_area = ft.Container(
            content=self._content_switcher,
            expand=True,
            padding=ft.Padding(left=16, right=20, top=16, bottom=16),
        )

        main_row = ft.Row(
            controls=[self._sidebar_container, content_area],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            expand=True,
        )

        page.add(
            ft.Column(
                controls=[self._titlebar_container, main_row],
                spacing=0,
                expand=True,
            )
        )
        self._layout_initialized = True

    def render(self, page: ft.Page):
        if hasattr(page, "_mem_stop") and page._mem_stop:
            page._mem_stop["active"] = False
            page._mem_stop = None

        if not self._layout_initialized:
            self._init_layout(page)
            page.update()
            return

        self._titlebar_container.content = build_titlebar(page)

        self._sidebar_container.content = build_sidebar(
            page,
            self.state.current_route,
            on_navigate=lambda rt: self.navigate(page, rt),
        )

        self._content_switcher.content = self._build_content_column(page)

        page.update()


def run_app(page: ft.Page):
    """Flet 入口函数。"""
    page.title = "McAUE - Minecraft 客户端"
    page.window.width = 1100
    page.window.height = 700
    page.window.min_width = 900
    page.window.min_height = 600
    page.window.title_bar_hidden = True
    page.padding = 0

    app = McAUEApp()

    if page.platform_brightness is not None:
        app.theme.set_system_dark(page.platform_brightness == ft.Brightness.DARK)

    def on_brightness_change(e):
        if app.theme.is_system:
            app.theme.set_system_dark(e.data == ft.Brightness.DARK.value)
            app.apply_theme(page)
            if app._login_dialog_open:
                app.render(page)
                app._rebuild_login_dialog(page)
            else:
                app.render(page)

    page.on_platform_brightness_change = on_brightness_change

    app.apply_theme(page)
    app.render(page)
