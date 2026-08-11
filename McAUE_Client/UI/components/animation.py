"""动画模块 - 平滑滚动、页面切换、标签过渡。

核心组件：
  SmoothScroll   基于 GestureDetector + Stack + animate_position 的平滑滚动，
                 直接捕获鼠标滚轮事件并动画化内容位置，实现真正的平滑滚动。
  tab_switcher   AnimatedSwitcher 封装，统一标签/页面切换动画参数。
"""

import time
import flet as ft

# ===== 动画常量 =====

SCROLL_DURATION = 200
SCROLL_CURVE = ft.AnimationCurve.EASE_OUT_CUBIC
MOMENTUM_FRICTION = 0.3
MOMENTUM_THRESHOLD = 120

TAB_DURATION = 400
TAB_REVERSE_DURATION = 300
PAGE_DURATION = 300
PAGE_REVERSE_DURATION = 200


# ===== 平滑滚动 =====

def SmoothScroll(page: ft.Page, controls: list = None, expand=True, spacing=8,
                 padding=None, column: ft.Column = None, **kwargs) -> ft.GestureDetector:
    """创建平滑滚动容器。

    使用 GestureDetector.on_scroll 捕获鼠标滚轮事件（scroll_delta 为像素值），
    通过 Stack + Container.top + animate_position 实现平滑滚动动画。

    用法：
        scroll = SmoothScroll(page=page, controls=[...], expand=True)
        scroll.key = "unique_key"

    传入外部 Column（需要后续更新 controls 时）：
        col = ft.Column(controls=[], spacing=2)
        scroll = SmoothScroll(page=page, column=col, expand=True)
        col.controls = new_controls  # 后续更新
        col.update()
    """
    if column is not None:
        content = column
    else:
        content = ft.Column(controls=controls or [], spacing=spacing)

    scroll_content = ft.Container(
        content=content,
        top=0,
        left=0,
        right=0,
        animate_position=ft.Animation(duration=SCROLL_DURATION, curve=SCROLL_CURVE),
        padding=padding,
    )

    stack = ft.Stack(
        controls=[scroll_content],
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        expand=expand,
    )

    state = {
        "scroll_y": 0.0,
        "content_h": 0.0,
        "viewport_h": 0.0,
        "velocity": 0.0,
        "last_time": 0.0,
        "max_scroll": 100000.0,
    }

    def on_content_size(e):
        try:
            state["content_h"] = e.height
            state["max_scroll"] = max(0, state["content_h"] - state["viewport_h"])
        except Exception:
            pass

    def on_stack_size(e):
        try:
            state["viewport_h"] = e.height
            state["max_scroll"] = max(0, state["content_h"] - state["viewport_h"])
        except Exception:
            pass

    content.on_size_change = on_content_size
    stack.on_size_change = on_stack_size

    def _do_scroll(dy, animate=True):
        new_y = state["scroll_y"] + dy
        new_y = max(0, min(new_y, state["max_scroll"]))
        state["scroll_y"] = new_y
        scroll_content.top = -new_y
        try:
            scroll_content.update()
        except Exception:
            pass

    def on_scroll(e):
        try:
            dy = e.scroll_delta.y
        except Exception:
            return

        now = time.time()
        dt = now - state["last_time"] if state["last_time"] > 0 else 0.016
        if dt > 0:
            state["velocity"] = dy / dt
        state["last_time"] = now

        _do_scroll(dy, animate=True)

    def on_pan(e):
        try:
            delta = e.local_delta
            dy = delta.y if delta else 0
        except Exception:
            try:
                dy = e.primary_delta or 0
            except Exception:
                return
        if dy == 0:
            return
        _do_scroll(-dy, animate=False)

    gesture = ft.GestureDetector(
        content=stack,
        on_scroll=on_scroll,
        on_pan_update=on_pan,
        expand=expand,
    )

    return gesture


# 兼容别名
make_scroll = SmoothScroll


# ===== 标签/页面切换 =====

def tab_switcher(content: ft.Control, key: str = "", duration: int = TAB_DURATION,
                 reverse_duration: int = TAB_REVERSE_DURATION) -> ft.AnimatedSwitcher:
    """创建标签切换 AnimatedSwitcher。"""
    content.key = key
    return ft.AnimatedSwitcher(
        content=content,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=duration,
        reverse_duration=reverse_duration,
        expand=True,
    )


def page_switcher(content: ft.Control, key: str = "", duration: int = PAGE_DURATION,
                  reverse_duration: int = PAGE_REVERSE_DURATION) -> ft.AnimatedSwitcher:
    """创建页面切换 AnimatedSwitcher。"""
    content.key = key
    return ft.AnimatedSwitcher(
        content=content,
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=duration,
        reverse_duration=reverse_duration,
        expand=True,
    )
