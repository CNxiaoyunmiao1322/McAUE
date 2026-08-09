"""全局应用状态 - 管理用户信息、当前视图、主题等。"""

from dataclasses import dataclass, field


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

    # 用户信息
    username: str = ""
    logged_in: bool = False

    # 当前路由
    current_route: str = "/home"

    # 新闻列表（示例数据）
    news: list = field(default_factory=list)

    # 工具列表
    tools: list = field(default_factory=list)

    # 下载页子导航状态
    download_category: str = "mc_install"
    download_expanded: list = field(default_factory=lambda: ["community", "installers"])

    # 设置页当前标签
    settings_tab: str = "launch"

    def __post_init__(self):
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
            ToolItem("种子搜索器", "根据条件筛选合适的种子", "search"),
            ToolItem("坐标转换器", "在不同维度间转换坐标", "explore"),
            ToolItem("附魔计算器", "计算最优附魔方案", "auto_awesome"),
            ToolItem("合成表查询", "查询物品合成配方", "grid_view"),
            ToolItem("NBT 编辑器", "查看和编辑 NBT 数据", "code"),
            ToolItem("皮肤查看器", "预览玩家皮肤", "face"),
        ]

    def login(self, username: str):
        self.username = username
        self.logged_in = True

    def logout(self):
        self.username = ""
        self.logged_in = False
