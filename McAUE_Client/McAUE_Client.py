"""McAUE_Client - PySide6 客户端入口。

UI 文件（UI/untitled.ui）在运行时通过 QUiLoader 动态加载，
所有业务逻辑统一写在继承 QMainWindow 的 MainWindow 类中：
- UI 加载放在 __init__ 里；
- 加载完成后，UI 中每个具名控件都可以通过 self.<objectName> 直接访问。
"""

from __future__ import annotations

import ctypes
import json
import sys
from pathlib import Path

from PySide6.QtCore import (
    QEasingCurve,
    QEvent,
    QFile,
    QIODevice,
    QObject,
    QPoint,
    QPropertyAnimation,
    QRect,
    QTimer,
    QVariantAnimation,
    Qt,
)
from PySide6.QtGui import QColor, QPainter
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
)
from qframelesswindow import WindowEffect

# 程序所在目录：本文件同级的 UI 文件夹
UI_FILE = Path(__file__).resolve().parent / "UI" / "untitled.ui"
STYLE_FILE = Path(__file__).resolve().parent / "UI" / "style.qss"
STYLE_DARK_FILE = Path(__file__).resolve().parent / "UI" / "style_dark.qss"

# 窗口圆角半径（像素）
CORNER_RADIUS = 12

# hover 颜色过渡时长（毫秒）
BUTTON_HOVER_MS = 100

# 登录方式组 / 底部菜单组按钮的主题色
BUTTON_COLORS_LIGHT = {
    "normal": QColor("#8EDCFF"),
    "hover": QColor("#FFB6D9"),
    "checked": QColor("#FF80BD"),
    "slider_handle": QColor("#ffffff"),
    "slider_handle_hover": QColor("#FFB6D9"),
    "slider_border": QColor("#4A7DFF"),
    "slider_disabled_handle": QColor("#d8d8d8"),
    "slider_disabled_border": QColor("#b0b0b0"),
    "mem_used": QColor("#4A6FE3"),
    "mem_game": QColor("#8EDCFF"),
    "mem_remaining": QColor("#D0D5DE"),
}
BUTTON_COLORS_DARK = {
    "normal": QColor("#3E5FCC"),
    "hover": QColor("#E84393"),
    "checked": QColor("#CC1970"),
    "slider_handle": QColor("#DCE4FF"),
    "slider_handle_hover": QColor("#E84393"),
    "slider_border": QColor("#6C8CFF"),
    "slider_disabled_handle": QColor("#3a3f55"),
    "slider_disabled_border": QColor("#555b75"),
    "mem_used": QColor("#2E4AA8"),
    "mem_game": QColor("#6C8CFF"),
    "mem_remaining": QColor("#3F4660"),
}

# 登录方式按钮（互斥，UI 里已设置 checkable）
LOGIN_BUTTONS = (
    "login_official_button",
    "login_offline_button",
    "login_thirdparty_button",
)

# 底部菜单按钮 -> 对应页面 objectName
MENU_BUTTONS = {
    "tab_launch_button": "launch",
    "tab_download_button": "page_2",
    "tab_tool_button": "page_2",
    "tab_settings_button": "setting",
    "tab_more_button": "page_2",
}

# 设置页左侧选项按钮 -> setting_content_area 子页面 objectName
SETTING_OPTION_BUTTONS = {
    "setting_launch_option_button": "launch_option_setting",
    "setting_mem_button": "mem_option",
    "setting_pro_option_button": "pro_setting",
}

# 设置持久化文件（与程序同目录）
SETTINGS_FILE = Path(__file__).resolve().parent / "settings.json"


