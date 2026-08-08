"""McAUE_Client - PySide6 客户端入口。

UI 文件（UI/untitled.ui）在运行时通过 QUiLoader 动态加载，
所有业务逻辑统一写在继承 QMainWindow 的 MainWindow 类中：
- UI 加载放在 __init__ 里；
- 加载完成后，UI 中每个具名控件都可以通过 self.<objectName> 直接访问。
"""

from __future__ import annotations

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
    QVariantAnimation,
    Qt,
)
from PySide6.QtGui import QColor
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
}
BUTTON_COLORS_DARK = {
    "normal": QColor("#3E5FCC"),
    "hover": QColor("#E84393"),
    "checked": QColor("#CC1970"),
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
    "tab_settings_button": "page_2",
    "tab_more_button": "page_2",
}


class MainWindow(QMainWindow):
    """客户端主窗口：UI 动态加载 + 全部业务逻辑。"""

    def __init__(self, ui_file: Path = UI_FILE):
        super().__init__()
        self._ui_window = None  # 持有 QUiLoader 加载出的临时窗口，防止被回收
        self.pageAnimation = None  # 页面切换动画，防止被垃圾回收
        self._button_colors = dict(BUTTON_COLORS_LIGHT)
        self._button_anims: dict[QPushButton, QVariantAnimation] = {}
        self._button_current: dict[QPushButton, QColor] = {}
        self._animated_buttons: set[QPushButton] = set()
        self._load_ui(ui_file)
        self._setup_frameless()
        self._setup_login_way()
        self._setup_menu()
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
        for button in self._animated_buttons:
            self._set_button_style(
                button,
                (
                    self._button_colors["checked"]
                    if button.isChecked()
                    else self._button_colors["normal"]
                ),
            )

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
