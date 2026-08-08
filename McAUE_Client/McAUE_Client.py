import sys
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect
)
from PySide6.QtCore import (
    Qt,
    QFile,
    QEvent,
    QPoint,
    QTimer,
    QPropertyAnimation,
    QEasingCurve
)
from PySide6.QtUiTools import QUiLoader

class Toast(QLabel):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
        QLabel{
            background:#323544;
            color:white;
            border-radius:12px;
            padding:10px 25px;
            font-size:14px;
        }
        """)
        self.adjustSize()
        self.move((parent.width()-self.width())//2,parent.height()-100)
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)
        self.anim = QPropertyAnimation(effect,b"opacity")
        self.anim.setDuration(300)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.start()
        self.show()
        QTimer.singleShot(2000,self.close)

class Launcher(QMainWindow):
    def __init__(self):
        super().__init__()
        # 无边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 支持圆角
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.dragPosition = None

        # 加载 UI
        loader = QUiLoader()
        file = QFile(".//UI//MCAUE_Launcher_v3.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file)
        file.close()
        self.setCentralWidget(self.ui)
        self.resize(1100,700)
        self.setMinimumSize(1100,700)

        # 加载 QSS
        with open(".//UI//MCAUE_v3.qss","r",encoding="utf-8") as f:
            self.setStyleSheet(f.read())
        # 阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(35)
        shadow.setOffset(0,0)
        self.ui.centralwidget.setGraphicsEffect(shadow)

        # 标题栏鼠标
        self.ui.titleBar.installEventFilter(self)
        # 防止标题文字阻挡拖动
        self.ui.titleLabel.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.initButton()

    # ======================
    # 按钮绑定
    # ======================
    def initButton(self):
        ui=self.ui
        ui.closeButton.clicked.connect(self.close)
        ui.minButton.clicked.connect(self.showMinimized)
        ui.navLaunch.clicked.connect(lambda:self.switchPage(0))
        ui.navDownload.clicked.connect(lambda:self.switchPage(1))
        ui.navTool.clicked.connect(lambda:self.switchPage(2))
        ui.navSetting.clicked.connect(lambda:self.switchPage(3))
        ui.navMore.clicked.connect(lambda:self.switchPage(4))
        ui.launchButton.clicked.connect(
            lambda:self.showToast(
                "正在启动 Minecraft..."
            )
        )

    # ======================
    # 页面切换动画
    # ======================
    def switchPage(self,index):
        stack=self.ui.pageStack
        old=stack.currentWidget()
        new=stack.widget(index)
        if old==new:
            return
        new.move(300,0)
        stack.setCurrentIndex(index)
        animation=QPropertyAnimation(new,b"pos")
        animation.setDuration(250)
        animation.setStartValue(QPoint(300,0))
        animation.setEndValue(QPoint(0,0))
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        self.pageAnimation=animation

    # ======================
    # Toast
    # ======================
    def showToast(self,text):
        Toast(self,text)
    # ======================
    # 标题栏拖动
    # ======================
    def eventFilter(self,obj,event):
        if obj==self.ui.titleBar:
            if event.type()==QEvent.MouseButtonPress:
                if event.button()==Qt.LeftButton:
                    self.dragPosition=(event.globalPosition().toPoint()-self.frameGeometry().topLeft()
                    )
                    return True
            elif event.type()==QEvent.MouseMove:
                if self.dragPosition:
                    self.move(event.globalPosition().toPoint()-self.dragPosition)
                    return True
            elif event.type()==QEvent.MouseButtonRelease:
                self.dragPosition=None
                return True
        return super().eventFilter(obj,event)
if __name__=="__main__":
    app=QApplication(sys.argv)
    window=Launcher()
    window.show()
    sys.exit(app.exec())