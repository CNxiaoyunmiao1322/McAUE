"""Java 管理器接口 - 预留 Java 运行时检测与管理功能。

实际实现需要：
- 系统注册表/文件系统扫描
- Java 版本检测 (java -version)
- 架构检测 (32/64 bit)
- 路径验证
- 自动选择合适 Java 版本
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class JavaInstallation:
    id: str
    type: str  # JDK, JRE
    version: str
    arch: str  # 64 Bit, 32 Bit
    vendor: str
    path: str
    is_valid: bool = True


class JavaManager:
    """Java 运行时管理器接口。"""

    SEARCH_PATHS = [
        r"C:\Program Files\Java\*",
        r"C:\Program Files\Eclipse Adoptium\*",
        r"C:\Program Files\Zulu\*",
        r"C:\Program Files\Microsoft\jdk-*",
        r"C:\Program Files (x86)\Java\*",
    ]

    def search(self) -> list[JavaInstallation]:
        """搜索系统中已安装的 Java。

        Returns:
            list[JavaInstallation]: 找到的 Java 安装列表
        """
        return []

    def add_manual(self, path: str) -> Optional[JavaInstallation]:
        """手动添加 Java 安装路径。

        Args:
            path: java.exe 或 Java 安装目录路径

        Returns:
            Optional[JavaInstallation]: 检测到的 Java 信息，失败返回 None
        """
        return None

    def validate(self, path: str) -> bool:
        """验证 Java 路径是否有效。

        Args:
            path: Java 安装路径

        Returns:
            bool: 是否有效
        """
        return False

    def select_for_version(self, mc_version: str) -> Optional[JavaInstallation]:
        """根据 Minecraft 版本自动选择合适的 Java。

        Args:
            mc_version: Minecraft 版本号

        Returns:
            Optional[JavaInstallation]: 推荐的 Java 安装
        """
        return None

    def get_installations(self) -> list[JavaInstallation]:
        """获取已保存的 Java 安装列表。"""
        return []


java_manager = JavaManager()
