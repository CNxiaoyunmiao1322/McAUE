"""下载页视图 - 多级菜单下载管理。

菜单结构：
  Minecraft（安装版本）→ 版本列表（正式版/预览版/远古版/愚人节版）
  社区资源（折叠框）→ 模组/整合包/数据包/资源包/光影包
  安装包（折叠框）→ Minecraft(.jar)/OptiFine/Forge/NeoForge/Fabric/Legacy Fabric/Quilt/LiteLoader
"""

import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar


# ===== 菜单数据 =====

MENU_ITEMS = [
    {
        "id": "mc_install",
        "label": "Minecraft",
        "subtitle": "安装版本",
        "icon": ft.Icons.VIDEOGAME_ASSET,
        "type": "leaf",
    },
    {
        "id": "community",
        "label": "社区资源",
        "icon": ft.Icons.PUBLIC,
        "type": "group",
        "children": [
            {"id": "community_mods", "label": "模组", "icon": ft.Icons.EXTENSION},
            {"id": "community_modpacks", "label": "整合包", "icon": ft.Icons.INVENTORY_2},
            {"id": "community_datapacks", "label": "数据包", "icon": ft.Icons.STORAGE},
            {"id": "community_resourcepacks", "label": "资源包", "icon": ft.Icons.IMAGE},
            {"id": "community_shaders", "label": "光影包", "icon": ft.Icons.WB_SUNNY},
        ],
    },
    {
        "id": "installers",
        "label": "安装包",
        "icon": ft.Icons.DOWNLOAD,
        "type": "group",
        "children": [
            {"id": "installer_mc_jar", "label": "Minecraft", "subtitle": ".jar", "icon": ft.Icons.VIDEOGAME_ASSET},
            {"id": "installer_optifine", "label": "OptiFine", "icon": ft.Icons.VISIBILITY},
            {"id": "installer_forge", "label": "Forge", "icon": ft.Icons.BUILD},
            {"id": "installer_neoforge", "label": "NeoForge", "icon": ft.Icons.BUILD_CIRCLE},
            {"id": "installer_fabric", "label": "Fabric", "icon": ft.Icons.TEXTURE},
            {"id": "installer_legacy_fabric", "label": "Legacy Fabric", "icon": ft.Icons.TEXTURE_OUTLINED},
            {"id": "installer_quilt", "label": "Quilt", "icon": ft.Icons.GRID_VIEW},
            {"id": "installer_liteloader", "label": "LiteLoader", "icon": ft.Icons.EGG},
        ],
    },
]


# ===== 版本数据 =====

VERSION_CATEGORIES = [
    {"id": "release", "label": "正式版", "icon": ft.Icons.STAR},
    {"id": "snapshot", "label": "预览版", "icon": ft.Icons.SCIENCE},
    {"id": "old", "label": "远古版", "icon": ft.Icons.HISTORY},
    {"id": "fools", "label": "愚人节版", "icon": ft.Icons.EMOJI_EMOTIONS},
]

ALL_VERSIONS = {
    "release": [
        ("1.21.5", False), ("1.21.4", True), ("1.21.3", False),
        ("1.20.6", True), ("1.20.4", False), ("1.19.4", False),
        ("1.18.2", False), ("1.16.5", True), ("1.12.2", False),
        ("1.8.9", False), ("1.7.10", False),
    ],
    "snapshot": [
        ("1.21.5-rc1", False), ("25w08a", False), ("25w07a", False),
        ("24w45a", False), ("1.21.4-rc1", False),
    ],
    "old": [
        ("b1.8.1", False), ("b1.7.3", False), ("a1.2.6", False),
        ("infdev", False), ("Classic 0.30", False),
    ],
    "fools": [
        ("22w13one", False), ("20w14infinite", False),
        ("15w14a", False), ("1.RV-Pre1", False), ("2.0", False),
    ],
}


# ===== 菜单项构建 =====

