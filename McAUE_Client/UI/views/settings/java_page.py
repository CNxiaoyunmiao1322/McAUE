"""Java 设置页面。"""

import os
import glob
import flet as ft

from theme.colors import Colors
from components.animation import SmoothScroll
from state.config import config
from ._common import build_section_title


async def _pick_java(page, installations, counter, rebuild_fn, status_text, c):
    """通过文件选择器添加 Java 安装。"""
    picker = ft.FilePicker()
    page.services.append(picker)
    page.update()

    result = await picker.pick_files(
        dialog_title="选择 java.exe",
        allowed_extensions=["exe"],
    )

    if not result:
        return

    file_path = result[0].path
    java_dir = os.path.dirname(os.path.dirname(file_path))
    java_exe = os.path.join(java_dir, "bin", "java.exe")
    if not os.path.exists(java_exe):
        java_dir = os.path.dirname(file_path)
        java_exe = file_path

    dir_name = os.path.basename(java_dir)
    jtype = "JDK" if os.path.exists(os.path.join(java_dir, "bin", "javac.exe")) else "JRE"
    lower = java_dir.lower()
    if "adoptium" in lower or "temurin" in lower:
        vendor = "Eclipse Temurin"
    elif "zulu" in lower:
        vendor = "Zulu"
    elif "microsoft" in lower:
        vendor = "Microsoft"
    else:
        vendor = "Oracle"
    arch = "32 Bit" if "x86" in java_dir else "64 Bit"

    new_entry = {
        "id": f"java_{counter[0]}",
        "type": jtype, "version": dir_name,
        "arch": arch, "vendor": vendor, "path": java_dir,
    }
    counter[0] += 1
    installations.append(new_entry)
    config.set("java", "installations", installations)
    status_text.value = f"已添加: {jtype} {dir_name}"
    status_text.color = c["primary"]
    rebuild_fn()
    try:
        status_text.update()
    except Exception:
        pass


