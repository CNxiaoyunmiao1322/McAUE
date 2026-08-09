"""设置视图 - 二级菜单导航，含启动/Java/管理/联机/个性化/语言/杂项/软件更新。"""

import asyncio
import psutil
import flet as ft

from theme.colors import Colors
from components.topbar import build_topbar


# ===== 二级菜单配置 =====

SETTINGS_TABS = [
    ("launch", "启动", ft.Icons.ROCKET_LAUNCH_OUTLINED),
    ("java", "Java", ft.Icons.COFFEE_OUTLINED),
    ("manage", "管理", ft.Icons.FOLDER_OUTLINED),
    ("multiplayer", "联机", ft.Icons.WIFI_OUTLINED),
    ("personalize", "个性化", ft.Icons.PALETTE_OUTLINED),
    ("language", "语言", ft.Icons.LANGUAGE_OUTLINED),
    ("misc", "杂项", ft.Icons.TUNE_OUTLINED),
    ("update", "软件更新", ft.Icons.SYSTEM_UPDATE_ALT_OUTLINED),
]


# ===== 辅助函数 =====

def _get_memory_info():
    mem = psutil.virtual_memory()
    total_gb = mem.total / (1024**3)
    used_gb = mem.used / (1024**3)
    return round(total_gb, 1), round(used_gb, 1)


def _build_section_title(page: ft.Page, title: str, icon: str) -> ft.Control:
    c = Colors.from_page(page)
    return ft.Row(
        controls=[
            ft.Icon(icon, color=c["primary"], size=20),
            ft.Text(title, size=16, weight=ft.FontWeight.W_600, color=c["on_surface"]),
        ],
        spacing=8,
    )


def _build_setting_row(page: ft.Page, label: str, subtitle: str, control: ft.Control) -> ft.Control:
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


