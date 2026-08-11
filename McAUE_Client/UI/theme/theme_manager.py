"""主题管理器 - 管理白天/黑夜/跟随系统主题切换。

与 config.py 集成，主题模式自动持久化。
"""

import subprocess

from state.config import config


class ThemeManager:
    """管理应用主题状态，支持白天/黑夜/跟随系统切换。"""

    def __init__(self):
        self._mode = config.get("theme_mode", default="dark")
        if self._mode not in ("dark", "light", "system"):
            self._mode = "dark"
        self._system_dark = None

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def is_system(self) -> bool:
        return self._mode == "system"

    @property
    def is_dark(self) -> bool:
        if self._mode == "system":
            if self._system_dark is not None:
                return self._system_dark
            return self._detect_system_dark()
        return self._mode == "dark"

    def set_mode(self, mode: str):
        if mode in ("dark", "light", "system"):
            self._mode = mode
            config.set("theme_mode", None, mode)

    def set_system_dark(self, is_dark: bool):
        self._system_dark = is_dark

    def toggle(self):
        self._mode = "light" if self.is_dark else "dark"
        config.set("theme_mode", None, self._mode)

    @staticmethod
    def _detect_system_dark() -> bool:
        try:
            result = subprocess.run(
                ["reg", "query",
                 r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                 "/v", "AppsUseLightTheme"],
                capture_output=True, text=True, timeout=2,
            )
            return "0x0" in result.stdout
        except Exception:
            return True
