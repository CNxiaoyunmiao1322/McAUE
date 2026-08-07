
"""McAUE_Client - PySide6 客户端入口。

使用 QUiLoader 在运行时动态加载同目录下的 untitled.ui，
不需要先用 pyside6-uic 把 .ui 编译成 .py。
"""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QMessageBox,
    QPushButton,
    QStackedWidget,
)

UI_FILE = Path(__file__).resolve().parent / "untitled.ui"

# 登录方式按钮（login_way 布局里的三个按钮）
LOGIN_BUTTONS = (
    "login_official_button",
    "login_offline_button",
    "login_thirdparty_button",
)

# 底部菜单按钮 -> 对应的页面 objectName（QStackedWidget 里没有的页面会被忽略）
MENU_BUTTONS = {
    "tab_launch_button": "launch",
    "tab_download_button": "page_2",
    "tab_tool_button": "page_2",
    "tab_settings_button": "page_2",
    "tab_more_button": "page_2",
}


def load_ui(loader: QUiLoader, ui_file: Path):
    """打开 untitled.ui 并动态加载，返回窗口对象。"""
    if not ui_file.exists():
        raise FileNotFoundError(f"找不到 UI 文件：{ui_file}")

    qfile = QFile(str(ui_file))
    if not qfile.open(QIODevice.OpenModeFlag.ReadOnly):
        raise RuntimeError(f"无法打开 UI 文件：{ui_file}")

    try:
        window = loader.load(qfile, None)
    finally:
        qfile.close()

    if window is None:
        raise RuntimeError(f"UI 文件加载失败：{loader.errorString()}")
    return window


def setup_login_way(window) -> None:
    """把 正版/离线/第三方 三个按钮加入互斥的 QButtonGroup。"""
    login_group = QButtonGroup(window)
    login_group.setExclusive(True)

    for name in LOGIN_BUTTONS:
        button = window.findChild(QPushButton, name)
        if button is not None:
            # UI 里这三个按钮没有 checkable 属性，这里补上，互斥才会生效
            button.setCheckable(True)
            login_group.addButton(button)


def setup_menu(window) -> None:
    """底部菜单按钮用互斥的 QButtonGroup 控制 QStackedWidget 的页面。"""
    stacked_widget = window.findChild(QStackedWidget, "stackedWidget")
    if stacked_widget is None:
        return

    menu_group = QButtonGroup(window)
    menu_group.setExclusive(True)

    pages = {
        stacked_widget.widget(index).objectName(): index
        for index in range(stacked_widget.count())
    }

    def switch_page(button: QPushButton) -> None:
        page_name = MENU_BUTTONS.get(button.objectName())
        if page_name in pages:
            stacked_widget.setCurrentIndex(pages[page_name])

    for name in MENU_BUTTONS:
        button = window.findChild(QPushButton, name)
        if button is not None:
            menu_group.addButton(button)
            button.clicked.connect(
                lambda checked=False, b=button: switch_page(b)
            )

    # 默认停在“启动”页，并让“启动”按钮处于选中状态
    launch_button = window.findChild(QPushButton, "tab_launch_button")
    if launch_button is not None:
        launch_button.setChecked(True)


def main() -> int:
    app = QApplication(sys.argv)

    try:
        window = load_ui(QUiLoader(), UI_FILE)
    except Exception as exc:
        QMessageBox.critical(None, "界面加载失败", str(exc))
        return 1

    setup_login_way(window)
    setup_menu(window)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