def _build_memory_panel(page: ft.Page, total_mem: float, used_mem: float) -> ft.Control:
    """构建内存分配面板 - 自动/手动分配切换 + 系统内存可视化。"""
    c = Colors.from_page(page)
    avail = total_mem - used_mem
    auto_alloc = round(min(max(avail * 0.5, 1), 4), 1)
    default_manual = min(4, max(1, int(avail)))
    pct = used_mem / total_mem if total_mem > 0 else 0
    mem_state = {"auto": True, "value": default_manual}

    alloc_text = ft.Text(
        f"{auto_alloc} GB",
        size=18, weight=ft.FontWeight.BOLD, color=c["primary"],
    )

    sys_mem_text = ft.Text(
        f"{used_mem} / {total_mem} GB",
        size=14, weight=ft.FontWeight.W_600, color=c["on_surface"],
    )

    def make_mode_btn(label, is_auto):
        icon = ft.Icon(
            ft.Icons.RADIO_BUTTON_CHECKED if mem_state["auto"] == is_auto else ft.Icons.RADIO_BUTTON_UNCHECKED,
            color=c["primary"] if mem_state["auto"] == is_auto else c["on_surface_variant"],
            size=18,
        )
        text = ft.Text(label, size=13, color=c["on_surface"])
        return ft.Container(
            content=ft.Row([icon, text], spacing=6),
            ink=True,
            on_click=lambda _: select_mode(is_auto),
        ), icon

    auto_btn, auto_icon = make_mode_btn("自动分配", True)
    manual_btn, manual_icon = make_mode_btn("手动分配", False)

    slider = ft.Slider(
        min=1, max=int(total_mem), divisions=max(int(total_mem) - 1, 1),
        value=default_manual, label="{value} GB",
        active_color=c["primary"], width=300,
        visible=False,
    )

    progress = ft.ProgressBar(
        value=pct,
        color=c["primary"],
        bgcolor=c["surface_variant"],
        height=8,
    )

    def select_mode(is_auto):
        mem_state["auto"] = is_auto
        auto_icon.icon = ft.Icons.RADIO_BUTTON_CHECKED if is_auto else ft.Icons.RADIO_BUTTON_UNCHECKED
        auto_icon.color = c["primary"] if is_auto else c["on_surface_variant"]
        manual_icon.icon = ft.Icons.RADIO_BUTTON_CHECKED if not is_auto else ft.Icons.RADIO_BUTTON_UNCHECKED
        manual_icon.color = c["primary"] if not is_auto else c["on_surface_variant"]
        slider.visible = not is_auto
        alloc_text.value = f"{auto_alloc if is_auto else mem_state['value']} GB"
        page.update()

    def on_slider_change(e):
        mem_state["value"] = int(slider.value)
        alloc_text.value = f"{mem_state['value']} GB"
        page.update()

    slider.on_change = on_slider_change

    # ===== 实时内存轮询 =====
    if hasattr(page, "_mem_stop") and page._mem_stop:
        page._mem_stop["active"] = False
    stop = {"active": True}
    page._mem_stop = stop

    async def _poll_memory():
        while stop["active"]:
            await asyncio.sleep(1)
            if not stop["active"]:
                break
            mem = psutil.virtual_memory()
            total = round(mem.total / (1024**3), 1)
            used = round(mem.used / (1024**3), 1)
            pct_new = used / total if total > 0 else 0
            progress.value = pct_new
            sys_mem_text.value = f"{used} / {total} GB"
            if mem_state["auto"]:
                avail_new = total - used
                auto_val = round(min(max(avail_new * 0.5, 1), 4), 1)
                alloc_text.value = f"{auto_val} GB"
            try:
                progress.update()
                sys_mem_text.update()
                if mem_state["auto"]:
                    alloc_text.update()
            except Exception:
                stop["active"] = False
                break

    page.run_task(_poll_memory)

    return ft.Container(
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.MEMORY, color=c["primary"], size=20),
                        ft.Text("内存分配", size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                    ],
                    spacing=8,
                ),
                ft.Row([auto_btn, ft.Container(width=20), manual_btn]),
                progress,
                ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text("系统内存", size=11, color=c["on_surface_variant"]),
                                sys_mem_text,
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        ft.Column(
                            controls=[
                                ft.Text("游戏分配", size=11, color=c["on_surface_variant"]),
                                alloc_text,
                            ],
                            spacing=2,
                        ),
                    ],
                ),
                slider,
            ],
            spacing=14,
        ),
        padding=ft.Padding(16, 16, 16, 16),
        bgcolor=c["surface"],
        border_radius=10,
        border=ft.Border.all(1, c["outline_variant"]),
    )


def _make_dropdown(page, value, options, width=160):
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


def _make_switch(page, value=True):
    c = Colors.from_page(page)
    return ft.Switch(value=value, active_color=c["primary"])


def _make_text_field(page, label, hint, icon=ft.Icons.FOLDER_OUTLINED):
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


def _make_button(page, text, icon, bgcolor_key="primary"):
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
    )


# ===== 各子页面构建 =====

