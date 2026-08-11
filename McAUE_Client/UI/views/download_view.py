"""下载页视图 - 多级菜单下载管理。

菜单结构：
  Minecraft（安装版本）→ 版本列表（正式版/预览版/远古版/愚人节版）
  社区资源（折叠框）→ 模组/整合包/数据包/资源包/光影包
  安装包（折叠框）→ Minecraft(.jar)/OptiFine/Forge/NeoForge/Fabric/Legacy Fabric/Quilt/LiteLoader

下载按钮已接入 downloader 接口，版本列表优先使用 downloader.get_version_list()。
"""

import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar
from components.animation import SmoothScroll
from core.downloader import downloader


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


def _build_menu(page, state, on_content_change) -> ft.Control:
    c = Colors.from_page(page)
    menu_column = ft.Column(controls=[], spacing=2)
    menu_scroll = SmoothScroll(page=page, column=menu_column, expand=True)
    group_refs = {}

    def toggle_group(group_id):
        if group_id in state.download_expanded:
            state.download_expanded.remove(group_id)
        else:
            state.download_expanded.append(group_id)
        refs = group_refs.get(group_id)
        if not refs:
            return
        is_exp = group_id in state.download_expanded
        refs["arrow"].rotate = 1.5708 if is_exp else 0
        item = next(i for i in MENU_ITEMS if i["id"] == group_id)
        if is_exp:
            new_content = ft.Column(
                controls=[
                    _build_child_item(c, child, state.download_category == child["id"], handle_select)
                    for child in item["children"]
                ],
                spacing=2,
            )
        else:
            new_content = ft.Container()
        refs["switcher"].content = new_content
        try:
            refs["arrow"].update()
            refs["switcher"].update()
        except Exception:
            pass

    def handle_select(category_id):
        state.download_category = category_id
        rebuild()
        try:
            menu_column.update()
        except Exception:
            pass
        on_content_change(category_id)

    def rebuild():
        selected = state.download_category
        group_refs.clear()
        controls = []
        for item in MENU_ITEMS:
            if item["type"] == "leaf":
                controls.append(
                    _build_leaf_item(c, item, selected == item["id"], handle_select)
                )
            else:
                is_exp = item["id"] in state.download_expanded
                arrow = ft.Container(
                    content=ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        color=c["on_surface_variant"],
                        size=18,
                    ),
                    rotate=1.5708 if is_exp else 0,
                    animate=ft.Animation(duration=200, curve=ft.AnimationCurve.EASE_IN_OUT),
                )
                header = ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(item["icon"], color=c["on_surface_variant"], size=20),
                            ft.Text(item["label"], size=14, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                            ft.Container(expand=True),
                            arrow,
                        ],
                        spacing=10,
                    ),
                    padding=ft.Padding(left=14, right=14, top=10, bottom=10),
                    border_radius=8,
                    ink=True,
                    on_click=lambda _, gid=item["id"]: toggle_group(gid),
                )
                if is_exp:
                    children_content = ft.Column(
                        controls=[
                            _build_child_item(c, child, selected == child["id"], handle_select)
                            for child in item["children"]
                        ],
                        spacing=2,
                    )
                else:
                    children_content = ft.Container()
                switcher = ft.AnimatedSwitcher(
                    content=children_content,
                    transition=ft.AnimatedSwitcherTransition.FADE,
                    duration=200,
                    reverse_duration=150,
                )
                group_refs[item["id"]] = {"switcher": switcher, "arrow": arrow}
                controls.append(header)
                controls.append(switcher)
        menu_column.controls = controls

    rebuild()

    return ft.Container(
        content=menu_scroll,
        padding=ft.Padding(8, 8, 8, 8),
        bgcolor=c["surface"],
        border_radius=12,
        border=ft.Border.all(1, c["outline_variant"]),
        width=220,
    )


# ===== 版本卡片构建 =====