def build_java_page(page):
    c = Colors.from_page(page)
    jc = config.get("java")

    java_installations = jc.get("installations", [])

    selected = {"value": jc.get("selected", "auto")}
    java_counter = [len(java_installations)]
    list_column = ft.Column(controls=[], spacing=4)
    status_text = ft.Text("", size=12, color=c["on_surface_variant"])

    def make_badge(text, is_primary=False):
        if is_primary:
            return ft.Container(
                content=ft.Text(text, size=10, weight=ft.FontWeight.W_500, color=c["primary"]),
                padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                border_radius=4,
                bgcolor=c["primary_container"],
            )
        return ft.Container(
            content=ft.Text(text, size=10, color=c["on_surface_variant"]),
            padding=ft.Padding(left=6, right=6, top=2, bottom=2),
            border_radius=4,
            bgcolor=c["surface_variant"],
            border=ft.Border.all(1, c["outline_variant"]),
        )

    def build_item(item_id, title, subtitle, badges, path):
        is_sel = selected["value"] == item_id
        radio = ft.Icon(
            ft.Icons.RADIO_BUTTON_CHECKED if is_sel else ft.Icons.RADIO_BUTTON_UNCHECKED,
            color=c["primary"] if is_sel else c["on_surface_variant"],
            size=18,
        )

        title_controls = [ft.Text(title, size=14, weight=ft.FontWeight.W_600, color=c["on_surface"])]
        for b in badges:
            title_controls.append(b)
        title_row = ft.Row(controls=title_controls, spacing=8)

        col_controls = [title_row]
        if subtitle:
            col_controls.append(ft.Text(subtitle, size=12, color=c["on_surface_variant"]))
        if path:
            col_controls.append(
                ft.Text(path, size=11, color=c["on_surface_variant"], overflow=ft.TextOverflow.ELLIPSIS)
            )

        if is_sel:
            border = ft.Border(
                left=ft.BorderSide(4, c["primary"]),
                top=ft.BorderSide(1, c["primary"]),
                right=ft.BorderSide(1, c["primary"]),
                bottom=ft.BorderSide(1, c["primary"]),
            )
            bgcolor = c["primary_container"]
        else:
            border = ft.Border.all(1, c["outline_variant"])
            bgcolor = c["surface"]

        return ft.Container(
            content=ft.Row(
                controls=[
                    radio,
                    ft.Column(controls=col_controls, spacing=4, expand=True),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=16, right=16, top=12, bottom=12),
            bgcolor=bgcolor,
            border_radius=8,
            border=border,
            ink=True,
            on_click=lambda _, id=item_id: select_java(id),
        )

    def rebuild_list():
        items = [
            build_item("auto", "自动选择", "依据游戏需要自动选择合适的 Java", [], None),
        ]
        for java in java_installations:
            badges = [
                make_badge(java["arch"]),
                make_badge(java["vendor"], is_primary=True),
            ]
            items.append(build_item(
                java["id"],
                f"{java['type']} {java['version']}",
                None, badges, java["path"],
            ))
        list_column.controls = items
        try:
            list_column.update()
        except Exception:
            pass

    def select_java(item_id):
        if selected["value"] == item_id:
            return
        selected["value"] = item_id
        config.set("java", "selected", item_id)
        rebuild_list()

    def do_search(e):
        search_paths = [
            r"C:\Program Files\Java\*",
            r"C:\Program Files\Eclipse Adoptium\*",
            r"C:\Program Files\Zulu\*",
            r"C:\Program Files\Microsoft\jdk-*",
            r"C:\Program Files (x86)\Java\*",
        ]
        found = []
        for pattern in search_paths:
            for path in glob.glob(pattern):
                java_exe = os.path.join(path, "bin", "java.exe")
                if not os.path.exists(java_exe):
                    continue
                dir_name = os.path.basename(path)
                jtype = "JDK" if os.path.exists(os.path.join(path, "bin", "javac.exe")) else "JRE"
                lower = path.lower()
                if "adoptium" in lower or "temurin" in lower:
                    vendor = "Eclipse Temurin"
                elif "zulu" in lower:
                    vendor = "Zulu"
                elif "microsoft" in lower:
                    vendor = "Microsoft"
                else:
                    vendor = "Oracle"
                arch = "32 Bit" if "x86" in path else "64 Bit"
                found.append({
                    "id": f"java_{java_counter[0]}",
                    "type": jtype, "version": dir_name,
                    "arch": arch, "vendor": vendor, "path": path,
                })
                java_counter[0] += 1

        if found:
            java_installations.clear()
            java_installations.extend(found)
            config.set("java", "installations", found)
            status_text.value = f"搜索完成，找到 {len(found)} 个 Java 安装"
        else:
            status_text.value = "未找到 Java 安装，请手动添加"
        status_text.color = c["primary"] if found else c["error"]
        rebuild_list()
        try:
            status_text.update()
        except Exception:
            pass

    rebuild_list()

    search_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.SEARCH, color="#FFFFFF", size=16),
                ft.Text("自动搜索", size=13, weight=ft.FontWeight.W_500, color="#FFFFFF"),
            ],
            spacing=6,
        ),
        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        border_radius=8,
        bgcolor=c["primary"],
        ink=True,
        on_click=do_search,
    )

    add_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD, color=c["on_surface"], size=16),
                ft.Text("添加", size=13, weight=ft.FontWeight.W_500, color=c["on_surface"]),
            ],
            spacing=6,
        ),
        padding=ft.Padding(left=16, right=16, top=10, bottom=10),
        border_radius=8,
        bgcolor=c["surface_variant"],
        border=ft.Border.all(1, c["outline"]),
        ink=True,
        on_click=lambda e: page.run_task(_pick_java, page, java_installations, java_counter, rebuild_list, status_text, c),
    )

    return SmoothScroll(
        page=page,
        controls=[
            build_section_title(page, "Java", ft.Icons.COFFEE_OUTLINED),
            ft.Row(controls=[search_btn, add_btn, ft.Container(expand=True)], spacing=8),
            status_text,
            ft.Container(
                content=list_column,
                padding=ft.Padding(8, 8, 8, 8),
                bgcolor=c["surface"],
                border_radius=12,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
        ],
        spacing=8,
        expand=True,
    )