def _build_leaf_item(c, item, is_selected, on_click) -> ft.Control:
    icon_color = c["primary"] if is_selected else c["on_surface_variant"]
    text_color = c["primary"] if is_selected else c["on_surface"]
    bg = c["primary_container"] if is_selected else ft.Colors.TRANSPARENT

    left_controls = [
        ft.Icon(item["icon"], color=icon_color, size=20),
        ft.Text(item["label"], size=14, weight=ft.FontWeight.W_500, color=text_color),
    ]
    if "subtitle" in item:
        left_controls.append(
            ft.Text(item["subtitle"], size=11, color=c["on_surface_variant"])
        )

    return ft.Container(
        content=ft.Row(controls=left_controls, spacing=10),
        padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        border_radius=8,
        bgcolor=bg,
        ink=True,
        on_click=lambda _: on_click(item["id"]),
    )


def _build_group_header(c, item, is_expanded, on_toggle) -> ft.Control:
    arrow = ft.Icons.EXPAND_MORE if is_expanded else ft.Icons.CHEVRON_RIGHT

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(item["icon"], color=c["on_surface_variant"], size=20),
                ft.Text(item["label"], size=14, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                ft.Container(expand=True),
                ft.Icon(arrow, color=c["on_surface_variant"], size=18),
            ],
            spacing=10,
        ),
        padding=ft.Padding(left=14, right=14, top=10, bottom=10),
        border_radius=8,
        ink=True,
        on_click=lambda _: on_toggle(item["id"]),
    )


def _build_child_item(c, child, is_selected, on_click) -> ft.Control:
    icon_color = c["primary"] if is_selected else c["on_surface_variant"]
    text_color = c["primary"] if is_selected else c["on_surface"]
    bg = c["primary_container"] if is_selected else ft.Colors.TRANSPARENT

    left_controls = [
        ft.Icon(child["icon"], color=icon_color, size=18),
        ft.Text(child["label"], size=13, weight=ft.FontWeight.W_500, color=text_color),
    ]
    if "subtitle" in child:
        left_controls.append(
            ft.Text(child["subtitle"], size=10, color=c["on_surface_variant"])
        )

    return ft.Container(
        content=ft.Row(controls=left_controls, spacing=8),
        padding=ft.Padding(left=34, right=14, top=8, bottom=8),
        border_radius=8,
        bgcolor=bg,
        ink=True,
        on_click=lambda _: on_click(child["id"]),
    )


def _build_menu(page, state, on_navigate, on_toggle_group) -> ft.Control:
    c = Colors.from_page(page)
    selected = state.download_category
    expanded = state.download_expanded

    controls = []
    for item in MENU_ITEMS:
        if item["type"] == "leaf":
            controls.append(
                _build_leaf_item(c, item, selected == item["id"], on_navigate)
            )
        else:
            is_expanded = item["id"] in expanded
            controls.append(
                _build_group_header(c, item, is_expanded, on_toggle_group)
            )
            if is_expanded:
                for child in item["children"]:
                    controls.append(
                        _build_child_item(c, child, selected == child["id"], on_navigate)
                    )

    return ft.Container(
        content=ft.Column(controls=controls, spacing=2, scroll=ft.ScrollMode.AUTO, expand=True),
        padding=ft.Padding(8, 8, 8, 8),
        bgcolor=c["surface"],
        border_radius=12,
        border=ft.Border.all(1, c["outline_variant"]),
        width=220,
    )


# ===== 版本卡片构建 =====

def _build_version_card(page, version, installed=False, is_jar=False) -> ft.Control:
    c = Colors.from_page(page)

    if installed:
        action_btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=c["primary"], size=16),
                    ft.Text("已安装", size=13, color=c["primary"], weight=ft.FontWeight.W_500),
                ],
                spacing=6,
            ),
            padding=ft.Padding(left=16, right=16, top=8, bottom=8),
            border_radius=8,
            border=ft.Border.all(1, c["outline"]),
        )
    else:
        btn_label = "下载 .jar" if is_jar else "安装"
        action_btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.DOWNLOAD, color="#FFFFFF", size=16),
                    ft.Text(btn_label, size=13, color="#FFFFFF", weight=ft.FontWeight.W_500),
                ],
                spacing=6,
            ),
            padding=ft.Padding(left=16, right=16, top=8, bottom=8),
            border_radius=8,
            gradient=ft.LinearGradient(
                begin=ft.Alignment.CENTER_LEFT,
                end=ft.Alignment.CENTER_RIGHT,
                colors=[c["gradient_start"], c["gradient_end"]],
            ),
            ink=True,
        )

    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.BLOCK, color="#FFFFFF", size=22),
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
                        ft.Text(version, size=15, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                        ft.Text("已安装" if installed else "未安装", size=11, color=c["on_surface_variant"]),
                    ],
                    spacing=2,
                    expand=True,
                ),
                action_btn,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=14,
        ),
        padding=ft.Padding(16, 14, 16, 14),
        bgcolor=c["surface"],
        border_radius=12,
        border=ft.Border.all(1, c["outline_variant"]),
    )


