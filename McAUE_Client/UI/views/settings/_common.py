"""设置页面共享工具函数。"""

import psutil
import flet as ft

from theme.colors import Colors
from state.config import config


def get_memory_info():
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024**3)
    used_gb = mem.used / (1024**3)
    return round(total_gb, 1), round(used_gb, 1)


def build_section_title(page: ft.Page, title: str, icon: str) -> ft.Control:
    c = Colors.from_page(page)
    return ft.Row(
        controls=[
            ft.Icon(icon, color=c["primary"], size=20),
            ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
        ],
        spacing=8,
    )


def build_setting_row(page: ft.Page, label: str, subtitle: str, control: ft.Control) -> ft.Control:
    c = Colors.from_page(page)
    label_controls = [
        ft.Text(label, size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
    ]
    if subtitle:
        label_controls.append(ft.Text(subtitle, size=12, color=c["on_surface_variant"]))
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(
                    controls=label_controls,
                    spacing=2,
                    expand=True,
                ),
                control,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding(left=16, right=16, top=12, bottom=12),
        bgcolor=c["surface"],
        border_radius=10,
        border=ft.Border.all(1, c["outline_variant"]),
    )


def make_dropdown(page, value, options, width=160):
    c = Colors.from_page(page)
    return ft.Dropdown(
        value=value,
        options=options,
        width=width,
        text_size=13,
        border_color=c["outline"],
        color=c["on_surface"],
        bgcolor=c["surface_variant"],
        filled=True,
    )


def make_switch(page, value=True):
    c = Colors.from_page(page)
    return ft.Switch(value=value, active_color=c["primary"])


def make_text_field(page, label, hint, icon=ft.Icons.FOLDER_OUTLINED):
    c = Colors.from_page(page)
    return ft.TextField(
        label=label,
        hint_text=hint,
        prefix_icon=icon,
        border_color=c["outline"],
        focused_border_color=c["primary"],
        color=c["on_surface"],
        bgcolor=c["surface_variant"],
        filled=True,
        width=300,
        text_size=13,
    )


def show_msg(page, msg):
    dialog = ft.AlertDialog(
        title=ft.Text("提示", size=16),
        content=ft.Text(msg, size=13),
        actions=[
            ft.TextButton("确定", on_click=lambda e: page.pop_dialog()),
        ],
    )
    page.show_dialog(dialog)


def make_button(page, text, icon, bgcolor_key="primary", on_click=None):
    c = Colors.from_page(page)
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
        bgcolor=c[bgcolor_key],
        ink=True,
        on_click=on_click,
    )


def cfg_switch(page, section, key, default):
    """创建绑定到 config 的开关控件。"""
    sw = make_switch(page, config.get(section, {}).get(key, default))
    sw.on_change = lambda e, k=key, s=section: config.set(s, k, e.control.value)
    return sw