def _show_download_dialog(page, version, is_jar=False):
    """显示下载进度对话框。"""
    c = Colors.from_page(page)
    progress = ft.ProgressBar(width=300, color=c["primary"], bgcolor=c["surface_variant"])
    status = ft.Text(f"正在下载 {version}...", size=13, color=c["on_surface_variant"])
    detail = ft.Text("", size=11, color=c["on_surface_variant"])

    def on_progress(ver, pct, downloaded, total):
        progress.value = pct / 100 if total > 0 else 0
        if total > 0:
            detail.value = f"{downloaded // 1024 // 1024} MB / {total // 1024 // 1024} MB"
        try:
            progress.update()
            detail.update()
        except Exception:
            pass

    def on_complete(result):
        status.value = result.message
        try:
            status.update()
        except Exception:
            pass

    dialog = ft.AlertDialog(
        title=ft.Text(f"{'下载' if is_jar else '安装'} Minecraft {version}", size=16),
        content=ft.Column(
            controls=[
                ft.Row([ft.Icon(ft.Icons.DOWNLOAD, color=c["primary"], size=24), status], spacing=8),
                progress,
                detail,
            ],
            spacing=8,
            tight=True,
        ),
        actions=[
            ft.TextButton("关闭", on_click=lambda e: page.pop_dialog()),
        ],
    )
    page.show_dialog(dialog)

    downloader.set_callbacks(on_progress=on_progress, on_complete=on_complete)
    if is_jar:
        downloader.download_jar(version)
    else:
        downloader.install_version(version)


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
            on_click=lambda e, v=version, jar=is_jar: _show_download_dialog(page, v, jar),
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

    api_versions = downloader.get_version_list()
    installed_versions = set(downloader.get_installed_versions())

    if api_versions:
        version_map = {"release": [], "snapshot": [], "old": [], "fools": []}
        for v in api_versions:
            vtype = v.type if v.type in version_map else "release"
            version_map[vtype].append((v.id, v.id in installed_versions))
        sections = []
        for cat in VERSION_CATEGORIES:
            versions = version_map.get(cat["id"], [])
            if versions:
                sections.append(_build_version_section(page, cat, versions, is_jar=is_jar))
    else:
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

    return SmoothScroll(
        page=page,
        controls=[header, ft.Container(height=4), *sections],
        spacing=16,
        expand=True,
    )


COMMUNITY_META = {
    "community_mods": {"label": "模组", "icon": ft.Icons.EXTENSION, "placeholder": "搜索模组..."},
    "community_modpacks": {"label": "整合包", "icon": ft.Icons.INVENTORY_2, "placeholder": "搜索整合包..."},
    "community_datapacks": {"label": "数据包", "icon": ft.Icons.STORAGE, "placeholder": "搜索数据包..."},
    "community_resourcepacks": {"label": "资源包", "icon": ft.Icons.IMAGE, "placeholder": "搜索资源包..."},
    "community_shaders": {"label": "光影包", "icon": ft.Icons.WB_SUNNY, "placeholder": "搜索光影包..."},
}

COMMUNITY_SAMPLE_DATA = [
    {"name": "示例项目 A", "author": "DeveloperA", "downloads": "1.2M", "desc": "这是一个示例项目，实际数据需要社区资源 API 接口实现后获取。", "tags": ["1.21", "流行"]},
    {"name": "示例项目 B", "author": "DeveloperB", "downloads": "856K", "desc": "示例项目 B，展示社区资源卡片 UI 布局。", "tags": ["1.20", "推荐"]},
    {"name": "示例项目 C", "author": "DeveloperC", "downloads": "423K", "desc": "示例项目 C，实际使用时将通过 API 返回真实数据。", "tags": ["1.19"]},
    {"name": "示例项目 D", "author": "DeveloperD", "downloads": "98K", "desc": "示例项目 D，用于演示搜索和筛选功能。", "tags": ["1.16.5"]},
]

INSTALLER_META = {
    "installer_optifine": {"label": "OptiFine", "icon": ft.Icons.VISIBILITY, "desc": "优化模组，提供更好的帧率和高清材质支持", "versions": ["OptiFine 1.21.4 HD U I7", "OptiFine 1.20.6 HD U I3", "OptiFine 1.16.5 HD U G8"]},
    "installer_forge": {"label": "Forge", "icon": ft.Icons.BUILD, "desc": "最经典的 Minecraft 模组加载器", "versions": ["47.3.0 (1.20.1)", "40.2.9 (1.18.2)", "36.2.42 (1.16.5)"]},
    "installer_neoforge": {"label": "NeoForge", "icon": ft.Icons.BUILD_CIRCLE, "desc": "Forge 的社区分支，现代化模组加载器", "versions": ["21.4.47-beta (1.21.4)", "20.6.125-beta (1.20.6)", "20.4.237 (1.20.4)"]},
    "installer_fabric": {"label": "Fabric", "icon": ft.Icons.TEXTURE, "desc": "轻量级模组加载器，更新速度快", "versions": ["0.16.9 (1.21.4)", "0.15.11 (1.20.6)", "0.14.24 (1.16.5)"]},
    "installer_legacy_fabric": {"label": "Legacy Fabric", "icon": ft.Icons.TEXTURE_OUTLINED, "desc": "支持旧版本的 Fabric 分支", "versions": ["0.16.9 (1.8.9)", "0.16.9 (1.7.10)", "0.16.9 (b1.7.3)"]},
    "installer_quilt": {"label": "Quilt", "icon": ft.Icons.GRID_VIEW, "desc": "Fabric 的社区分支，兼容 Fabric 模组", "versions": ["0.27.1-beta.1 (1.21.4)", "0.26.1-beta.1 (1.20.6)", "0.24.0-beta.1 (1.20.1)"]},
    "installer_liteloader": {"label": "LiteLoader", "icon": ft.Icons.EGG, "desc": "轻量级模组加载器（已停止维护）", "versions": ["1.12.2-SNAPSHOT", "1.11.2-SNAPSHOT", "1.10.2-SNAPSHOT"]},
}


