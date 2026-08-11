"""全局应用状态 - 管理用户信息、当前视图、主题等。

与 config.py 集成，所有设置自动持久化到 JSON 配置文件。
"""

from dataclasses import dataclass, field
from state.config import config


@dataclass
class NewsItem:
    title: str
    summary: str
    tag: str


@dataclass
class ToolItem:
    name: str
    description: str
    icon: str


@dataclass
class AppState:
    """全局应用状态。"""

    username: str = ""
    logged_in: bool = False
    current_route: str = "/home"
    news: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    download_category: str = "mc_install"
    download_expanded: list = field(default_factory=lambda: ["community", "installers"])
    settings_tab: str = "launch"
    home_subview: str = "home"
    home_vs_version: str = ""
    about_subview: str = "about"
    tools_subview: str = "grid"

    def __post_init__(self):
        nav = config.get("navigation")
        self.current_route = nav.get("current_route", "/home")
        self.settings_tab = nav.get("settings_tab", "launch")

        account = config.get("account")
        self.username = account.get("username", "")
        self.logged_in = account.get("logged_in", False)

        self.news = [
            NewsItem(
                "1.21.5 快照发布",
                "新的试炼密室更新已进入快照阶段，包含全新生物群系。",
                "更新",
            ),
            NewsItem(
                "基岩版跨平台联机优化",
                "基岩版现已支持更稳定的跨平台联机体验。",
                "公告",
            ),
            NewsItem(
                "Mod API 重大更新",
                "Fabric & NeoForge 同步更新至最新版本接口。",
                "Mod",
            ),
        ]
        self.tools = [
            ToolItem("皮肤库", "浏览和下载玩家皮肤", "face"),
            ToolItem("服务器管理", "管理游戏服务器", "dns"),
            ToolItem("我的通行证", "查看账户通行证信息", "badge"),
        ]

    def login(self, username: str):
        self.username = username
        self.logged_in = True
        config.set("account", "username", username)
        config.set("account", "logged_in", True)

    def logout(self):
        self.username = ""
        self.logged_in = False
        config.set("account", "username", "")
        config.set("account", "logged_in", False)

    def save_navigation(self):
        config.set("navigation", "current_route", self.current_route)
        config.set("navigation", "settings_tab", self.settings_tab)
