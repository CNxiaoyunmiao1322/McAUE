"""游戏启动器接口 - 预留游戏启动功能。

实际实现需要：
- Java 运行时管理
- Minecraft 版本隔离/实例管理
- 正版验证/离线验证 token
- 进程创建与参数拼接
- 启动前/后回调
"""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class LaunchResult:
    success: bool
    message: str
    pid: Optional[int] = None


class GameLauncher:
    """游戏启动器接口。"""

    def __init__(self):
        self._on_progress: Optional[Callable[[str, float], None]] = None
        self._on_log: Optional[Callable[[str], None]] = None
        self._on_complete: Optional[Callable[[LaunchResult], None]] = None

    def set_callbacks(
        self,
        on_progress: Callable[[str, float], None] = None,
        on_log: Callable[[str], None] = None,
        on_complete: Callable[[LaunchResult], None] = None,
    ):
        self._on_progress = on_progress
        self._on_log = on_log
        self._on_complete = on_complete

    def launch(
        self,
        version: str,
        java_path: str = "",
        username: str = "",
        auth_token: str = "",
        memory: int = 0,
        extra_args: str = "",
    ) -> LaunchResult:
        """启动游戏。

        Args:
            version: Minecraft 版本号
            java_path: Java 可执行文件路径，空字符串表示自动选择
            username: 用户名
            auth_token: 验证 token
            memory: 分配内存 (MB)，0 表示自动
            extra_args: 额外启动参数

        Returns:
            LaunchResult: 启动结果
        """
        if self._on_progress:
            self._on_progress("验证游戏文件...", 0.1)
        if self._on_progress:
            self._on_progress("加载游戏资源...", 0.3)
        if self._on_progress:
            self._on_progress("准备启动参数...", 0.6)
        if self._on_log:
            self._on_log("[接口预留] 游戏启动功能尚未实现")
        result = LaunchResult(
            success=False,
            message="游戏启动功能尚未实现，需要完成核心启动模块",
        )
        if self._on_complete:
            self._on_complete(result)
        return result

    def is_game_running(self) -> bool:
        """检查游戏是否正在运行。"""
        return False

    def kill_game(self) -> bool:
        """终止游戏进程。"""
        return False


launcher = GameLauncher()