def _build_community_content(page, category_id) -> ft.Control:
    """构建社区资源浏览UI（搜索、筛选、卡片列表）。"""
    c = Colors.from_page(page)
    meta = COMMUNITY_META.get(category_id, {"label": "资源", "icon": ft.Icons.DOWNLOAD, "placeholder": "搜索..."})

    search_field = ft.TextField(
        hint_text=meta["placeholder"],
        prefix_icon=ft.Icons.SEARCH,
        width=280,
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        text_size=13,
        content_padding=ft.Padding(left=12, right=12, top=8, bottom=8),
    )

    version_filter = ft.Dropdown(
        label="游戏版本",
        width=160,
        text_size=13,
        label_style=ft.TextStyle(size=12),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        options=[
            ft.DropdownOption("all", text="全部版本"),
            ft.DropdownOption("1.21", text="1.21"),
            ft.DropdownOption("1.20", text="1.20"),
            ft.DropdownOption("1.19", text="1.19"),
            ft.DropdownOption("1.16.5", text="1.16.5"),
        ],
        value="all",
    )

    sort_filter = ft.Dropdown(
        label="排序",
        width=140,
        text_size=13,
        label_style=ft.TextStyle(size=12),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        options=[
            ft.DropdownOption("popular", text="热门"),
            ft.DropdownOption("newest", text="最新"),
            ft.DropdownOption("downloads", text="下载量"),
        ],
        value="popular",
    )

    def _show_resource_dialog(e, item):
        """显示资源详情对话框。"""
        dialog = ft.AlertDialog(
            title=ft.Text(item["name"], size=16),
            content=ft.Column(
                controls=[
                    ft.Text(f"作者：{item['author']}", size=13, color=c["on_surface_variant"]),
                    ft.Text(f"下载量：{item['downloads']}", size=13, color=c["on_surface_variant"]),
                    ft.Container(height=4),
                    ft.Text(item["desc"], size=13, color=c["on_surface"]),
                    ft.Container(height=8),
                    ft.Text("实际下载功能需要社区资源 API 接口实现。", size=11, color=c["on_surface_variant"]),
                ],
                spacing=4,
                tight=True,
            ),
            actions=[
                ft.TextButton("关闭", on_click=lambda e: page.pop_dialog()),
                ft.FilledButton("下载", on_click=lambda e: page.pop_dialog()),
            ],
        )
        page.show_dialog(dialog)

    cards = []
    for item in COMMUNITY_SAMPLE_DATA:
        tag_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(tag, size=10, color=c["primary"]),
                    padding=ft.Padding(left=6, right=6, top=2, bottom=2),
                    border_radius=4,
                    bgcolor=c["primary_container"],
                )
                for tag in item["tags"]
            ],
            spacing=4,
        )
        cards.append(
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(meta["icon"], color="#FFFFFF", size=24),
                            width=48,
                            height=48,
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
                                ft.Text(item["name"], size=14, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                                ft.Text(item["author"], size=11, color=c["on_surface_variant"]),
                                tag_row,
                            ],
                            spacing=3,
                            expand=True,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(item["downloads"], size=13, weight=ft.FontWeight.W_600, color=c["primary"]),
                                ft.Text("下载", size=10, color=c["on_surface_variant"]),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=0,
                        ),
                        ft.Container(
                            content=ft.Icon(ft.Icons.DOWNLOAD, color="#FFFFFF", size=18),
                            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
                            border_radius=8,
                            bgcolor=c["primary"],
                            ink=True,
                            on_click=lambda e, it=item: _show_resource_dialog(e, it),
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=12,
                ),
                padding=ft.Padding(14, 12, 14, 12),
                bgcolor=c["surface"],
                border_radius=10,
                border=ft.Border.all(1, c["outline_variant"]),
            )
        )

    return SmoothScroll(
        page=page,
        controls=[
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(meta["icon"], color=c["primary"], size=22),
                            ft.Text(meta["label"], size=18, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                        ],
                        spacing=8,
                    ),
                    ft.Text("浏览和下载社区资源（当前为示例数据）", size=13, color=c["on_surface_variant"]),
                ],
                spacing=2,
            ),
            ft.Container(height=4),
            ft.Row(
                controls=[search_field, version_filter, sort_filter],
                spacing=10,
            ),
            ft.Container(height=2),
            *cards,
            ft.Container(height=4),
            ft.Text(
                "社区资源数据需要接入 API（如 CurseForge / Modrinth），当前显示示例数据。",
                size=11,
                color=c["on_surface_variant"],
            ),
        ],
        spacing=8,
        expand=True,
    )


