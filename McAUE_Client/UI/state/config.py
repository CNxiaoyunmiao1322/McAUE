"""配置持久化系统 - JSON 存取所有应用设置。

使用单例 ConfigManager 管理配置文件，支持自动保存和分类加载。
配置文件位置：项目根目录下 McAUE/config.json
"""

import json
import os
from pathlib import Path


def _get_config_dir() -> Path:
    project_root = Path(__file__).resolve().parent.parent.parent
    config_dir = project_root / "McAUE"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


CONFIG_FILE = _get_config_dir() / "config.json"


DEFAULT_CONFIG = {
    "window": {
        "width": 1100,
        "height": 700,
    },
    "theme_mode": "dark",

    "launch": {
        "instance_isolation": "all",
        "window_title": "",
        "custom_info": "",
        "launcher_visibility": "keep",
        "process_priority": "normal",
        "window_size_mode": "default",
        "custom_width": "",
        "custom_height": "",
        "auth_method": "device",
        "ip_protocol": "default",
        "renderer": "default",
        "jvm_args_head": "-Djava.awt.headless=true",
        "game_args_tail": "--width 1280 --height 720",
        "pre_exec_cmd": "",
        "disable_java_wrapper": False,
        "disable_legacyfix": False,
        "force_high_perf_gpu": False,
        "use_java_exe": True,
        "disable_lwjgl_unsafe": False,
        "disable_crash_analysis": False,
        "memory_auto": True,
        "memory_value": 4,
    },

    "java": {
        "selected": "auto",
        "installations": [],
    },

    "manage": {
        "file_dl_source": "mirror_prefer",
        "version_list_source": "mirror_prefer",
        "max_threads": 8,
        "speed_limit": 0,
        "auto_select_new": True,
        "upgrade_authlib": True,
        "community_dl_source": "mirror_prefer",
        "filename_format": "modname_bracket",
        "mod_manage_style": "translated",
        "quick_download": "ask",
        "hide_quilt": False,
        "auto_install_deps": True,
        "auto_game_language": True,
        "detect_clipboard": False,
    },

    "personalize": {
        "opacity": 100,
        "advanced_material": False,
        "blur_radius": 15,
        "blur_method": "gaussian",
        "sample_rate": 80,
        "font": "default",
        "bg_adapt": "smart",
        "bg_opacity": 80,
        "bg_blur": 0,
        "bg_pause_on_game": False,
        "color_overlay": False,
        "music_volume": 50,
        "music_shuffle": False,
        "music_autostart": False,
        "music_play_on_game": False,
        "music_pause_on_game": False,
        "music_smtc": False,
        "titlebar_style": "default",
        "titlebar_text": "",
    },

    "language": {
        "interface": "简体中文",
        "region": "zh_cn",
    },

    "misc": {
        "max_fps": 60,
        "log_lines": 500,
        "disable_hw_accel": False,
        "telemetry": False,
        "doh": False,
        "proxy_mode": "none",
        "proxy_addr": "",
        "proxy_user": "",
        "proxy_pass": "",
        "anim_speed": 10,
        "no_copy_on_download": False,
        "debug_mode": False,
    },

    "update": {
        "channel": "stable",
        "beta_update_notify": False,
        "stable_update_notify": True,
        "auto_update": True,
    },

    "account": {
        "username": "",
        "logged_in": False,
        "login_type": "",
    },

    "navigation": {
        "current_route": "/home",
        "settings_tab": "launch",
    },

    "multiplayer": {
        "servers": [],
    },

    "game": {
        "selected_version": "1.21.4",
    },

    "version_settings": {},

    "tools": {
        "skins": [],
        "servers": [],
    },
}


class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data = None
            cls._instance._load()
        return cls._instance

    def _load(self):
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._data = self._deep_merge(dict(DEFAULT_CONFIG), loaded)
            else:
                self._data = dict(DEFAULT_CONFIG)
        except Exception:
            self._data = dict(DEFAULT_CONFIG)

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        for key, val in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(val, dict):
                base[key] = ConfigManager._deep_merge(base[key], val)
            else:
                base[key] = val
        return base

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def get(self, section: str, key: str = None, default=None):
        section_data = self._data.get(section, {})
        if key is None:
            return section_data
        return section_data.get(key, default)

    def set(self, section: str, key: str, value):
        if key is None:
            self._data[section] = value
        else:
            if section not in self._data or not isinstance(self._data.get(section), dict):
                self._data[section] = {}
            self._data[section][key] = value
        self.save()

    def set_section(self, section: str, data: dict):
        self._data[section] = data
        self.save()

    def get_all(self) -> dict:
        return self._data

    def export_config(self, path: str) -> bool:
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def import_config(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as f:
                imported = json.load(f)
            self._data = self._deep_merge(dict(DEFAULT_CONFIG), imported)
            self.save()
            return True
        except Exception:
            return False

    def clear_cache(self) -> bool:
        try:
            cache_dir = _get_config_dir() / "cache"
            if cache_dir.exists():
                import shutil
                shutil.rmtree(cache_dir)
            cache_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False


config = ConfigManager()
