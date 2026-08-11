"""日志查看器接口 - 预留日志查看功能。

实际实现需要：
- 日志文件读取
- 日志级别过滤
- 时间范围筛选
- 日志文件管理（列表、导出、清理）
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogEntry:
    timestamp: str
    level: str  # INFO, WARN, ERROR, DEBUG
    message: str


@dataclass
class LogFileInfo:
    filename: str
    filepath: str
    timestamp: str
    size: int  # bytes
    is_current: bool = False


class LogManager:
    """日志管理器接口。"""

    def get_logs(self, limit: int = 500, level: str = None) -> list[LogEntry]:
        """获取日志条目。"""
        return []

    def get_log_file_path(self) -> Optional[str]:
        """获取当前日志文件路径。"""
        return None

    def get_log_dir(self) -> str:
        """获取日志目录路径。"""
        from state.config import _get_config_dir
        log_dir = _get_config_dir() / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        return str(log_dir)

    def get_log_files(self) -> list[LogFileInfo]:
        """获取所有日志文件列表。"""
        return []

    def clear_logs(self) -> bool:
        """清除历史日志。"""
        return False

    def export_log(self, filepath: str, dest: str) -> bool:
        """导出单个日志文件。"""
        return False

    def export_all_logs(self, dest_dir: str) -> bool:
        """导出全部日志文件。"""
        return False


log_manager = LogManager()
