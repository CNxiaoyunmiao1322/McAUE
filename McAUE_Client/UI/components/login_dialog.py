"""登录弹窗组件 - 支持离线、正版、第三方登录。"""

import flet as ft

from theme.colors import Colors


def _make_field(page, label, hint, icon, password=False) -> ft.TextField:
    c = Colors.from_page(page)
    return ft.TextField(
        label=label,
        hint_text=hint,
        prefix_icon=icon,
        password=password,
        can_reveal_password=password,
        border_color=c["outline"],
        focused_border_color=c["primary"],
        color=c["on_surface"],
        bgcolor=c["surface_variant"],
        filled=True,
        width=380,
        text_size=13,
    )


def build_login_dialog(page: ft.Page, state, on_login=None, on_cancel=None, initial_state=None) -> ft.AlertDialog:
    """构建登录弹窗。on_login(username) 在登录成功时调用。on_cancel() 在取消时调用。"""
    c = Colors.from_page(page)

    # 登录方式状态
    login_type = {"value": initial_state["login_type"]} if initial_state else {"value": "offline"}

    # ===== 各方式字段 =====
    # 离线
    offline_name = _make_field(page, "用户名", "输入游戏内显示名称", ft.Icons.PERSON_OUTLINE)
    if initial_state and initial_state.get("offline_name"):
        offline_name.value = initial_state["offline_name"]

    # 正版
    official_email = _make_field(page, "邮箱", "Mojang / Microsoft 账户邮箱", ft.Icons.EMAIL_OUTLINED)
    official_pass = _make_field(page, "密码", "账户密码", ft.Icons.LOCK_OUTLINE, password=True)
    if initial_state:
        if initial_state.get("official_email"):
            official_email.value = initial_state["official_email"]
        if initial_state.get("official_pass"):
            official_pass.value = initial_state["official_pass"]

    # 第三方
    third_name = _make_field(page, "用户名", "第三方账户用户名", ft.Icons.PERSON_OUTLINE)
    third_pass = _make_field(page, "密码", "第三方账户密码", ft.Icons.LOCK_OUTLINE, password=True)
    third_auth = _make_field(page, "验证服务器", "https://auth.example.com/yggdrasil", ft.Icons.DNS_OUTLINED)
    third_reg = _make_field(page, "服务器注册链接", "https://example.com/register", ft.Icons.APP_REGISTRATION)
    third_sname = _make_field(page, "服务器名称", "自定义服务器名称", ft.Icons.LABEL_OUTLINE)
    if initial_state:
        if initial_state.get("third_name"):
            third_name.value = initial_state["third_name"]
        if initial_state.get("third_pass"):
            third_pass.value = initial_state["third_pass"]
        if initial_state.get("third_auth"):
            third_auth.value = initial_state["third_auth"]
        if initial_state.get("third_reg"):
            third_reg.value = initial_state["third_reg"]
        if initial_state.get("third_sname"):
            third_sname.value = initial_state["third_sname"]

    # 第三方面板（高级设置始终展开）
    third_panel = ft.Column(
        controls=[
            third_name,
            third_pass,
            ft.Container(height=4),
            third_auth,
            third_reg,
            third_sname,
        ],
        spacing=10,
        visible=(login_type["value"] == "thirdparty"),
    )

    # 离线面板
    offline_panel = ft.Column(
        controls=[offline_name],
        spacing=10,
        visible=(login_type["value"] == "offline"),
    )

    # 正版面板
    official_panel = ft.Column(
        controls=[official_email, official_pass],
        spacing=10,
        visible=(login_type["value"] == "official"),
    )

    # 存储字段引用，供外部读取当前输入状态
    page._login_fields = {
        "login_type": login_type,
        "offline_name": offline_name,
        "official_email": official_email,
        "official_pass": official_pass,
        "third_name": third_name,
        "third_pass": third_pass,
        "third_auth": third_auth,
        "third_reg": third_reg,
        "third_sname": third_sname,
    }

    # ===== 类型选择按钮 =====
    type_configs = [
        ("offline", "离线", ft.Icons.PERSON_OUTLINE),
        ("official", "正版", ft.Icons.VERIFIED_USER_OUTLINED),
        ("thirdparty", "第三方", ft.Icons.HUB_OUTLINED),
    ]

    def select_type(key):
        login_type["value"] = key
        for k, btn_info in type_buttons.items():
            active = k == key
            color = "#FFFFFF" if active else c["on_surface_variant"]
            btn_info["container"].bgcolor = c["primary"] if active else c["surface_variant"]
            btn_info["icon"].color = color
            btn_info["text"].color = color
        offline_panel.visible = key == "offline"
        official_panel.visible = key == "official"
        third_panel.visible = key == "thirdparty"
        page.update()

    type_buttons = {}
    type_btns_row = ft.Row(spacing=8)

    for key, label, icon in type_configs:
        active = login_type["value"] == key
        color = "#FFFFFF" if active else c["on_surface_variant"]
        ic = ft.Icon(icon, color=color, size=16)
        txt = ft.Text(label, size=13, color=color, weight=ft.FontWeight.W_500)
        btn = ft.Container(
            content=ft.Row(
                controls=[ic, txt],
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding(left=12, right=12, top=10, bottom=10),
            border_radius=8,
            bgcolor=c["primary"] if active else c["surface_variant"],
            ink=True,
            expand=True,
            on_click=lambda e, k=key: select_type(k),
        )
        type_buttons[key] = {"container": btn, "icon": ic, "text": txt}
        type_btns_row.controls.append(btn)

    # ===== 登录按钮 =====
    def do_login(e):
        t = login_type["value"]
        if t == "offline":
            name = offline_name.value.strip() if offline_name.value else ""
            if not name:
                offline_name.error_text = "请输入用户名"
                page.update()
                return
            username = name
        elif t == "official":
            email = official_email.value.strip() if official_email.value else ""
            if not email:
                official_email.error_text = "请输入邮箱"
                page.update()
                return
            username = email.split("@")[0]
        else:
            name = third_name.value.strip() if third_name.value else ""
            if not name:
                third_name.error_text = "请输入用户名"
                page.update()
                return
            auth = third_auth.value.strip() if third_auth.value else ""
            if not auth:
                third_auth.error_text = "请输入验证服务器地址"
                page.update()
                return
            reg = third_reg.value.strip() if third_reg.value else ""
            if not reg:
                third_reg.error_text = "请输入服务器注册链接"
                page.update()
                return
            sname = third_sname.value.strip() if third_sname.value else ""
            if not sname:
                third_sname.error_text = "请输入服务器名称"
                page.update()
                return
            username = name

        state.login(username)
        page.pop_dialog()
        if on_login:
            on_login(username)

    login_btn = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOGIN, color="#FFFFFF", size=18),
                ft.Text("登录", size=14, weight=ft.FontWeight.W_600, color="#FFFFFF"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        ),
        width=380,
        height=44,
        border_radius=10,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=[c["gradient_start"], c["gradient_end"]],
        ),
        ink=True,
        on_click=do_login,
        alignment=ft.Alignment.CENTER,
    )

    cancel_btn = ft.TextButton(
        "取消",
        on_click=lambda _: (page.pop_dialog(), on_cancel() if on_cancel else None),
    )

    content = ft.Column(
        controls=[
            type_btns_row,
            ft.Container(height=4),
            offline_panel,
            official_panel,
            third_panel,
            ft.Container(height=4),
            login_btn,
        ],
        spacing=10,
        width=400,
        tight=True,
        scroll=ft.ScrollMode.AUTO,
    )

    dialog = ft.AlertDialog(
        title=ft.Row(
            controls=[
                ft.Icon(ft.Icons.LOCK_PERSON_OUTLINED, color=c["primary"], size=24),
                ft.Text("登录", size=20, weight=ft.FontWeight.BOLD, color=c["on_surface"]),
            ],
            spacing=10,
        ),
        content=content,
        actions=[cancel_btn],
        modal=True,
    )

    return dialog
