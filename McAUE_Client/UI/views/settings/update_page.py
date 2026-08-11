"""软件更新设置页面。"""

import flet as ft

from theme.colors import Colors
from components.animation import SmoothScroll
from state.config import config
from core.updater import updater
from ._common import build_section_title, build_setting_row, make_dropdown, make_switch, make_button


def build_update_page(page):
    c = Colors.from_page(page)
    uc = config.get("update")

    channel_dropdown = make_dropdown(page, uc.get("channel", "stable"), [
        ft.dropdown.Option("stable", "正式版"),
        ft.dropdown.Option("beta", "测试版"),
        ft.dropdown.Option("dev", "开发版"),
    ])
    channel_dropdown.on_select = lambda e: config.set("update", "channel", e.control.value)

    beta_notify_sw = make_switch(page, uc.get("beta_update_notify", False))
    beta_notify_sw.on_change = lambda e: config.set("update", "beta_update_notify", beta_notify_sw.value)

    beta_update_row = build_setting_row(page, "测试版更新提示", "接收快照/测试版更新通知", beta_notify_sw)
    beta_update_row.visible = uc.get("channel", "stable") != "stable"

    def on_channel_change(e):
        val = e.control.value
        beta_update_row.visible = val != "stable"
        config.set("update", "channel", val)
        try:
            beta_update_row.update()
        except Exception:
            pass

    channel_dropdown.on_select = on_channel_change

    stable_notify_sw = make_switch(page, uc.get("stable_update_notify", True))
    stable_notify_sw.on_change = lambda e: config.set("update", "stable_update_notify", stable_notify_sw.value)

    auto_update_sw = make_switch(page, uc.get("auto_update", True))
    auto_update_sw.on_change = lambda e: config.set("update", "auto_update", auto_update_sw.value)

    version_text = ft.Text(f"当前版本：v{updater.VERSION}", size=14, weight=ft.FontWeight.W_600, color=c["on_surface"])
    status_text = ft.Text("已是最新版本", size=12, color=c["on_surface_variant"])
    status_icon = ft.Icon(ft.Icons.CHECK_CIRCLE, color=c["primary"], size=28)

    def _on_check_update(e):
        status_icon.icon = ft.Icons.REFRESH
        status_icon.color = c["on_surface_variant"]
        status_text.value = "正在检查更新..."
        try:
            status_icon.update()
            status_text.update()
        except Exception:
            pass

        update_info = updater.check_update(uc.get("channel", "stable"))

        if update_info.has_update:
            status_icon.icon = ft.Icons.DOWNLOAD_ROUNDED
            status_icon.color = c["primary"]
            status_text.value = f"发现新版本：v{update_info.latest_version}"
        else:
            status_icon.icon = ft.Icons.CHECK_CIRCLE
            status_icon.color = c["primary"]
            status_text.value = "已是最新版本"

        try:
            status_icon.update()
            status_text.update()
        except Exception:
            pass

    return SmoothScroll(
        page=page,
        controls=[
            build_section_title(page, "软件更新", ft.Icons.SYSTEM_UPDATE_ALT_OUTLINED),
            ft.Container(
                content=ft.Row(
                    controls=[
                        status_icon,
                        ft.Column(
                            controls=[
                                version_text,
                                status_text,
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        make_button(page, "检查更新", ft.Icons.REFRESH, on_click=_on_check_update),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(16, 16, 16, 16),
                bgcolor=c["surface"],
                border_radius=10,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
            build_setting_row(page, "更新通道", "选择更新发布通道", channel_dropdown),
            build_setting_row(page, "正式版更新提示", "接收 Minecraft 正式版更新通知", stable_notify_sw),
            beta_update_row,
            build_setting_row(page, "自动更新", "有新版本时自动下载更新", auto_update_sw),
        ],
        spacing=8,
        expand=True,
    )