def _build_launch_page(page, total_mem, used_mem):
    c = Colors.from_page(page)

    # ===== 启动选项 =====
    instance_isolation = _make_dropdown(page, "all", [
        ft.dropdown.Option("off", "关闭"),
        ft.dropdown.Option("mods", "隔离可安装模组的实例"),
        ft.dropdown.Option("non_release", "隔离非正式版"),
        ft.dropdown.Option("mods_non_release", "隔离可安装模组的实例与非正式版"),
        ft.dropdown.Option("all", "隔离所有实例"),
    ], width=280)

    window_title = _make_text_field(page, "窗口标题", "Minecraft 1.21.4", ft.Icons.TITLE)

    custom_info = _make_text_field(page, "自定义信息", "自定义 F3 信息", ft.Icons.INFO_OUTLINE)

    launcher_visibility = _make_dropdown(page, "keep", [
        ft.dropdown.Option("close", "游戏启动后立即关闭"),
        ft.dropdown.Option("hide_close", "游戏启动后隐藏，退出后关闭"),
        ft.dropdown.Option("hide_reopen", "游戏启动后隐藏，退出后重开"),
        ft.dropdown.Option("minimize", "游戏启动后最小化"),
        ft.dropdown.Option("keep", "游戏启动后仍保持不变"),
    ], width=280)

    process_priority = _make_dropdown(page, "normal", [
        ft.dropdown.Option("realtime", "实时"),
        ft.dropdown.Option("very_high", "极高"),
        ft.dropdown.Option("high", "高"),
        ft.dropdown.Option("normal", "中（平衡）"),
        ft.dropdown.Option("low", "低"),
    ], width=280)

    # 窗口大小：下拉框 + 自定义尺寸输入
    window_size_dd = _make_dropdown(page, "default", [
        ft.dropdown.Option("fullscreen", "全屏"),
        ft.dropdown.Option("default", "默认"),
        ft.dropdown.Option("launcher", "与启动器尺寸一致"),
        ft.dropdown.Option("custom", "自定义尺寸"),
        ft.dropdown.Option("maximize", "最大化"),
    ], width=280)

    custom_w = ft.TextField(
        hint_text="宽", width=70, text_size=13,
        border_color=c["outline"], color=c["on_surface"],
        bgcolor=c["surface_variant"], filled=True,
    )
    custom_h = ft.TextField(
        hint_text="高", width=70, text_size=13,
        border_color=c["outline"], color=c["on_surface"],
        bgcolor=c["surface_variant"], filled=True,
    )
    custom_size_row = ft.Row(
        controls=[
            custom_w,
            ft.Text("×", size=13, color=c["on_surface_variant"]),
            custom_h,
        ],
        spacing=6,
        visible=False,
    )

    def on_window_size_change(e):
        custom_size_row.visible = e.control.value == "custom"
        try:
            custom_size_row.update()
        except Exception:
            pass

    window_size_dd.on_select = on_window_size_change

    window_size_control = ft.Column(
        controls=[window_size_dd, custom_size_row],
        spacing=6,
        horizontal_alignment=ft.CrossAxisAlignment.END,
    )

    auth_method = _make_dropdown(page, "device", [
        ft.dropdown.Option("device", "设备代码流"),
        ft.dropdown.Option("pkce", "授权码流程 (PKCE)"),
    ], width=280)

    ip_protocol = _make_dropdown(page, "default", [
        ft.dropdown.Option("ipv4", "IPv4 优先"),
        ft.dropdown.Option("default", "Java 默认"),
        ft.dropdown.Option("ipv6", "IPv6 优先"),
    ], width=280)

    # ===== 高级启动选项 =====
    renderer = _make_dropdown(page, "default", [
        ft.dropdown.Option("default", "游戏默认"),
        ft.dropdown.Option("llvmpipe", "软渲染 (llvmpipe)"),
        ft.dropdown.Option("d3d12", "DirectX12 (d3d12)"),
        ft.dropdown.Option("zink", "Vulkan (zink)"),
    ], width=280)

    jvm_args_head = _make_text_field(page, "JVM 参数头部", "-Djava.awt.headless=true", ft.Icons.TERMINAL)
    game_args_tail = _make_text_field(page, "游戏参数尾部", "--width 1280 --height 720", ft.Icons.TERMINAL)
    pre_exec_cmd = _make_text_field(page, "启动前执行命令", "输入命令...", ft.Icons.TERMINAL)

    return ft.Column(
        controls=[
            _build_section_title(page, "启动", ft.Icons.ROCKET_LAUNCH_OUTLINED),

            ft.Text("启动选项", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            _build_setting_row(page, "默认实例隔离", "选择实例隔离策略", instance_isolation),
            _build_setting_row(page, "游戏窗口标题", "自定义游戏窗口显示标题", window_title),
            _build_setting_row(page, "自定义信息", "自定义 F3 显示信息", custom_info),
            _build_setting_row(page, "启动器可见性", "游戏运行时启动器的行为", launcher_visibility),
            _build_setting_row(page, "进程优先级", "选择游戏进程优先级", process_priority),
            _build_setting_row(page, "窗口大小", "游戏窗口大小模式", window_size_control),
            _build_setting_row(page, "正版验证方式", "Microsoft 账户验证流程", auth_method),
            _build_setting_row(page, "IP 协议偏好", "网络连接 IP 协议偏好", ip_protocol),

            ft.Text("游戏内存", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            _build_memory_panel(page, total_mem, used_mem),

            ft.Text("高级启动选项", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            _build_setting_row(page, "渲染器", "游戏渲染后端", renderer),
            _build_setting_row(page, "JVM 参数头部", "附加在 JVM 启动参数前部", jvm_args_head),
            _build_setting_row(page, "游戏参数尾部", "传递给游戏的额外参数", game_args_tail),
            _build_setting_row(page, "启动前执行命令", "游戏启动前执行的系统命令", pre_exec_cmd),
            _build_setting_row(page, "禁用 Java Launch Wrapper", "", _make_switch(page, False)),
            _build_setting_row(page, "禁用 LegacyFix", "", _make_switch(page, False)),
            _build_setting_row(page, "要求 Java 使用高性能显卡", "", _make_switch(page, False)),
            _build_setting_row(page, "使用 java.exe 而不是 javaw.exe", "", _make_switch(page, True)),
            _build_setting_row(page, "禁用 LWJGL Unsafe Agent", "", _make_switch(page, False)),
            _build_setting_row(page, "禁用自动崩溃分析", "", _make_switch(page, False)),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _build_java_page(page):
    return ft.Column(
        controls=[
            _build_section_title(page, "Java", ft.Icons.COFFEE_OUTLINED),
            _build_setting_row(page, "Java 路径", "手动添加 Java 运行时", _make_button(page, "添加 Java", ft.Icons.ADD)),
            _build_setting_row(page, "Java 版本", "当前检测到 Java 21.0.5", _make_dropdown(page, "自动选择", [
                ft.dropdown.Option("自动选择"),
                ft.dropdown.Option("Java 21"),
                ft.dropdown.Option("Java 17"),
                ft.dropdown.Option("Java 8"),
            ])),
            _build_setting_row(page, "自动检测", "启动时自动寻找合适的 Java", _make_switch(page, True)),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _build_manage_page(page, state, on_logout):
    c = Colors.from_page(page)

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

    return ft.Column(
        controls=[
            _build_section_title(page, "管理", ft.Icons.FOLDER_OUTLINED),

            # 账户信息
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

            _build_setting_row(page, "游戏目录", "管理游戏安装目录", _make_button(page, "打开目录", ft.Icons.FOLDER_OPEN)),
            _build_setting_row(page, "存档备份", "备份或恢复游戏存档", _make_button(page, "备份", ft.Icons.BACKUP)),
            _build_setting_row(page, "清理垃圾", "清理临时文件和缓存", _make_button(page, "清理", ft.Icons.DELETE_SWEEP)),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _build_multiplayer_page(page):
    c = Colors.from_page(page)
    return ft.Column(
        controls=[
            _build_section_title(page, "联机", ft.Icons.WIFI_OUTLINED),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.CONSTRUCTION, color=c["on_surface_variant"], size=48),
                        ft.Text("正在开发中", size=18, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                        ft.Text("联机功能正在开发中，敬请期待", size=13, color=c["on_surface_variant"]),
                    ],
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(0, 48, 0, 48),
                alignment=ft.Alignment.CENTER,
                expand=True,
            ),
        ],
        spacing=8,
        expand=True,
    )


def _build_personalize_page(page, theme_mode, on_set_theme):
    c = Colors.from_page(page)

    theme_dropdown = _make_dropdown(page, theme_mode, [
        ft.dropdown.Option("light", "白天模式"),
        ft.dropdown.Option("dark", "黑夜模式"),
        ft.dropdown.Option("system", "跟随系统"),
    ])
    theme_dropdown.on_select = lambda e: on_set_theme(e.control.value) if on_set_theme else None

    return ft.Column(
        controls=[
            _build_section_title(page, "个性化", ft.Icons.PALETTE_OUTLINED),
            _build_setting_row(page, "主题模式", "选择白天、黑夜或跟随系统", theme_dropdown),
            _build_setting_row(page, "动画效果", "启用界面过渡动画", _make_switch(page, True)),
            _build_setting_row(page, "自定义背景", "设置启动器背景图片", _make_button(page, "选择图片", ft.Icons.IMAGE)),
            _build_setting_row(page, "透明度", "窗口背景透明度", ft.Slider(min=0, max=100, divisions=20, value=100, label="{value}%", active_color=c["primary"], width=180)),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _build_language_page(page):
    lang_dropdown = _make_dropdown(page, "简体中文", [
        ft.dropdown.Option("简体中文"),
        ft.dropdown.Option("English"),
        ft.dropdown.Option("日本語"),
    ])

    return ft.Column(
        controls=[
            _build_section_title(page, "语言", ft.Icons.LANGUAGE_OUTLINED),
            _build_setting_row(page, "界面语言", "选择启动器界面显示语言", lang_dropdown),
            _build_setting_row(page, "游戏语言", "Minecraft 游戏内语言", _make_dropdown(page, "zh_cn", [
                ft.dropdown.Option("zh_cn", "简体中文"),
                ft.dropdown.Option("en_us", "English (US)"),
                ft.dropdown.Option("ja_jp", "日本語"),
                ft.dropdown.Option("lzh", "文言文"),
            ])),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _build_misc_page(page):
    log_dropdown = _make_dropdown(page, "INFO", [
        ft.dropdown.Option("DEBUG"),
        ft.dropdown.Option("INFO"),
        ft.dropdown.Option("WARNING"),
        ft.dropdown.Option("ERROR"),
    ])

    return ft.Column(
        controls=[
            _build_section_title(page, "杂项", ft.Icons.TUNE_OUTLINED),
            _build_setting_row(page, "调试模式", "显示详细调试信息", _make_switch(page, False)),
            _build_setting_row(page, "日志等级", "控制台日志输出等级", log_dropdown),
            _build_setting_row(page, "自动关闭", "游戏退出后自动关闭启动器", _make_switch(page, True)),
            _build_setting_row(page, "清除缓存", "清除启动器缓存数据", _make_button(page, "清除", ft.Icons.CLEANING_SERVICES)),
            _build_setting_row(page, "打开日志", "查看启动器运行日志", _make_button(page, "打开", ft.Icons.DESCRIPTION)),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def _build_update_page(page):
    c = Colors.from_page(page)

    channel_dropdown = _make_dropdown(page, "stable", [
        ft.dropdown.Option("stable", "正式版"),
        ft.dropdown.Option("beta", "测试版"),
        ft.dropdown.Option("dev", "开发版"),
    ])

    return ft.Column(
        controls=[
            _build_section_title(page, "软件更新", ft.Icons.SYSTEM_UPDATE_ALT_OUTLINED),
            ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE, color=c["primary"], size=28),
                        ft.Column(
                            controls=[
                                ft.Text("当前版本：v1.0.0", size=14, weight=ft.FontWeight.W_600, color=c["on_surface"]),
                                ft.Text("已是最新版本", size=12, color=c["on_surface_variant"]),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        _make_button(page, "检查更新", ft.Icons.REFRESH),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.Padding(16, 16, 16, 16),
                bgcolor=c["surface"],
                border_radius=10,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
            _build_setting_row(page, "更新通道", "选择更新发布通道", channel_dropdown),
            _build_setting_row(page, "自动更新", "有新版本时自动下载更新", _make_switch(page, True)),
        ],
        spacing=8,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


# ===== 主视图 =====

def build_settings_view(
    page: ft.Page,
    state,
    on_navigate=None,
    on_toggle_theme=None,
    on_set_theme=None,
    on_user_click=None,
    on_logout=None,
    theme_mode="dark",
    **kwargs,
) -> list:
    """构建设置视图 - 左侧二级菜单 + 右侧内容区。"""
    c = Colors.from_page(page)
    total_mem, used_mem = _get_memory_info()

    current_tab = {"value": state.settings_tab}

    # 构建侧边栏导航项
    nav_items = []
    nav_icons = {}

    def select_tab(tab_id):
        if current_tab["value"] == "launch" and tab_id != "launch":
            if hasattr(page, "_mem_stop") and page._mem_stop:
                page._mem_stop["active"] = False
                page._mem_stop = None
        current_tab["value"] = tab_id
        state.settings_tab = tab_id
        for tid, icon in nav_icons.items():
            active = tid == tab_id
            icon.color = "#FFFFFF" if active else c["on_surface_variant"]
            try:
                icon.update()
            except Exception:
                pass
        for tid, btn in nav_containers.items():
            active = tid == tab_id
            btn.bgcolor = c["primary"] if active else c["surface_variant"]
            try:
                btn.update()
            except Exception:
                pass
        new_content = _build_tab_content(page, tab_id, state, total_mem, used_mem, theme_mode, on_set_theme, on_logout)
        new_content.key = f"tab_{tab_id}"
        content_switcher.content = new_content
        try:
            content_switcher.update()
        except Exception:
            pass

    nav_containers = {}
    for tab_id, label, icon_name in SETTINGS_TABS:
        active = tab_id == current_tab["value"]
        ic = ft.Icon(icon_name, color="#FFFFFF" if active else c["on_surface_variant"], size=18)
        txt = ft.Text(label, size=13, color="#FFFFFF" if active else c["on_surface"], weight=ft.FontWeight.W_500)
        nav_icons[tab_id] = ic
        btn = ft.Container(
            content=ft.Row([ic, txt], spacing=8),
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            border_radius=8,
            bgcolor=c["primary"] if active else c["surface_variant"],
            ink=True,
            on_click=lambda e, tid=tab_id: select_tab(tid),
        )
        nav_containers[tab_id] = btn
        nav_items.append(btn)

    sidebar = ft.Container(
        content=ft.Column(
            controls=nav_items,
            spacing=4,
        ),
        padding=ft.Padding(8, 8, 8, 8),
        bgcolor=c["surface"],
        border_radius=12,
        width=140,
    )

    _initial_content = _build_tab_content(page, current_tab["value"], state, total_mem, used_mem, theme_mode, on_set_theme, on_logout)
    _initial_content.key = f"tab_{current_tab['value']}"

    content_switcher = ft.AnimatedSwitcher(
        content=_initial_content,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=400,
        reverse_duration=300,
        expand=True,
    )

    body = ft.Row(
        controls=[sidebar, content_switcher],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,
        expand=True,
    )

    content = ft.Column(
        controls=[
            build_topbar(
                page,
                "设置",
                state.username,
                state.logged_in,
                on_toggle_theme,
                on_user_click,
            ),
            ft.Container(height=4),
            body,
        ],
        spacing=8,
        expand=True,
    )

    return [content]


def _build_tab_content(page, tab_id, state, total_mem, used_mem, theme_mode, on_set_theme, on_logout) -> ft.Control:
    """根据当前选中的标签页构建内容。"""
    if tab_id == "launch":
        return _build_launch_page(page, total_mem, used_mem)
    elif tab_id == "java":
        return _build_java_page(page)
    elif tab_id == "manage":
        return _build_manage_page(page, state, on_logout)
    elif tab_id == "multiplayer":
        return _build_multiplayer_page(page)
    elif tab_id == "personalize":
        return _build_personalize_page(page, theme_mode, on_set_theme)
    elif tab_id == "language":
        return _build_language_page(page)
    elif tab_id == "misc":
        return _build_misc_page(page)
    elif tab_id == "update":
        return _build_update_page(page)
    return ft.Container()
