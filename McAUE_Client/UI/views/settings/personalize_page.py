"""个性化设置页面。"""

import os
import subprocess
import flet as ft

from theme.colors import Colors
from components.animation import SmoothScroll
from state.config import config, _get_config_dir
from ._common import build_section_title, build_setting_row, make_dropdown, make_switch


def build_personalize_page(page, theme_mode, on_set_theme):
    c = Colors.from_page(page)
    pc = config.get("personalize")

    _data_dir = str(_get_config_dir())
    bg_media_dir = os.path.join(_data_dir, "background")
    bg_music_dir = os.path.join(_data_dir, "music")
    has_bg_media = os.path.isdir(bg_media_dir) and len(os.listdir(bg_media_dir)) > 0 if os.path.isdir(bg_media_dir) else False
    has_bg_music = os.path.isdir(bg_music_dir) and len(os.listdir(bg_music_dir)) > 0 if os.path.isdir(bg_music_dir) else False

    def _action_btn(text, icon, on_click=None):
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color=c["on_surface"], size=14),
                    ft.Text(text, size=12, color=c["on_surface"]),
                ],
                spacing=4,
            ),
            padding=ft.Padding(left=12, right=12, top=8, bottom=8),
            border_radius=6,
            bgcolor=c["surface_variant"],
            border=ft.Border.all(1, c["outline"]),
            ink=True,
            on_click=on_click,
        )

    def _open_folder(path):
        os.makedirs(path, exist_ok=True)
        try:
            if os.name == "nt":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

    opacity_slider = ft.Slider(
        min=40, max=100, divisions=60, value=pc.get("opacity", 100),
        label="{value}%",
        active_color=c["primary"], width=180,
    )
    opacity_slider.on_change = lambda e: config.set("personalize", "opacity", int(opacity_slider.value))

    theme_dropdown = make_dropdown(page, theme_mode, [
        ft.dropdown.Option("light", "白天模式"),
        ft.dropdown.Option("dark", "黑夜模式"),
        ft.dropdown.Option("system", "跟随系统"),
    ], width=280)
    theme_dropdown.on_select = lambda e: (on_set_theme(e.control.value) if on_set_theme else None, config.set("theme_mode", None, e.control.value))

    adv_material_switch = make_switch(page, pc.get("advanced_material", False))

    blur_radius_slider = ft.Slider(
        min=0, max=45, divisions=45, value=pc.get("blur_radius", 15),
        label="{value} 像素",
        active_color=c["primary"], width=180,
    )
    blur_radius_slider.on_change = lambda e: config.set("personalize", "blur_radius", int(blur_radius_slider.value))

    blur_method_dd = make_dropdown(page, pc.get("blur_method", "gaussian"), [
        ft.dropdown.Option("gaussian", "高斯模糊"),
        ft.dropdown.Option("box", "方框模糊"),
    ], width=280)
    blur_method_dd.on_select = lambda e: config.set("personalize", "blur_method", e.control.value)

    sample_rate_slider = ft.Slider(
        min=0, max=100, divisions=100, value=pc.get("sample_rate", 80),
        label="{value}%",
        active_color=c["primary"], width=180,
    )
    sample_rate_slider.on_change = lambda e: config.set("personalize", "sample_rate", int(sample_rate_slider.value))

    adv_content = ft.Column(
        controls=[
            build_setting_row(page, "模糊半径", "", blur_radius_slider),
            build_setting_row(page, "模糊方式", "选择模糊算法", blur_method_dd),
            build_setting_row(page, "采样率", "材质采样率", sample_rate_slider),
        ],
        spacing=8,
        visible=pc.get("advanced_material", False),
    )

    def on_adv_material(e):
        adv_content.visible = adv_material_switch.value
        config.set("personalize", "advanced_material", adv_material_switch.value)
        try:
            adv_content.update()
        except Exception:
            pass

    adv_material_switch.on_change = on_adv_material

    font_options = [ft.dropdown.Option("default", "默认")]
    for name in ["Microsoft YaHei", "SimHei", "SimSun", "KaiTi", "FangSong",
                 "Arial", "Calibri", "Consolas", "Times New Roman", "Verdana", "Tahoma", "Segoe UI"]:
        font_options.append(ft.dropdown.Option(name, name))
    font_dd = make_dropdown(page, pc.get("font", "default"), font_options, width=280)
    font_dd.on_select = lambda e: config.set("personalize", "font", e.control.value)

    bg_adapt_dd = make_dropdown(page, pc.get("bg_adapt", "smart"), [
        ft.dropdown.Option("smart", "智能"),
        ft.dropdown.Option("center", "居中"),
        ft.dropdown.Option("fit", "适应"),
        ft.dropdown.Option("stretch", "拉伸"),
        ft.dropdown.Option("tile", "平铺"),
        ft.dropdown.Option("topleft", "居于左上"),
        ft.dropdown.Option("topright", "居于右上"),
        ft.dropdown.Option("bottomleft", "居于左下"),
        ft.dropdown.Option("bottomright", "居于右下"),
    ], width=280)
    bg_adapt_dd.on_select = lambda e: config.set("personalize", "bg_adapt", e.control.value)

    bg_opacity_slider = ft.Slider(
        min=20, max=100, divisions=80, value=pc.get("bg_opacity", 80),
        label="{value}%",
        active_color=c["primary"], width=180,
    )
    bg_opacity_slider.on_change = lambda e: config.set("personalize", "bg_opacity", int(bg_opacity_slider.value))

    bg_blur_slider = ft.Slider(
        min=0, max=45, divisions=45, value=pc.get("bg_blur", 0),
        label="{value} 像素",
        active_color=c["primary"], width=180,
    )
    bg_blur_slider.on_change = lambda e: config.set("personalize", "bg_blur", int(bg_blur_slider.value))

    bg_pause_sw = make_switch(page, pc.get("bg_pause_on_game", False))
    bg_pause_sw.on_change = lambda e: config.set("personalize", "bg_pause_on_game", bg_pause_sw.value)

    color_overlay_sw = make_switch(page, pc.get("color_overlay", False))
    color_overlay_sw.on_change = lambda e: config.set("personalize", "color_overlay", color_overlay_sw.value)

    def _clear_bg_media(e):
        try:
            if os.path.isdir(bg_media_dir):
                import shutil
                shutil.rmtree(bg_media_dir)
        except Exception:
            pass

    bg_buttons_always = ft.Row(
        controls=[
            _action_btn("打开文件夹", ft.Icons.FOLDER_OPEN, lambda e: _open_folder(bg_media_dir)),
            _action_btn("刷新", ft.Icons.REFRESH, lambda e: _open_folder(bg_media_dir)),
        ],
        spacing=8,
    )

    bg_buttons_conditional = ft.Row(
        controls=[
            _action_btn("清空", ft.Icons.DELETE_SWEEP, _clear_bg_media),
        ],
        spacing=8,
        visible=has_bg_media,
    )

    bg_media_conditional = ft.Column(
        controls=[
            build_setting_row(page, "内容自适应方式", "背景内容适配模式", bg_adapt_dd),
            build_setting_row(page, "不透明度", "20% - 100%", bg_opacity_slider),
            build_setting_row(page, "背景模糊", "0 - 45 像素", bg_blur_slider),
            build_setting_row(page, "游戏启动后暂停视频背景", "游戏退出后重新播放", bg_pause_sw),
            build_setting_row(page, "清空背景内容", "", bg_buttons_conditional),
        ],
        spacing=8,
        visible=has_bg_media,
    )

    music_volume_slider = ft.Slider(
        min=0, max=100, divisions=100, value=pc.get("music_volume", 50),
        label="{value}%",
        active_color=c["primary"], width=180,
    )
    music_volume_slider.on_change = lambda e: config.set("personalize", "music_volume", int(music_volume_slider.value))

    def _cfg_switch(key, default):
        sw = make_switch(page, pc.get(key, default))
        sw.on_change = lambda e, k=key: config.set("personalize", k, e.control.value)
        return sw

    music_shuffle_sw = _cfg_switch("music_shuffle", False)
    music_autostart_sw = _cfg_switch("music_autostart", False)
    music_game_play_sw = _cfg_switch("music_play_on_game", False)
    music_game_pause_sw = _cfg_switch("music_pause_on_game", False)
    music_smtc_sw = _cfg_switch("music_smtc", False)

    def on_game_play(e):
        if music_game_play_sw.value:
            music_game_pause_sw.value = False
            config.set("personalize", "music_pause_on_game", False)
            try:
                music_game_pause_sw.update()
            except Exception:
                pass
        config.set("personalize", "music_play_on_game", music_game_play_sw.value)

    def on_game_pause(e):
        if music_game_pause_sw.value:
            music_game_play_sw.value = False
            config.set("personalize", "music_play_on_game", False)
            try:
                music_game_play_sw.update()
            except Exception:
                pass
        config.set("personalize", "music_pause_on_game", music_game_pause_sw.value)

    music_game_play_sw.on_change = on_game_play
    music_game_pause_sw.on_change = on_game_pause

    def _clear_bg_music(e):
        try:
            if os.path.isdir(bg_music_dir):
                import shutil
                shutil.rmtree(bg_music_dir)
        except Exception:
            pass

    music_buttons_always = ft.Row(
        controls=[
            _action_btn("打开文件夹", ft.Icons.FOLDER_OPEN, lambda e: _open_folder(bg_music_dir)),
            _action_btn("刷新", ft.Icons.REFRESH, lambda e: _open_folder(bg_music_dir)),
        ],
        spacing=8,
    )

    music_buttons_conditional = ft.Row(
        controls=[
            _action_btn("清空", ft.Icons.DELETE_SWEEP, _clear_bg_music),
        ],
        spacing=8,
        visible=has_bg_music,
    )

    bg_music_conditional = ft.Column(
        controls=[
            build_setting_row(page, "音量", "0% - 100%", music_volume_slider),
            build_setting_row(page, "随机播放", "", music_shuffle_sw),
            build_setting_row(page, "打开启动器自动开始播放", "", music_autostart_sw),
            build_setting_row(page, "游戏启动后自动播放", "启动后播放，退出后暂停", music_game_play_sw),
            build_setting_row(page, "游戏启动后自动暂停", "启动后暂停，退出后播放", music_game_pause_sw),
            build_setting_row(page, "接入 SMTC 控件", "系统媒体传输控制", music_smtc_sw),
            build_setting_row(page, "清空背景音乐", "", music_buttons_conditional),
        ],
        spacing=8,
        visible=has_bg_music,
    )

    titlebar_radio = ft.RadioGroup(
        value=pc.get("titlebar_style", "default"),
        content=ft.Row(
            controls=[
                ft.Radio(value="none", label="无", active_color=c["primary"]),
                ft.Radio(value="default", label="默认", active_color=c["primary"]),
                ft.Radio(value="text", label="文本", active_color=c["primary"]),
                ft.Radio(value="image", label="图片", active_color=c["primary"]),
            ],
            spacing=20,
        ),
    )

    titlebar_text_field = ft.TextField(
        hint_text="输入标题栏文本",
        width=280, text_size=13,
        border_color=c["outline"], color=c["on_surface"],
        bgcolor=c["surface_variant"], filled=True,
        value=pc.get("titlebar_text", ""),
        visible=(pc.get("titlebar_style", "default") == "text"),
    )
    titlebar_text_field.on_blur = lambda e: config.set("personalize", "titlebar_text", titlebar_text_field.value)

    async def _change_titlebar_image(e):
        picker = ft.FilePicker()
        page.services.append(picker)
        page.update()
        result = await picker.pick_files(
            dialog_title="选择标题栏图片",
            allowed_extensions=["png", "jpg", "jpeg", "bmp", "gif"],
        )
        if result:
            config.set("personalize", "titlebar_image_path", result[0].path)

    clear_img_btn = _action_btn("清空图片", ft.Icons.DELETE)
    titlebar_image_buttons = ft.Row(
        controls=[
            _action_btn("更改图片", ft.Icons.IMAGE, _change_titlebar_image),
            clear_img_btn,
        ],
        spacing=8,
        visible=(pc.get("titlebar_style", "default") == "image"),
    )

    def on_titlebar_change(e):
        val = titlebar_radio.value
        config.set("personalize", "titlebar_style", val)
        titlebar_text_field.visible = (val == "text")
        titlebar_image_buttons.visible = (val == "image")
        try:
            titlebar_text_field.update()
            titlebar_image_buttons.update()
        except Exception:
            pass

    titlebar_radio.on_change = on_titlebar_change

    def on_clear_image(e):
        titlebar_radio.value = "default"
        config.set("personalize", "titlebar_style", "default")
        config.set("personalize", "titlebar_image_path", "")
        titlebar_image_buttons.visible = False
        try:
            titlebar_radio.update()
            titlebar_image_buttons.update()
        except Exception:
            pass

    clear_img_btn.on_click = on_clear_image

    return SmoothScroll(
        page=page,
        controls=[
            build_section_title(page, "个性化", ft.Icons.PALETTE_OUTLINED),

            ft.Text("基础", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "不透明度", "", opacity_slider),
            build_setting_row(page, "主题", "选择白天、黑夜或跟随系统", theme_dropdown),
            build_setting_row(page, "高级材质", "", adv_material_switch),
            adv_content,

            ft.Text("字体", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "启动器字体", "选择启动器界面字体", font_dd),

            ft.Text("背景图片/视频", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "背景内容管理", "", bg_buttons_always),
            bg_media_conditional,
            build_setting_row(page, "叠加彩色背景", "", color_overlay_sw),

            ft.Text("背景音乐", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            build_setting_row(page, "背景音乐管理", "", music_buttons_always),
            bg_music_conditional,

            ft.Text("标题栏", size=14, weight=ft.FontWeight.W_600, color=c["primary"]),
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text("标题栏样式", size=14, weight=ft.FontWeight.W_500, color=c["on_surface"]),
                                titlebar_radio,
                            ],
                            spacing=20,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        titlebar_text_field,
                        titlebar_image_buttons,
                    ],
                    spacing=8,
                ),
                padding=ft.Padding(left=16, right=16, top=12, bottom=12),
                bgcolor=c["surface"],
                border_radius=10,
                border=ft.Border.all(1, c["outline_variant"]),
            ),
        ],
        spacing=8,
        expand=True,
    )