def _build_version_section(page, category, versions, is_jar=False) -> ft.Control:
    c = Colors.from_page(page)

    cards = [
        _build_version_card(page, v, installed=inst, is_jar=is_jar)
        for v, inst in versions
    ]

    return ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Icon(category["icon"], color=c["primary"], size=18),
                    ft.Text(category["label"], size=15, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                    ft.Container(
                        content=ft.Text(str(len(versions)), size=11, color=c["on_surface_variant"]),
                        padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                        border_radius=6,
                        bgcolor=c["surface_variant"],
                    ),
                ],
                spacing=8,
            ),
            ft.Column(controls=cards, spacing=6),
        ],
        spacing=8,
    )


def _build_version_content(page, is_jar=False) -> ft.Control:
    c = Colors.from_page(page)

    sections = []
    for cat in VERSION_CATEGORIES:
        versions = ALL_VERSIONS.get(cat["id"], [])
        if versions:
            sections.append(_build_version_section(page, cat, versions, is_jar=is_jar))

    title = "下载 Minecraft 版本文件 (.jar)" if is_jar else "安装 Minecraft 游戏版本"
    subtitle = "选择需要的版本进行下载" if is_jar else "选择需要安装的游戏版本"

    header = ft.Column(
        controls=[
            ft.Text(title, size=18, weight=ft.FontWeight.W_600, color=c["on_surface"]),
            ft.Text(subtitle, size=13, color=c["on_surface_variant"]),
        ],
        spacing=2,
    )

    return ft.Column(
        controls=[header, ft.Container(height=4), *sections],
        spacing=16,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _build_placeholder_content(page, category_id) -> ft.Control:
    c = Colors.from_page(page)

    label = category_id
    icon = ft.Icons.DOWNLOAD
    desc = "该功能正在开发中，敬请期待"
    for item in MENU_ITEMS:
        if item.get("children"):
            for child in item["children"]:
                if child["id"] == category_id:
                    label = child["label"]
                    icon = child.get("icon", ft.Icons.DOWNLOAD)
                    break

    return ft.Column(
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(icon, color="#FFFFFF", size=48),
                            width=80,
                            height=80,
                            border_radius=20,
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment.TOP_LEFT,
                                end=ft.Alignment.BOTTOM_RIGHT,
                                colors=[c["gradient_start"], c["gradient_end"]],
                            ),
                            alignment=ft.Alignment.CENTER,
                        ),
                        ft.Text(label, size=20, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                        ft.Text(desc, size=13, color=c["on_surface_variant"]),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                padding=ft.Padding(40, 40, 40, 40),
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


# ===== 主视图 =====

def build_download_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_user_click=None,
    on_download_navigate=None,
    on_toggle_group=None,
    **kwargs,
) -> list:
    """构建下载页视图。"""
    category = state.download_category

    nav_cb = on_download_navigate or (lambda _: None)
    toggle_cb = on_toggle_group or (lambda _: None)

    menu = _build_menu(page, state, nav_cb, toggle_cb)

    if category == "mc_install":
        content = _build_version_content(page, is_jar=False)
    elif category == "installer_mc_jar":
        content = _build_version_content(page, is_jar=True)
    else:
        content = _build_placeholder_content(page, category)

    layout = ft.Column(
        controls=[
            build_topbar(
                page,
                "下载",
                state.username,
                state.logged_in,
                on_toggle_theme,
                on_user_click,
            ),
            ft.Container(height=4),
            ft.Row(
                controls=[
                    menu,
                    ft.Container(
                        content=content,
                        expand=True,
                        padding=ft.Padding(left=16, right=0, top=0, bottom=0),
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True,
            ),
        ],
        spacing=8,
        expand=True,
    )

    return [layout]
