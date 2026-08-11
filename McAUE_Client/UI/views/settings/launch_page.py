"""启动设置页面。"""

import asyncio
import psutil
import flet as ft

from theme.colors import Colors
from components.animation import SmoothScroll
from state.config import config
from ._common import build_section_title, build_setting_row, make_dropdown, make_switch, make_text_field


def _build_memory_panel(page: ft.Page, total_mem: float, used_mem: float) -> ft.Control:
    c = Colors.from_page(page)
    avail = total_mem - used_mem
    auto_alloc = round(min(max(avail * 0.5, 1), 4), 1)
    default_manual = min(4, max(1, int(avail)))
    pct = used_mem / total_mem if total_mem > 0 else 0
    lc = config.get("launch")
    mem_state = {"auto": lc.get("memory_auto", True), "value": lc.get("memory_value", default_manual)}

    alloc_text = ft.Text(
        f"{auto_alloc if mem_state['auto'] else mem_state['value']} GB",
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
        value=mem_state["value"], label="{value} GB",
        active_color=c["primary"], width=300,
        visible=not mem_state["auto"],
    )

    progress = ft.ProgressBar(
        value=pct,
        color=c["primary"],
        bgcolor=c["surface_variant"],
        height=8,
    )

    def select_mode(is_auto):
        mem_state["auto"] = is_auto
        config.set("launch", "memory_auto", is_auto)
        auto_icon.icon = ft.Icons.RADIO_BUTTON_CHECKED if is_auto else ft.Icons.RADIO_BUTTON_UNCHECKED
        auto_icon.color = c["primary"] if is_auto else c["on_surface_variant"]
        manual_icon.icon = ft.Icons.RADIO_BUTTON_CHECKED if not is_auto else ft.Icons.RADIO_BUTTON_UNCHECKED
        manual_icon.color = c["primary"] if not is_auto else c["on_surface_variant"]
        slider.visible = not is_auto
        alloc_text.value = f"{auto_alloc if is_auto else mem_state['value']} GB"
        page.update()

    def on_slider_change(e):
        mem_state["value"] = int(slider.value)
        config.set("launch", "memory_value", mem_state["value"])
        alloc_text.value = f"{mem_state['value']} GB"
        page.update()

    slider.on_change = on_slider_change

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


