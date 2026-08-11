"""下载管理器接口 - 预留版本下载和社区资源下载功能。

实际实现需要：
- Mojang 版本清单 API 调用
- 文件下载与校验 (SHA1)
- 多线程并发下载
- 速度限制
- 进度回调
- 镜像源切换
"""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class VersionInfo:
    id: str
    type: str  # release, snapshot, old_beta, old_alpha
    release_time: str
    url: str
    installed: bool = False


@dataclass
class DownloadResult:
    success: bool
    message: str
    downloaded_bytes: int = 0
    total_bytes: int = 0


class DownloadManager:
    """下载管理器接口。"""

    def __init__(self):
        self._on_progress: Optional[Callable[[str, float, int, int], None]] = None
        self._on_complete: Optional[Callable[[DownloadResult], None]] = None
        self._cancelled = False

    def set_callbacks(
        self,
        on_progress: Callable[[str, float, int, int], None] = None,
        on_complete: Callable[[DownloadResult], None] = None,
    ):
        self._on_progress = on_progress
        self._on_complete = on_complete

    def get_version_list(self, source: str = "mirror_prefer") -> list[VersionInfo]:
        """获取 Minecraft 版本列表。

        Args:
            source: 下载源 (mirror_prefer, official_fallback, official_prefer)

        Returns:
            list[VersionInfo]: 版本信息列表
        """
        return []

    def get_installed_versions(self) -> list[str]:
        """获取已安装的版本列表。"""
        return []

    def install_version(
        self,
        version: str,
        max_threads: int = 8,
        speed_limit: float = 0,
        source: str = "mirror_prefer",
    ) -> DownloadResult:
        """安装 Minecraft 版本。

        Args:
            version: 版本号
            max_threads: 最大线程数
            speed_limit: 速度限制 (MiB/s)，0 = 不限速
            source: 下载源

        Returns:
            DownloadResult: 下载结果
        """
        if self._on_progress:
            self._on_progress(version, 0.0, 0, 0)
        result = DownloadResult(
            success=False,
            message="版本下载功能尚未实现，需要完成下载管理模块",
        )
        if self._on_complete:
            self._on_complete(result)
        return result

    def download_jar(
        self,
        version: str,
        max_threads: int = 8,
        speed_limit: float = 0,
        source: str = "mirror_prefer",
    ) -> DownloadResult:
        """下载 Minecraft .jar 文件。

        Args:
            version: 版本号
            max_threads: 最大线程数
            speed_limit: 速度限制 (MiB/s)，0 = 不限速
            source: 下载源

        Returns:
            DownloadResult: 下载结果
        """
        if self._on_progress:
            self._on_progress(version, 0.0, 0, 0)
        result = DownloadResult(
            success=False,
            message=".jar 下载功能尚未实现，需要完成下载管理模块",
        )
        if self._on_complete:
            self._on_complete(result)
        return result

    def download_mod(self, mod_id: str, source: str = "mirror_prefer") -> DownloadResult:
        """下载模组。"""
        result = DownloadResult(
            success=False,
            message="模组下载功能尚未实现",
        )
        if self._on_complete:
            self._on_complete(result)
        return result

    def download_modpack(self, pack_id: str, source: str = "mirror_prefer") -> DownloadResult:
        """下载整合包。"""
        result = DownloadResult(
            success=False,
            message="整合包下载功能尚未实现",
        )
        if self._on_complete:
            self._on_complete(result)
        return result

    def cancel(self):
        """取消当前下载。"""
        self._cancelled = True


downloader = DownloadManager()