class MainWindow(QMainWindow):
    """客户端主窗口：UI 动态加载 + 全部业务逻辑。"""

    def __init__(self, ui_file: Path = UI_FILE):
        super().__init__()
        self._ui_window = None  # 持有 QUiLoader 加载出的临时窗口，防止被回收
        self.pageAnimation = None  # 页面切换动画，防止被垃圾回收
        self.settingPageAnimation = None  # 设置子页面切换动画
        self._slider_anim = None  # 滑块 handle hover 动画
        self._button_colors = dict(BUTTON_COLORS_LIGHT)
        self._button_anims: dict[QPushButton, QVariantAnimation] = {}
        self._button_current: dict[QPushButton, QColor] = {}
        self._animated_buttons: set[QPushButton] = set()
        self._loading_settings = False
        self._load_ui(ui_file)
        self._setup_frameless()
        self._setup_login_way()
        self._setup_menu()
        self._setup_setting_page()
        self._setup_memory_page()
        self._load_settings()
        self._update_memory_display()
        # 启动时默认停在“启动”页，与底部选中的“启动”标签保持一致
        self.stackedWidget.setCurrentIndex(0)
        self._connect_window_buttons()

    # ---------- UI 加载 ----------

    def _load_ui(self, ui_file: Path) -> None:
        """加载 untitled.ui，并把其中所有具名控件挂到 self.<控件名> 上。"""
        if not ui_file.exists():
            raise FileNotFoundError(f"找不到 UI 文件：{ui_file}")

        qfile = QFile(str(ui_file))
        if not qfile.open(QIODevice.OpenModeFlag.ReadOnly):
            raise RuntimeError(f"无法打开 UI 文件：{ui_file}")

        loader = QUiLoader()
        try:
            loaded_window = loader.load(qfile, None)
        finally:
            qfile.close()

        if loaded_window is None:
            raise RuntimeError(f"UI 文件加载失败：{loader.errorString()}")
        self._ui_window = loaded_window

        central = loaded_window.centralWidget()
        if central is None:
            raise RuntimeError(f"UI 文件没有 centralWidget：{ui_file}")
        self.setCentralWidget(central)
        # 把 .ui 里定义的窗口尺寸同步到我们的主窗口
        self.resize(loaded_window.size())

        # 让所有具名控件都可以通过 self.<objectName> 访问
        for obj in self.findChildren(QObject):
            name = obj.objectName()
            if name:
                setattr(self, name, obj)

    # ---------- 控件初始化 ----------

    def _setup_frameless(self) -> None:
        """无边框、圆角、标题栏拖动、禁止调整窗口大小。"""
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        # 锁死窗口尺寸，禁止缩放
        self.setFixedSize(self.size())

        # 加载主题样式（亮/暗跟随系统），并监听系统主题切换
        self._apply_theme()
        QApplication.styleHints().colorSchemeChanged.connect(self._apply_theme)

        # 使用 WindowEffect 恢复 DWM 窗口阴影，以及最大化/最小化动画
        self._window_effect = WindowEffect(self)
        self._window_effect.addShadowEffect(self.winId())
        self._window_effect.addWindowAnimation(self.winId())

        # 在标题栏区域（包括标题文字）上按住左键可拖动窗口
        self._drag_offset: QPoint | None = None
        title_area = getattr(self, "title_area", None)
        if title_area is not None:
            title_area.installEventFilter(self)
        title_label = getattr(self, "title", None)
        if title_label is not None:
            title_label.installEventFilter(self)

    def _apply_theme(self, scheme: Qt.ColorScheme | None = None) -> None:
        """按系统深浅色加载 QSS；文件不存在时退回代码内的基础样式。"""
        if scheme is None:
            scheme = QApplication.styleHints().colorScheme()
        is_dark = scheme == Qt.ColorScheme.Dark
        self._button_colors = dict(BUTTON_COLORS_DARK if is_dark else BUTTON_COLORS_LIGHT)
        style_file = STYLE_DARK_FILE if is_dark else STYLE_FILE
        if style_file.exists():
            self.setStyleSheet(style_file.read_text(encoding="utf-8"))
        else:
            background = (
                "rgba(24, 28, 48, 240)"
                if is_dark
                else "rgba(235, 240, 255, 235)"
            )
            self.setStyleSheet(
                "#centralwidget {"
                f" background: {background};"
                f" border-radius: {CORNER_RADIUS}px;"
                "}"
            )
        self._reset_button_colors()
        self._update_memory_display()

    def _setup_login_way(self) -> None:
        """正版/离线/第三方三个登录方式按钮互斥。"""
        self._login_group = QButtonGroup(self)
        self._login_group.setExclusive(True)
        for name in LOGIN_BUTTONS:
            button = getattr(self, name, None)
            if isinstance(button, QPushButton):
                self._login_group.addButton(button)
                self._setup_button_hover(button)

    def _setup_menu(self) -> None:
        """底部菜单按钮互斥，并控制 QStackedWidget 页面切换。"""
        self._menu_group = QButtonGroup(self)
        self._menu_group.setExclusive(True)
        for name in MENU_BUTTONS:
            button = getattr(self, name, None)
            if isinstance(button, QPushButton):
                self._menu_group.addButton(button)
                self._setup_button_hover(button)
                button.clicked.connect(
                    lambda checked=False, b=button: self.switch_page(b)
                )

    def _setup_setting_page(self) -> None:
        """设置页：左侧选项按钮互斥、绑定子页面、记忆内存模式联动、即时保存。"""
        self._setting_option_group = QButtonGroup(self)
        self._setting_option_group.setExclusive(True)
        for name, page_name in SETTING_OPTION_BUTTONS.items():
            button = getattr(self, name, None)
            if isinstance(button, QPushButton):
                self._setting_option_group.addButton(button)
                self._setup_button_hover(button)
                button.clicked.connect(
                    lambda checked=False, b=button, p=page_name: self.switch_setting_page(b, p)
                )

        # 内存模式联动滑块：自动 -> 禁用，自定义 -> 启用
        if hasattr(self, "mem_auto"):
            self.mem_auto.toggled.connect(self.mem_slider.setDisabled)
        if hasattr(self, "mem_custom"):
            self.mem_custom.toggled.connect(self.mem_slider.setEnabled)

        self._connect_settings_signals()
        self._setup_slider_hover()

    def switch_setting_page(self, button: QPushButton, page_name: str) -> None:
        """把设置页左侧按钮绑定到对应子页面，并自下而上滑入。"""
        content = getattr(self, "setting_content_area", None)
        if content is None:
            return
        for index in range(content.count()):
            if content.widget(index).objectName() == page_name:
                old = content.currentWidget()
                new = content.widget(index)
                if old is new or new is None:
                    return
                if self.settingPageAnimation is not None:
                    self.settingPageAnimation.stop()

                new.move(0, 300)
                content.setCurrentIndex(index)

                animation = QPropertyAnimation(new, b"pos")
                animation.setDuration(250)
                animation.setStartValue(QPoint(0, 300))
                animation.setEndValue(QPoint(0, 0))
                animation.setEasingCurve(QEasingCurve.OutCubic)
                animation.start()
                self.settingPageAnimation = animation
                return

    def _setup_slider_hover(self) -> None:
        """给内存滑块 handle 添加 hover 颜色过渡（0.1s 平滑变化）。"""
        slider = getattr(self, "mem_slider", None)
        if slider is None:
            return
        slider.installEventFilter(self)
        self._slider_anim = QVariantAnimation(slider)
        self._slider_anim.setDuration(BUTTON_HOVER_MS)
        self._slider_anim.valueChanged.connect(self._on_slider_anim_value)
        self._set_slider_handle(self._button_colors["slider_handle"])

    def _setup_memory_page(self) -> None:
        """内存分配页：真实内存数值、自动/手动分配逻辑、mem_display 绘图、1s 实时刷新。"""
        mem_display = getattr(self, "mem_display", None)
        if mem_display is not None:
            mem_display.installEventFilter(self)
        for radio in (getattr(self, "mem_auto", None), getattr(self, "mem_custom", None)):
            if radio is not None:
                radio.toggled.connect(self._update_memory_display)
        if hasattr(self, "mem_slider"):
            self.mem_slider.valueChanged.connect(self._update_memory_display)
        # 每 1 秒刷新一次已用/空闲内存
        self._memory_timer = QTimer(self)
        self._memory_timer.setInterval(1000)
        self._memory_timer.timeout.connect(self._update_memory_display)
        self._memory_timer.start()

    def _update_memory_display(self) -> None:
        """刷新内存标签和 mem_display 绘图。"""
        total, avail = self._get_system_memory()
        if total <= 0:
            return
        gb = 1024 ** 3
        used_gb = (total - avail) / gb
        total_gb = total / gb
        game_gb = self._current_game_memory_bytes() / gb
        free_gb = avail / gb
        if hasattr(self, "used_mem_label"):
            self.used_mem_label.setText(f"{used_gb:.1f}/{total_gb:.1f} GB")
        if hasattr(self, "game_use_mem_label"):
            if game_gb > free_gb:
                self.game_use_mem_label.setText(
                    f"{game_gb:.1f} GB（空闲 {free_gb:.1f} GB）"
                )
            else:
                self.game_use_mem_label.setText(f"{game_gb:.1f} GB")
        mem_display = getattr(self, "mem_display", None)
        if mem_display is not None:
            mem_display.update()

    @staticmethod
    def _get_system_memory() -> tuple[int, int]:
        """返回 (总物理内存, 可用物理内存)，单位字节。"""
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(stat)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return 0, 0
        return int(stat.ullTotalPhys), int(stat.ullAvailPhys)

    def _get_auto_game_memory_gb(self) -> float:
        """自动分配时的游戏内存（GB）。

        目前固定为 1GB，后续在这里补上真实的自动分配逻辑。
        """
        # TODO: 自动分配真实规则
        return 1.0

    def _current_game_memory_bytes(self) -> int:
        """当前模式下的游戏分配内存（字节）。"""
        total, avail = self._get_system_memory()
        if getattr(self, "mem_custom", None) is not None and self.mem_custom.isChecked():
            percent = self.mem_slider.value() if hasattr(self, "mem_slider") else 0
            return int(total * percent / 100)
        return int(self._get_auto_game_memory_gb() * 1024 ** 3)

    def _paint_mem_display(self, widget) -> None:
        """在 mem_display 上用 QPainter 绘制内存分配矩形条。"""
        painter = QPainter(widget)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            total, avail = self._get_system_memory()
            if total <= 0:
                return
            used = total - avail
            game = self._current_game_memory_bytes()
            bar = QRect(widget.rect()).adjusted(2, 2, -2, -2)
            colors = self._button_colors
            used_w = int(bar.width() * used / total)
            game_w = int(bar.width() * game / total)
            remaining_w = bar.width() - used_w - game_w

            x = bar.left()
            for width, key in (
                (used_w, "mem_used"),
                (game_w, "mem_game"),
                (remaining_w, "mem_remaining"),
            ):
                if width <= 0:
                    continue
                painter.fillRect(x, bar.top(), width, bar.height(), colors[key])
                x += width
        finally:
            painter.end()

    def _set_slider_handle(self, color: QColor) -> None:
        """刷新滑块 handle 的行内样式（保留禁用态）。"""
        slider = getattr(self, "mem_slider", None)
        if slider is None:
            return
        self._slider_handle_current = QColor(color)
        bg = QColor(color).name(QColor.NameFormat.HexRgb)
        border = self._button_colors["slider_border"].name(QColor.NameFormat.HexRgb)
        disabled_bg = self._button_colors["slider_disabled_handle"].name(
            QColor.NameFormat.HexRgb
        )
        disabled_border = self._button_colors["slider_disabled_border"].name(
            QColor.NameFormat.HexRgb
        )
        slider.setStyleSheet(
            "#mem_slider::handle:horizontal {"
            " width: 18px; height: 18px; margin: -5px 0;"
            f" border-radius: 9px; background: {bg}; border: 2px solid {border};"
            " }"
            "#mem_slider::handle:horizontal:disabled {"
            f" background: {disabled_bg}; border: 2px solid {disabled_border};"
            " }"
        )

    def _start_slider_anim(self, end_color: QColor) -> None:
        """从当前 handle 颜色平滑过渡到目标颜色。"""
        if self._slider_anim is None:
            return
        start = getattr(
            self, "_slider_handle_current", self._button_colors["slider_handle"]
        )
        self._slider_anim.stop()
        self._slider_anim.setStartValue(start)
        self._slider_anim.setEndValue(QColor(end_color))
        self._slider_anim.start()

    def _on_slider_anim_value(self, value) -> None:
        """滑块 handle 动画每一帧刷新颜色。"""
        self._set_slider_handle(QColor(value))

    def _connect_settings_signals(self) -> None:
        """所有设置控件变化时立即保存到本地 JSON。"""
        if hasattr(self, "mem_auto"):
            self.mem_auto.toggled.connect(self._save_settings)
        if hasattr(self, "mem_custom"):
            self.mem_custom.toggled.connect(self._save_settings)
        if hasattr(self, "mem_slider"):
            self.mem_slider.valueChanged.connect(self._save_settings)
        if hasattr(self, "jvm_para"):
            self.jvm_para.textChanged.connect(self._save_settings)
        if hasattr(self, "game_para"):
            self.game_para.textChanged.connect(self._save_settings)
        if hasattr(self, "cmd_before_launch"):
            self.cmd_before_launch.textChanged.connect(self._save_settings)
        if hasattr(self, "java_list_comboBox"):
            self.java_list_comboBox.currentIndexChanged.connect(self._save_settings)
        if hasattr(self, "ban_jlw"):
            self.ban_jlw.toggled.connect(self._save_settings)
        if hasattr(self, "ban_lwjgl"):
            self.ban_lwjgl.toggled.connect(self._save_settings)
        if hasattr(self, "version_isolate_comboBox"):
            self.version_isolate_comboBox.currentIndexChanged.connect(self._save_settings)
        if hasattr(self, "game_title"):
            self.game_title.textChanged.connect(self._save_settings)
        if hasattr(self, "setting_custom_info"):
            self.setting_custom_info.textChanged.connect(self._save_settings)
        if hasattr(self, "launcher_visble_comboBox"):
            self.launcher_visble_comboBox.currentIndexChanged.connect(self._save_settings)

    def _save_settings(self, *args) -> None:
        """把当前设置写入本地 settings.json（与程序同目录）。"""
        if self._loading_settings:
            return

        def get_text(name: str, default: str = "") -> str:
            obj = getattr(self, name, None)
            if obj is None:
                return default
            if hasattr(obj, "toPlainText"):
                return obj.toPlainText()
            if hasattr(obj, "currentText"):
                return obj.currentText()
            return obj.text()

        def get_bool(name: str) -> bool:
            obj = getattr(self, name, None)
            return bool(obj.isChecked()) if obj is not None else False

        def get_index(name: str, default: int = 0) -> int:
            obj = getattr(self, name, None)
            return int(obj.currentIndex()) if obj is not None else default

        mem_slider = getattr(self, "mem_slider", None)
        data = {
            "mem_mode": "auto" if get_bool("mem_auto") else "custom",
            "mem_value": int(mem_slider.value()) if mem_slider is not None else 0,
            "jvm_para": get_text("jvm_para"),
            "game_para": get_text("game_para"),
            "cmd_before_launch": get_text("cmd_before_launch"),
            "java_list": get_text("java_list_comboBox"),
            "ban_jlw": get_bool("ban_jlw"),
            "ban_lwjgl": get_bool("ban_lwjgl"),
            "version_isolate": get_index("version_isolate_comboBox"),
            "game_title": get_text("game_title"),
            "setting_custom_info": get_text("setting_custom_info"),
            "launcher_visble": get_index("launcher_visble_comboBox"),
        }
        try:
            SETTINGS_FILE.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as exc:
            print(f"保存设置失败：{exc}")

    def _load_settings(self) -> None:
        """启动时读取 settings.json 并还原设置。"""
        if not SETTINGS_FILE.exists():
            return
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(data, dict):
            return

        self._loading_settings = True
        try:
            if "mem_mode" in data and hasattr(self, "mem_auto"):
                self.mem_auto.setChecked(data.get("mem_mode") == "auto")
                self.mem_custom.setChecked(data.get("mem_mode") == "custom")
            if "mem_value" in data and hasattr(self, "mem_slider"):
                self.mem_slider.setValue(int(data["mem_value"]))
            if "jvm_para" in data and hasattr(self, "jvm_para"):
                self.jvm_para.setPlainText(str(data["jvm_para"]))

            for name in ("game_para", "cmd_before_launch", "game_title", "setting_custom_info"):
                if name in data and hasattr(self, name):
                    getattr(self, name).setText(str(data[name]))

            for name in ("ban_jlw", "ban_lwjgl"):
                if name in data and hasattr(self, name):
                    getattr(self, name).setChecked(bool(data[name]))

            for widget_name, key in (
                ("version_isolate_comboBox", "version_isolate"),
                ("launcher_visble_comboBox", "launcher_visble"),
            ):
                if key in data and hasattr(self, widget_name):
                    combo = getattr(self, widget_name)
                    index = int(data[key])
                    if 0 <= index < combo.count():
                        combo.setCurrentIndex(index)

            if "java_list" in data and hasattr(self, "java_list_comboBox"):
                combo = self.java_list_comboBox
                index = combo.findText(str(data["java_list"]))
                if index >= 0:
                    combo.setCurrentIndex(index)
        except (ValueError, TypeError):
            pass
        finally:
            self._loading_settings = False

    def _setup_button_hover(self, button: QPushButton) -> None:
        """给登录/菜单按钮装 hover 颜色过渡（0.1s 平滑变化，而非渐变）。"""
        button.installEventFilter(self)
        self._animated_buttons.add(button)
        button.toggled.connect(
            lambda checked, b=button: self._on_button_toggled(b, checked)
        )

        animation = QVariantAnimation(button)
        animation.setDuration(BUTTON_HOVER_MS)
        animation.valueChanged.connect(
            lambda value, b=button: self._on_button_anim_value(b, value)
        )
        self._button_anims[button] = animation
        self._set_button_style(
            button,
            (
                self._button_colors["checked"]
                if button.isChecked()
                else self._button_colors["normal"]
            ),
        )

    def _on_button_toggled(self, button: QPushButton, checked: bool) -> None:
        """按钮选中/取消选中时修正背景色，避免残留 hover 颜色。"""
        animation = self._button_anims.get(button)
        if animation is not None:
            animation.stop()
        if checked:
            self._button_current[button] = QColor(self._button_colors["checked"])
        else:
            # 先让常态色等于当前显示色，再平滑过渡回常态色，防止闪烁
            current = self._button_current.get(
                button, self._button_colors["normal"]
            )
            self._set_button_style(button, current)
            self._start_button_anim(button, self._button_colors["normal"])

    def _reset_button_colors(self) -> None:
        """主题切换后停止所有过渡，并把按钮恢复为常态颜色。"""
        for animation in self._button_anims.values():
            animation.stop()
        if self._slider_anim is not None:
            self._slider_anim.stop()
        for button in self._animated_buttons:
            self._set_button_style(
                button,
                (
                    self._button_colors["checked"]
                    if button.isChecked()
                    else self._button_colors["normal"]
                ),
            )
        self._set_slider_handle(self._button_colors["slider_handle"])

    def _set_button_style(self, button: QPushButton, color: QColor) -> None:
        """用行内样式覆盖按钮背景色（选中态始终保持选中色）。"""
        self._button_current[button] = QColor(color)
        normal = QColor(color).name(QColor.NameFormat.HexRgb)
        checked = self._button_colors["checked"].name(QColor.NameFormat.HexRgb)
        button.setStyleSheet(
            f"QPushButton {{ background-color: {normal}; }}"
            f"QPushButton:checked {{ background-color: {checked}; }}"
        )

    def _start_button_anim(self, button: QPushButton, end_color: QColor) -> None:
        """从当前颜色平滑过渡到目标颜色。"""
        animation = self._button_anims.get(button)
        if animation is None:
            return
        start = self._button_current.get(button, self._button_colors["normal"])
        animation.stop()
        animation.setStartValue(start)
        animation.setEndValue(QColor(end_color))
        animation.start()

    def _on_button_anim_value(self, button: QPushButton, value) -> None:
        """动画每一帧刷新按钮背景色。"""
        self._set_button_style(button, QColor(value))

    def _connect_window_buttons(self) -> None:
        """标题栏按钮：最小化 / 关闭，以及启动页的业务按钮。"""
        if hasattr(self, "min_button"):
            self.min_button.clicked.connect(self.showMinimized)
        if hasattr(self, "quit_button"):
            self.quit_button.clicked.connect(self.close)
        if hasattr(self, "launch_game_button"):
            self.launch_game_button.clicked.connect(self.on_launch_game_clicked)
        if hasattr(self, "choose_version_button"):
            self.choose_version_button.clicked.connect(
                self.on_choose_version_clicked
            )

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        """处理标题栏拖动，以及登录/菜单按钮的 hover 颜色过渡。"""
        if isinstance(obj, QPushButton) and obj in self._animated_buttons:
            if event.type() == QEvent.Type.Enter and not obj.isChecked():
                self._start_button_anim(obj, self._button_colors["hover"])
            elif event.type() == QEvent.Type.Leave and not obj.isChecked():
                self._start_button_anim(obj, self._button_colors["normal"])

        mem_display = getattr(self, "mem_display", None)
        if obj is mem_display and event.type() == QEvent.Type.Paint:
            self._paint_mem_display(obj)
            event.accept()
            return True

        slider = getattr(self, "mem_slider", None)
        if obj is slider:
            if event.type() == QEvent.Type.Enter and slider.isEnabled():
                self._start_slider_anim(self._button_colors["slider_handle_hover"])
            elif event.type() == QEvent.Type.Leave:
                self._start_slider_anim(self._button_colors["slider_handle"])

        title_area = getattr(self, "title_area", None)
        title_label = getattr(self, "title", None)
        if obj is title_area or obj is title_label:
            if (
                event.type() == QEvent.Type.MouseButtonPress
                and event.button() == Qt.MouseButton.LeftButton
            ):
                self._drag_offset = (
                    event.globalPosition().toPoint()
                    - self.frameGeometry().topLeft()
                )
                event.accept()
                return True
            if (
                event.type() == QEvent.Type.MouseMove
                and self._drag_offset is not None
                and event.buttons() & Qt.MouseButton.LeftButton
            ):
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                event.accept()
                return True
            if event.type() == QEvent.Type.MouseButtonRelease:
                self._drag_offset = None
                event.accept()
                return True
        return super().eventFilter(obj, event)

    def showEvent(self, event) -> None:
        """显示后锁定固定几何按钮的高度（QSS 内容最小高度会顶掉 min-height）。"""
        super().showEvent(event)
        if hasattr(self, "choose_version_button"):
            self.choose_version_button.setFixedHeight(28)

    # ---------- 业务逻辑（后续在这里扩展） ----------

    def switchPage(self, index: int) -> None:
        """带滑动动画地切换到指定页面（index 为 QStackedWidget 中的页面序号）。"""
        stack = self.stackedWidget
        old = stack.currentWidget()
        new = stack.widget(index)
        if old is new or new is None:
            return

        # 停止上一个未完成的动画，避免两个页面同时滑动
        if self.pageAnimation is not None:
            self.pageAnimation.stop()

        new.move(300, 0)
        stack.setCurrentIndex(index)

        animation = QPropertyAnimation(new, b"pos")
        animation.setDuration(250)
        animation.setStartValue(QPoint(300, 0))
        animation.setEndValue(QPoint(0, 0))
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        self.pageAnimation = animation

    def switch_page(self, button: QPushButton) -> None:
        """根据底部菜单按钮解析页面序号，并交给 switchPage 做滑动切换。"""
        page_name = MENU_BUTTONS.get(button.objectName())
        stacked_widget: QStackedWidget = getattr(self, "stackedWidget", None)
        if stacked_widget is None or page_name is None:
            return
        for index in range(stacked_widget.count()):
            if stacked_widget.widget(index).objectName() == page_name:
                self.switchPage(index)
                return

    def on_launch_game_clicked(self) -> None:
        """点击“启动游戏”。"""
        # TODO: 启动游戏业务逻辑
        print("启动游戏（待实现）：", self.username_lineEdit.text())

    def on_choose_version_clicked(self) -> None:
        """点击“选择版本”。"""
        # TODO: 选择版本业务逻辑
        print("选择版本（待实现）")


def main() -> int:
    app = QApplication(sys.argv)
    try:
        window = MainWindow()
    except Exception as exc:
        QMessageBox.critical(None, "界面加载失败", str(exc))
        return 1
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