def build_launch_page(page, total_mem, used_mem):
    c = Colors.from_page(page)
    lc = config.get("launch")

    instance_isolation = make_dropdown(page, lc.get("instance_isolation", "all"), [
        ft.dropdown.Option("off", "关闭"),
        ft.dropdown.Option("mods", "隔离可安装模组的实例"),
        ft.dropdown.Option("non_release", "隔离非正式版"),
        ft.dropdown.Option("mods_non_release", "隔离可安装模组的实例与非正式版"),
        ft.dropdown.Option("all", "隔离所有实例"),
    ], width=280)
    instance_isolation.on_select = lambda e: config.set("launch", "instance_isolation", e.control.value)

    window_title = make_text_field(page, "窗口标题", "Minecraft 1.21.4", ft.Icons.TITLE)
    window_title.value = lc.get("window_title", "")
    window_title.on_blur = lambda e: config.set("launch", "window_title", window_title.value)

    custom_info = make_text_field(page, "自定义信息", "自定义 F3 信息", ft.Icons.INFO_OUTLINE)
    custom_info.value = lc.get("custom_info", "")
    custom_info.on_blur = lambda e: config.set("launch", "custom_info", custom_info.value)

    launcher_visibility = make_dropdown(page, lc.get("launcher_visibility", "keep"), [
        ft.dropdown.Option("close", "游戏启动后立即关闭"),
        ft.dropdown.Option("hide_close", "游戏启动后隐藏，退出后关闭"),
        ft.dropdown.Option("hide_reopen", "游戏启动后隐藏，退出后重开"),
        ft.dropdown.Option("minimize", "游戏启动后最小化"),
        ft.dropdown.Option("keep", "游戏启动后仍保持不变"),
    ], width=280)
    launcher_visibility.on_select = lambda e: config.set("launch", "launcher_visibility", e.control.value)

    process_priority = make_dropdown(page, lc.get("process_priority", "normal"), [
        ft.dropdown.Option("realtime", "实时"),
        ft.dropdown.Option("very_high", "极高"),
        ft.dropdown.Option("high", "高"),
        ft.dropdown.Option("normal", "中（平衡）"),
        ft.dropdown.Option("low", "低"),
    ], width=280)
    process_priority.on_select = lambda e: config.set("launch", "process_priority", e.control.value)

    window_size_dd = make_dropdown(page, lc.get("window_size_mode", "default"), [
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
        value=lc.get("custom_width", ""),
    )
    custom_h = ft.TextField(
        hint_text="高", width=70, text_size=13,
        border_color=c["outline"], color=c["on_surface"],
        bgcolor=c["surface_variant"], filled=True,
        value=lc.get("custom_height", ""),
    )
    custom_size_row = ft.Row(
        controls=[
            custom_w,
            ft.Text("×", size=13, color=c["on_surface_variant"]),
            custom_h,
        ],
        spacing=6,
        visible=(window_size_dd.value == "custom"),
    )

    def on_window_size_change(e):
        val = e.control.value
        custom_size_row.visible = (val == "custom")
        config.set("launch", "window_size_mode", val)
        try:
            custom_size_row.update()
        except Exception:
            pass

    window_size_dd.on_select = on_window_size_change
    custom_w.on_blur = lambda e: config.set("launch", "custom_width", custom_w.value)
    custom_h.on_blur = lambda e: config.set("launch", "custom_height", custom_h.value)

    window_size_control = ft.Column(
        controls=[window_size_dd, custom_size_row],
        spacing=6,
        horizontal_alignment=ft.CrossAxisAlignment.END,
    )

    auth_method = make_dropdown(page, lc.get("auth_method", "device"), [
        ft.dropdown.Option("device", "设备代码流"),
        ft.dropdown.Option("pkce", "授权码流程 (PKCE)"),
    ], width=280)
    auth_method.on_select = lambda e: config.set("launch", "auth_method", e.control.value)

    ip_protocol = make_dropdown(page, lc.get("ip_protocol", "default"), [
        ft.dropdown.Option("ipv4", "IPv4 优先"),
        ft.dropdown.Option("default", "Java 默认"),
        ft.dropdown.Option("ipv6", "IPv6 优先"),
    ], width=280)
    ip_protocol.on_select = lambda e: config.set("launch", "ip_protocol", e.control.value)

    renderer = make_dropdown(page, lc.get("renderer", "default"), [
        ft.dropdown.Option("default", "游戏默认"),
        ft.dropdown.Option("llvmpipe", "软渲染 (llvmpipe)"),
        ft.dropdown.Option("d3d12", "DirectX12 (d3d12)"),
        ft.dropdown.Option("zink", "Vulkan (zink)"),
    ], width=280)
    renderer.on_select = lambda e: config.set("launch", "renderer", e.control.value)

    jvm_args_head = make_text_field(page, "JVM 参数头部", "-Djava.awt.headless=true", ft.Icons.TERMINAL)
    jvm_args_head.value = lc.get("jvm_args_head", "-Djava.awt.headless=true")
    jvm_args_head.on_blur = lambda e: config.set("launch", "jvm_args_head", jvm_args_head.value)

    game_args_tail = make_text_field(page, "游戏参数尾部", "--width 1280 --height 720", ft.Icons.TERMINAL)
    game_args_tail.value = lc.get("game_args_tail", "--width 1280 --height 720")
    game_args_tail.on_blur = lambda e: config.set("launch", "game_args_tail", game_args_tail.value)

    pre_exec_cmd = make_text_field(page, "启动前执行命令", "输入命令...", ft.Icons.TERMINAL)
    pre_exec_cmd.value = lc.get("pre_exec_cmd", "")
    pre_exec_cmd.on_blur = lambda e: config.set("launch", "pre_exec_cmd", pre_exec_cmd.value)

    def _cfg_switch(key, default):
        sw = make_switch(page, lc.get(key, default))
        sw.on_change = lambda e, k=key: config.set("launch", k, e.control.value)
        return sw

    return SmoothScroll(
        page=page,
        controls=[
            build_section_title(page, "启动", ft.Icons.ROCKET_LAUNCH_OUTLINED),

            ft.Text("启动选项", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "默认实例隔离", "选择实例隔离策略", instance_isolation),
            build_setting_row(page, "游戏窗口标题", "自定义游戏窗口显示标题", window_title),
            build_setting_row(page, "自定义信息", "自定义 F3 显示信息", custom_info),
            build_setting_row(page, "启动器可见性", "游戏运行时启动器的行为", launcher_visibility),
            build_setting_row(page, "进程优先级", "选择游戏进程优先级", process_priority),
            build_setting_row(page, "窗口大小", "游戏窗口大小模式", window_size_control),
            build_setting_row(page, "正版验证方式", "Microsoft 账户验证流程", auth_method),
            build_setting_row(page, "IP 协议偏好", "网络连接 IP 协议偏好", ip_protocol),

            ft.Text("游戏内存", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            _build_memory_panel(page, total_mem, used_mem),

            ft.Text("高级启动选项", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "渲染器", "游戏渲染后端", renderer),
            build_setting_row(page, "JVM 参数头部", "附加在 JVM 启动参数前部", jvm_args_head),
            build_setting_row(page, "游戏参数尾部", "传递给游戏的额外参数", game_args_tail),
            build_setting_row(page, "启动前执行命令", "游戏启动前执行的系统命令", pre_exec_cmd),
            build_setting_row(page, "禁用 Java Launch Wrapper", "", _cfg_switch("disable_java_wrapper", False)),
            build_setting_row(page, "禁用 LegacyFix", "", _cfg_switch("disable_legacyfix", False)),
            build_setting_row(page, "要求 Java 使用高性能显卡", "", _cfg_switch("force_high_perf_gpu", False)),
            build_setting_row(page, "使用 java.exe 而不是 javaw.exe", "", _cfg_switch("use_java_exe", True)),
            build_setting_row(page, "禁用 LWJGL Unsafe Agent", "", _cfg_switch("disable_lwjgl_unsafe", False)),
            build_setting_row(page, "禁用自动崩溃分析", "", _cfg_switch("disable_crash_analysis", False)),
        ],
        spacing=8,
        expand=True,
    )
