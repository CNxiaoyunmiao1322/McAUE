"""蓝粉/紫品红色调色板定义。

白天主题：柔和的蓝粉色渐变搭配浅色背景。
黑夜主题：深紫到亮品红渐变搭配深色背景。
"""

import flet as ft


class Colors:
    # ===== 白天主题 - 柔和蓝粉色调 =====
    LIGHT = {
        "primary": "#4F7CFF",            # 柔和蓝主色
        "on_primary": "#FFFFFF",
        "primary_container": "#E0E9FF",
        "on_primary_container": "#1A4099",
        "secondary": "#F56BA0",          # 柔和粉辅色
        "on_secondary": "#FFFFFF",
        "secondary_container": "#FDE4EF",
        "on_secondary_container": "#8C2456",
        "tertiary": "#8B5CF6",            # 紫色点缀
        "on_tertiary": "#FFFFFF",
        "background": "#F5F7FB",          # 柔和浅蓝白底
        "on_background": "#1A1F36",
        "surface": "#FFFFFF",
        "on_surface": "#1A1F36",
        "surface_variant": "#EEF2F9",
        "on_surface_variant": "#5A6378",
        "outline": "#C8D1E0",
        "outline_variant": "#DDE3EE",
        "error": "#EF4444",
        "on_error": "#FFFFFF",
        "error_container": "#FEE2E2",
        "on_error_container": "#991B1B",
        "shadow": "#B0BAC8",              # 浅色阴影
        "scrim": "#1A1F36",
        "gradient_start": "#6B9BFF",        # 明亮蓝渐变
        "gradient_end": "#FF80B0",          # 明亮粉渐变
        "button_accent": "#FF80B0",         # 启动按钮强调色
        "icon_accent": "#6B9BFF",           # 卡片图标强调色
    }

    # ===== 黑夜主题 - 更深的蓝粉色调 =====
    DARK = {
        "primary": "#2563EB",            # 深蓝主色
        "on_primary": "#FFFFFF",
        "primary_container": "#1E3A8A",  # 深蓝容器
        "on_primary_container": "#BFDBFE",
        "secondary": "#DB2777",          # 深粉辅色
        "on_secondary": "#FFFFFF",
        "secondary_container": "#831843", # 深粉容器
        "on_secondary_container": "#FBCFE8",
        "tertiary": "#7C3AED",            # 深紫点缀
        "on_tertiary": "#FFFFFF",
        "background": "#0B1120",          # 极深藏蓝底
        "on_background": "#E2E8F0",
        "surface": "#131C31",             # 深藏蓝面
        "on_surface": "#E2E8F0",
        "surface_variant": "#1E293B",
        "on_surface_variant": "#94A3B8",
        "outline": "#334155",
        "outline_variant": "#1E293B",
        "error": "#DC2626",
        "on_error": "#FFFFFF",
        "error_container": "#7F1D1D",
        "on_error_container": "#FECACA",
        "shadow": "#000000",
        "scrim": "#000000",
        "gradient_start": "#6D28D9",        # 深紫渐变
        "gradient_end": "#E879F9",          # 亮品红渐变
        "button_accent": "#E879F9",         # 启动按钮强调色
        "icon_accent": "#E879F9",           # 卡片图标强调色
    }

    @classmethod
    def get(cls, mode: str) -> dict:
        """根据主题模式获取色板。"""
        return cls.DARK if mode == "dark" else cls.LIGHT

    @classmethod
    def from_page(cls, page) -> dict:
        """根据 Page 当前主题模式获取色板。"""
        try:
            return cls.get("light") if page.theme_mode == ft.ThemeMode.LIGHT else cls.get("dark")
        except Exception:
            return cls.get("dark")

    @classmethod
    def build_color_scheme(cls, mode: str) -> ft.ColorScheme:
        """构建 Flet ColorScheme。"""
        c = cls.get(mode)
        return ft.ColorScheme(
            primary=c["primary"],
            on_primary=c["on_primary"],
            primary_container=c["primary_container"],
            on_primary_container=c["on_primary_container"],
            secondary=c["secondary"],
            on_secondary=c["on_secondary"],
            secondary_container=c["secondary_container"],
            on_secondary_container=c["on_secondary_container"],
            tertiary=c["tertiary"],
            on_tertiary=c["on_tertiary"],
            surface=c["surface"],
            on_surface=c["on_surface"],
            surface_container_high=c["surface_variant"],
            on_surface_variant=c["on_surface_variant"],
            outline=c["outline"],
            outline_variant=c["outline_variant"],
            error=c["error"],
            on_error=c["on_error"],
            error_container=c["error_container"],
            on_error_container=c["on_error_container"],
            shadow=c["shadow"],
            scrim=c["scrim"],
        )

    @classmethod
    def build_theme(cls, mode: str) -> ft.Theme:
        """构建 Flet Theme 对象。"""
        c = cls.get(mode)
        return ft.Theme(
            color_scheme=cls.build_color_scheme(mode),
            color_scheme_seed=c["primary"],
        )
