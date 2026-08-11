"""杂项设置页面。"""

import flet as ft

from theme.colors import Colors
from components.animation import SmoothScroll
from state.config import config
from ._common import build_section_title, build_setting_row, make_switch, show_msg


def build_misc_page(page):
    c = Colors.from_page(page)
    mc = config.get("misc")

    fps_slider = ft.Slider(
        min=1, max=60, divisions=59, value=mc.get("max_fps", 60),
        label="{value} FPS",
        active_color=c["primary"], width=300,
    )
    fps_slider.on_change = lambda e: config.set("misc", "max_fps", int(fps_slider.value))

    log_lines_slider = ft.Slider(
        min=50, max=2000, divisions=39, value=mc.get("log_lines", 500),
        label="{value} 行",
        active_color=c["primary"], width=300,
    )
    log_lines_slider.on_change = lambda e: config.set("misc", "log_lines", int(log_lines_slider.value))

    hw_accel_switch = make_switch(page, mc.get("disable_hw_accel", False))
    hw_accel_switch.on_change = lambda e: config.set("misc", "disable_hw_accel", hw_accel_switch.value)

    telemetry_switch = make_switch(page, mc.get("telemetry", False))
    telemetry_switch.on_change = lambda e: config.set("misc", "telemetry", telemetry_switch.value)

    dual_switch_row_sys = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("禁用硬件加速", size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                        hw_accel_switch,
                    ],
                    spacing=8,
                ),
                ft.Container(width=24),
                ft.Row(
                    controls=[
                        ft.Text("启用遥测数据收集", size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                        telemetry_switch,
                    ],
                    spacing=8,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        bgcolor=c["surface"],
        border_radius=10,
        border=ft.Border.all(1, c["outline_variant"]),
    )

    def _cfg_btn(text, icon, on_click=None):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color="#FFFFFF", size=16),
                    ft.Text(text, size=13, weight=ft.FontWeight.W_500, color="#FFFFFF"),
                ],
                spacing=6,
            ),
            padding=ft.Padding(left=16, right=16, top=10, bottom=10),
            border_radius=8,
            bgcolor=c["primary"],
            ink=True,
            expand=True,
            alignment=ft.Alignment.CENTER,
            on_click=on_click,
        )

    async def _on_export(e):
        picker = ft.FilePicker()
        page.services.append(picker)
        page.update()
        path = await picker.save_file(
            dialog_title="导出配置",
            file_name="mcaue_config.json",
            allowed_extensions=["json"],
        )
        if path:
            if config.export_config(path):
                show_msg(page, "配置已导出")
            else:
                show_msg(page, "导出失败")

    async def _on_import(e):
        picker = ft.FilePicker()
        page.services.append(picker)
        page.update()
        result = await picker.pick_files(
            dialog_title="导入配置",
            allowed_extensions=["json"],
        )
        if result and len(result) > 0:
            if config.import_config(result[0].path):
                show_msg(page, "配置已导入，重启后生效")
            else:
                show_msg(page, "导入失败")

    def _on_clear_cache(e):
        def on_confirm(ev):
            try:
                page.pop_dialog()
            except Exception:
                pass
            if config.clear_cache():
                show_msg(page, "缓存已清除")
            else:
                show_msg(page, "清除失败")

        confirm_dialog = ft.AlertDialog(
            title=ft.Text("确认清除缓存", size=16),
            content=ft.Text("确定要清除所有缓存吗？", size=13),
            actions=[
                ft.TextButton("取消", on_click=lambda e: page.pop_dialog()),
                ft.TextButton("确定", on_click=on_confirm),
            ],
        )
        page.show_dialog(confirm_dialog)

    cfg_buttons_row = ft.Row(
        controls=[
            _cfg_btn("导出配置", ft.Icons.FILE_DOWNLOAD_OUTLINED, _on_export),
            _cfg_btn("导入配置", ft.Icons.FILE_UPLOAD_OUTLINED, _on_import),
            _cfg_btn("清除缓存", ft.Icons.CLEANING_SERVICES, _on_clear_cache),
        ],
        spacing=8,
    )

    doh_switch = make_switch(page, mc.get("doh", False))
    doh_switch.on_change = lambda e: config.set("misc", "doh", doh_switch.value)

    proxy_radio = ft.RadioGroup(
        value=mc.get("proxy_mode", "none"),
        content=ft.Row(
            controls=[
                ft.Radio(value="none", label="不使用代理", active_color=c["primary"]),
                ft.Radio(value="system", label="使用系统代理", active_color=c["primary"]),
                ft.Radio(value="custom", label="自定义代理", active_color=c["primary"]),
            ],
            spacing=20,
        ),
    )

    proxy_addr_field = ft.TextField(
        hint_text="比如 http://127.0.0.1:1080/",
        width=400, text_size=13,
        border_color=c["outline"], color=c["on_surface"],
        bgcolor=c["surface_variant"], filled=True,
        value=mc.get("proxy_addr", ""),
    )

    proxy_user_field = ft.TextField(
        label="账号", hint_text="如有",
        width=180, text_size=13,
        border_color=c["outline"], color=c["on_surface"],
        bgcolor=c["surface_variant"], filled=True,
        value=mc.get("proxy_user", ""),
    )

    proxy_pass_field = ft.TextField(
        label="密码", hint_text="如有", password=True, can_reveal_password=True,
        width=180, text_size=13,
        border_color=c["outline"], color=c["on_surface"],
        bgcolor=c["surface_variant"], filled=True,
        value=mc.get("proxy_pass", ""),
    )

    def _on_apply_proxy(e):
        config.set("misc", "proxy_mode", proxy_radio.value)
        config.set("misc", "proxy_addr", proxy_addr_field.value)
        config.set("misc", "proxy_user", proxy_user_field.value)
        config.set("misc", "proxy_pass", proxy_pass_field.value)
        show_msg(page, "代理信息已保存")

    proxy_apply_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.CHECK, color="#FFFFFF", size=16),
                ft.Text("应用代理信息", size=13, weight=ft.FontWeight.W_500, color="#FFFFFF"),
            ],
            spacing=6,
        ),
        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        border_radius=8,
        bgcolor=c["primary"],
        ink=True,
        on_click=_on_apply_proxy,
    )

    proxy_custom_panel = ft.Container(
        content=ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.WARNING_AMBER, color="#FFFFFF", size=18),
                            ft.Text("请勿填写不信任的代理地址", size=13, weight=ft.FontWeight.W_500, color="#FFFFFF"),
                        ],
                        spacing=8,
                    ),
                    padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                    border_radius=8,
                    bgcolor="#DAA520",
                ),
                proxy_addr_field,
                ft.Row(
                    controls=[proxy_user_field, proxy_pass_field],
                    spacing=12,
                ),
                ft.Row(
                    controls=[ft.Container(expand=True), proxy_apply_btn],
                ),
            ],
            spacing=10,
        ),
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        bgcolor=c["surface"],
        border_radius=10,
        border=ft.Border.all(1, c["outline_variant"]),
        visible=(mc.get("proxy_mode", "none") == "custom"),
    )

    def on_proxy_change(e):
        val = proxy_radio.value
        proxy_custom_panel.visible = (val == "custom")
        config.set("misc", "proxy_mode", val)
        try:
            proxy_custom_panel.update()
        except Exception:
            pass

    proxy_radio.on_change = on_proxy_change

    anim_speed_slider = ft.Slider(
        min=1, max=31, divisions=30, value=mc.get("anim_speed", 10),
        label="关闭" if mc.get("anim_speed", 10) >= 31 else f"{mc.get('anim_speed', 10) / 10:.1f}x",
        active_color=c["primary"], width=300,
    )

    def on_anim_speed_change(e):
        val = int(anim_speed_slider.value)
        anim_speed_slider.label = "关闭" if val >= 31 else f"{val / 10:.1f}x"
        config.set("misc", "anim_speed", val)
        try:
            anim_speed_slider.update()
        except Exception:
            pass

    anim_speed_slider.on_change = on_anim_speed_change

    no_copy_switch = make_switch(page, mc.get("no_copy_on_download", False))
    no_copy_switch.on_change = lambda e: config.set("misc", "no_copy_on_download", no_copy_switch.value)

    debug_switch = make_switch(page, mc.get("debug_mode", False))
    debug_switch.on_change = lambda e: config.set("misc", "debug_mode", debug_switch.value)

    dual_switch_row_debug = ft.Container(
        content=ft.Row(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("禁止在下载时从其他文件夹复制文件", size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                        no_copy_switch,
                    ],
                    spacing=8,
                ),
                ft.Container(width=24),
                ft.Row(
                    controls=[
                        ft.Text("调试模式", size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                        debug_switch,
                    ],
                    spacing=8,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        bgcolor=c["surface"],
        border_radius=10,
        border=ft.Border.all(1, c["outline_variant"]),
    )

    return SmoothScroll(
        page=page,
        controls=[
            build_section_title(page, "杂项", ft.Icons.TUNE_OUTLINED),

            ft.Text("系统", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "最高动画帧率", "", fps_slider),
            build_setting_row(page, "实时日志行数", "", log_lines_slider),
            dual_switch_row_sys,
            cfg_buttons_row,

            ft.Text("网络", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "使用 DoH 解析地址", "通过 DNS over HTTPS 解析域名", doh_switch),
            build_setting_row(page, "HTTP 代理", "选择代理方式", proxy_radio),
            proxy_custom_panel,

            ft.Text("调试选项", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "动画速度", "", anim_speed_slider),
            dual_switch_row_debug,
        ],
        spacing=8,
        expand=True,
    )