def _build_installer_content(page, category_id) -> ft.Control:
    """构建安装包下载UI。"""
    c = Colors.from_page(page)
    meta = INSTALLER_META.get(category_id)
    if not meta:
        return _build_placeholder_content(page, category_id)

    version_dropdown = ft.Dropdown(
        label="选择版本",
        width=320,
        text_size=13,
        label_style=ft.TextStyle(size=13),
        border_color=c["outline_variant"],
        focused_border_color=c["primary"],
        options=[ft.DropdownOption(v, text=v) for v in meta["versions"]],
        value=meta["versions"][0] if meta["versions"] else None,
    )

    def _show_installer_dialog(e):
        ver = version_dropdown.value or "未知版本"
        dialog = ft.AlertDialog(
            title=ft.Text(f"下载 {meta['label']}", size=16),
            content=ft.Column(
                controls=[
                    ft.Text(f"版本：{ver}", size=13, color=c["on_surface"]),
                    ft.Text(meta["desc"], size=13, color=c["on_surface_variant"]),
                    ft.Container(height=8),
                    ft.Text("实际下载和安装功能需要加载器安装模块实现。", size=11, color=c["on_surface_variant"]),
                ],
                spacing=4,
                tight=True,
            ),
            actions=[
                ft.TextButton("关闭", on_click=lambda e: page.pop_dialog()),
            ],
        )
        page.show_dialog(dialog)

    download_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.DOWNLOAD, color="#FFFFFF", size=18),
                ft.Text("下载安装", size=14, color="#FFFFFF", weight=ft.FontWeight.W_500),
            ],
            spacing=8,
        ),
        padding=ft.Padding(left=24, right=24, top=10, bottom=10),
        border_radius=10,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=[c["gradient_start"], c["gradient_end"]],
        ),
        ink=True,
        on_click=_show_installer_dialog,
    )

    info_cards = [
        ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=c["on_surface_variant"], size=16),
                    ft.Text("安装后可在启动页的版本设置中选择对应加载器", size=12, color=c["on_surface_variant"]),
                ],
                spacing=6,
            ),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=c["surface"],
            border_radius=8,
            border=ft.Border.all(1, c["outline_variant"]),
        ),
        ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, color=c["on_surface_variant"], size=16),
                    ft.Text("建议先安装对应版本的 Minecraft 再安装加载器", size=12, color=c["on_surface_variant"]),
                ],
                spacing=6,
            ),
            padding=ft.Padding(12, 10, 12, 10),
            bgcolor=c["surface"],
            border_radius=8,
            border=ft.Border.all(1, c["outline_variant"]),
        ),
    ]

    return SmoothScroll(
        page=page,
        controls=[
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(meta["icon"], color="#FFFFFF", size=28),
                        width=56,
                        height=56,
                        border_radius=14,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment.TOP_LEFT,
                            end=ft.Alignment.BOTTOM_RIGHT,
                            colors=[c["gradient_start"], c["gradient_end"]],
                        ),
                        alignment=ft.Alignment.CENTER,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(meta["label"], size=18, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                            ft.Text(meta["desc"], size=13, color=c["on_surface_variant"]),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=14,
            ),
            ft.Container(height=4),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("选择版本", size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                        version_dropdown,
                        ft.Container(height=4),
                        download_btn,
                    ],
                    spacing=10,
                ),
                padding=ft.Padding(16, 16, 16, 16),
                bgcolor=c["surface"],
                border_radius=12,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
            ft.Container(height=2),
            *info_cards,
        ],
        spacing=8,
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

    return SmoothScroll(
        page=page,
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
        expand=True,
    )


# ===== 主视图 =====

def _build_category_content(page, category) -> ft.Control:
    """根据分类构建对应的内容区。"""
    if category == "mc_install":
        return _build_version_content(page, is_jar=False)
    elif category == "installer_mc_jar":
        return _build_version_content(page, is_jar=True)
    elif category in COMMUNITY_META:
        return _build_community_content(page, category)
    elif category in INSTALLER_META:
        return _build_installer_content(page, category)
    else:
        return _build_placeholder_content(page, category)


def build_download_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_user_click=None,
    **kwargs,
) -> list:
    """构建下载页视图。"""

    content_switcher = ft.AnimatedSwitcher(
        content=_build_category_content(page, state.download_category),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=200,
        reverse_duration=150,
    )

    def on_content_change(category_id):
        content_switcher.content = _build_category_content(page, category_id)
        try:
            content_switcher.update()
        except Exception:
            pass

    menu = _build_menu(page, state, on_content_change)

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
                        content=content_switcher,
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
