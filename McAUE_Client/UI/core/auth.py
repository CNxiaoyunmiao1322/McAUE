"""认证接口 - 预留正版/离线/第三方验证功能。

实际实现需要：
- Microsoft OAuth 2.0 设备代码流/PKCE
- Xbox Live 认证
- XSTS Token 获取
- Minecraft Token 获取
- 离线模式 UUID 生成
- 第三方 Authlib-Injector 验证
- Token 持久化与刷新
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthResult:
    success: bool
    message: str
    username: str = ""
    uuid: str = ""
    access_token: str = ""
    account_type: str = ""  # microsoft, offline, thirdparty


class AuthManager:
    """认证管理器接口。"""

    def login_offline(self, username: str) -> AuthResult:
        """离线登录。

        Args:
            username: 用户名

        Returns:
            AuthResult: 认证结果
        """
        return AuthResult(
            success=False,
            message="离线登录功能尚未实现，需要完成认证模块",
        )

    def login_microsoft(self, method: str = "device") -> AuthResult:
        """微软正版登录。

        Args:
            method: 验证方式 (device, pkce)

        Returns:
            AuthResult: 认证结果
        """
        return AuthResult(
            success=False,
            message="微软正版登录功能尚未实现，需要完成认证模块",
        )

    def login_thirdparty(
        self,
        username: str,
        password: str,
        auth_server: str,
        server_name: str = "",
    ) -> AuthResult:
        """第三方 Authlib-Injector 登录。

        Args:
            username: 用户名/邮箱
            password: 密码
            auth_server: 验证服务器地址
            server_name: 服务器名称

        Returns:
            AuthResult: 认证结果
        """
        return AuthResult(
            success=False,
            message="第三方登录功能尚未实现，需要完成认证模块",
        )

    def refresh_token(self, account_type: str, refresh_token: str) -> AuthResult:
        """刷新 Token。

        Args:
            account_type: 账户类型
            refresh_token: 刷新令牌

        Returns:
            AuthResult: 新的认证结果
        """
        return AuthResult(
            success=False,
            message="Token 刷新功能尚未实现",
        )

    def logout(self):
        """退出登录，清除本地凭据。"""
        pass

    def get_stored_account(self) -> Optional[AuthResult]:
        """获取已存储的登录信息。"""
        return None


auth = AuthManager()
