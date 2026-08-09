# McAUE

> 基于 PySide6 的 Minecraft 游戏启动器，采用客户端-服务端架构，具备无边框美化界面、多线程下载引擎与完整的设置管理体系。

McAUE 是一个使用 Python + Qt（PySide6）构建的桌面端 Minecraft 启动器项目。当前处于早期开发阶段：客户端 UI 框架（含动画、主题、内存管理、设置持久化）已基本完成，多线程下载引擎已实现但尚未接入界面，游戏启动与版本选择等核心业务逻辑为待实现状态，服务端为占位空文件。

- **许可证**：GPL-3.0
- **开发语言**：Python 3.14（100%）
- **目标平台**：Windows（依赖 Windows API 与 DWM 窗口特效）
- **开发环境**：Visual Studio + Python Tools (PTVS)

---

## 目录

- [项目整体架构](#项目整体架构)
- [目录结构](#目录结构)
- [客户端架构详解](#客户端架构详解)
- [下载引擎详解](#下载引擎详解)
- [依赖关系](#依赖关系)
- [项目运行方式](#项目运行方式)
- [配置文件说明](#配置文件说明)
- [开发指南](#开发指南)
- [项目状态与路线图](#项目状态与路线图)

---

## 项目整体架构

McAUE 采用**客户端-服务端（Client-Server）**架构，通过 Visual Studio 解决方案（`McAUE.slnx`）统一管理两个 Python 项目。

```
┌─────────────────────────────────────────────────────────┐
│                    McAUE.slnx (解决方案)                  │
│                                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐    │
│  │   McAUE_Client      │    │   McAUE_Server      │    │
│  │   (客户端 / GUI)     │    │   (服务端 / 占位)    │    │
│  │                     │    │                     │    │
│  │  • McAUE_Client.py  │    │  • McAUE_Server.py  │    │
│  │    (主入口+业务逻辑) │    │    (空占位文件)      │    │
│  │  • Downloader/      │    │                     │    │
│  │    (多线程下载引擎)  │    │                     │    │
│  │  • UI/              │    │                     │    │
│  │    (界面与样式)      │    │                     │    │
│  │  • settings.json    │    │                     │    │
│  │    (配置持久化)      │    │                     │    │
│  └─────────────────────┘    └─────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### 架构层次

| 层次 | 组件 | 说明 |
|------|------|------|
| **表现层** | `UI/untitled.ui` + QSS 样式 | Qt Designer 设计的界面文件，运行时通过 `QUiLoader` 动态加载 |
| **控制层** | `MainWindow` 类（`McAUE_Client.py`） | 继承 `QMainWindow`，承载全部 UI 交互与业务逻辑 |
| **服务层** | `Downloader/` 下载引擎 | 多线程、断点续传、SHA256 校验的下载模块 |
| **持久化层** | `settings.json` | 本地 JSON 配置文件，设置变更即时写入 |
| **服务端** | `McAUE_Server.py` | 当前为空占位文件，预留服务端能力 |

### 客户端与下载引擎的协作

目前下载引擎（`DownloadEngine`）作为独立模块实现，尚未在客户端主代码中导入调用。预期工作流程为：客户端界面触发下载任务 → 调用 `DownloadEngine` 执行多线程下载 → 通过回调函数向 UI 报告进度。

---

## 目录结构

```
McAUE/
├── McAUE.slnx                      # Visual Studio 解决方案文件（链接两个项目）
├── README.md                       # 项目说明文档
├── LICENSE.txt                     # GPL-3.0 许可证
├── .gitattributes                  # Git 属性配置
├── .gitignore                      # Git 忽略规则（Visual Studio 模板）
├── .claudiaideconfig               # ClaudiaIDE 扩展配置（VS 编辑器背景图）
│
├── McAUE_Client/                   # ===== 客户端项目 =====
│   ├── McAUE_Client.py             # 主入口（765 行）：MainWindow 类 + 全部业务逻辑
│   ├── McAUE_Client.pyproj         # VS Python 项目文件（Python 3.14 / X64）
│   ├── requirements.txt            # Python 依赖清单
│   ├── settings.json               # 运行时配置（自动生成与更新）
│   │
│   ├── Downloader/                 # 多线程下载引擎模块
│   │   ├── __init__.py             # 包导出（导出 DownloadEngine）
│   │   ├── engine.py               # 下载引擎核心（306 行）
│   │   ├── task.py                 # DownloadTask 数据类
│   │   └── verify.py               # SHA256 文件校验
│   │
│   └── UI/                         # 界面资源
│       ├── untitled.ui             # Qt Designer 界面文件（919 行）
│       ├── style.qss               # 亮色主题样式表
│       └── style_dark.qss          # 暗色主题样式表
│
└── McAUE_Server/                   # ===== 服务端项目 =====
    ├── McAUE_Server.py             # 占位空文件（待实现）
    └── McAUE_Server.pyproj         # VS Python 项目文件（Python 3.14 / X64）
```

---

## 客户端架构详解

客户端核心位于 `McAUE_Client.py` 的 `MainWindow` 类中，采用"UI 动态加载 + 逻辑集中管理"的设计模式。

### 启动流程

```
main()
  │
  ├─ QApplication 初始化
  ├─ MainWindow() 构造
  │    ├─ _load_ui()              # 通过 QUiLoader 加载 untitled.ui
  │    │    └─ 将所有具名控件挂到 self.<objectName>
  │    ├─ _setup_frameless()      # 无边框窗口 + DWM 阴影 + 主题加载
  │    ├─ _setup_login_way()      # 登录方式按钮组（互斥）
  │    ├─ _setup_menu()           # 底部菜单按钮组 + 页面切换
  │    ├─ _setup_setting_page()   # 设置页子页面切换 + 控件联动
  │    ├─ _setup_memory_page()    # 内存分配页绘图与逻辑
  │    ├─ _load_settings()        # 从 settings.json 还原配置
  │    ├─ _update_memory_display()# 刷新内存显示
  │    └─ _connect_window_buttons()# 绑定标题栏与启动页按钮
  └─ window.show() → app.exec()
```

### 核心功能模块

#### 1. 无边框窗口与主题系统

- 通过 `Qt.FramelessWindowHint` 实现无边框，`WA_TranslucentBackground` 实现透明背景
- 使用 `qframelesswindow.WindowEffect` 恢复 DWM 窗口阴影与最大化/最小化动画
- 标题栏区域支持鼠标拖动移动窗口（通过事件过滤器实现）
- 窗口尺寸锁定（`setFixedSize`），禁止缩放
- **亮/暗主题**自动跟随系统配色（`QApplication.styleHints().colorScheme()`），监听系统主题切换实时响应
- 圆角半径 12px，蓝粉配色方案

#### 2. 页面导航

底部菜单使用 `QButtonGroup`（互斥）控制 `QStackedWidget` 页面切换，切换时带有 250ms 的位移动画（`QPropertyAnimation` + `OutCubic` 缓动曲线）：

| 菜单按钮 | 目标页面 |
|----------|----------|
| `tab_launch_button`（启动） | `launch` |
| `tab_download_button`（下载） | `page_2` |
| `tab_tool_button`（工具） | `page_2` |
| `tab_settings_button`（设置） | `setting` |
| `tab_more_button`（更多） | `page_2` |

#### 3. 登录方式

三种互斥登录方式按钮：
- `login_official_button`（正版登录）
- `login_offline_button`（离线登录）
- `login_thirdparty_button`（第三方登录）

#### 4. 设置页面（三段子页面）

设置页左侧选项按钮控制 `setting_content_area`（嵌套 `QStackedWidget`）的子页面切换，带有自下而上的滑入动画：

| 选项按钮 | 子页面 | 功能 |
|----------|--------|------|
| `setting_launch_option_button` | `launch_option_setting` | 启动选项（JVM 参数、游戏参数、启动前命令、Java 选择等） |
| `setting_mem_button` | `mem_option` | 内存分配（自动/自定义模式、滑块、可视化条） |
| `setting_pro_option_button` | `pro_setting` | 高级设置（版本隔离、游戏标题、自定义信息、启动器可见性等） |

#### 5. 内存管理

- **系统内存检测**：通过 `ctypes` 调用 Windows API `kernel32.GlobalMemoryStatusEx` 获取总物理内存与可用内存
- **分配模式**：
  - 自动模式（`mem_auto`）：固定分配 1GB（`_get_auto_game_memory_gb`，真实规则待实现）
  - 自定义模式（`mem_custom`）：通过滑块按可用内存百分比分配
- **可视化绘制**：`mem_display` 控件通过 `QPainter` 绘制三段式内存条（已用/游戏分配/剩余），实时刷新

#### 6. 设置持久化

- 所有设置控件的变化即时触发 `_save_settings()`，写入同目录 `settings.json`
- 启动时通过 `_load_settings()` 还原配置（加载期间设置 `_loading_settings` 标志避免循环触发）

#### 7. 动画系统

- **按钮 hover 动画**：登录/菜单按钮 hover 时通过 `QVariantAnimation` 平滑过渡颜色（100ms）
- **滑块 handle 动画**：内存滑块 hover 时 handle 颜色平滑过渡
- **页面切换动画**：主页面与设置子页面的位移滑入动画
- 主题切换时自动停止所有进行中的动画并重置颜色

#### 8. 业务逻辑（待实现）

以下方法目前为占位实现，标注 `TODO`：
- `on_launch_game_clicked()` — 启动游戏
- `on_choose_version_clicked()` — 选择版本
- `_get_auto_game_memory_gb()` — 自动内存分配真实规则

---

## 下载引擎详解

`Downloader/` 模块是一个独立的多线程下载引擎，当前尚未接入客户端 UI。

### DownloadEngine 核心特性

| 特性 | 说明 |
|------|------|
| **多线程下载** | 最多 512 线程（默认 32），按文件大小自动分块 |
| **断点续传** | 通过 `.partN` 分块文件实现，支持中断后恢复 |
| **Range 请求** | 使用 HTTP `Range` 头分块下载（需服务器支持 206 响应） |
| **SHA256 校验** | 下载完成后校验文件完整性，不匹配则清理重下 |
| **暂停/恢复/取消** | 基于 `threading.Event` 实现线程安全控制 |
| **重试机制** | 默认重试 3 次 |
| **进度回调** | 每秒报告下载量、总量、速度、百分比、阶段 |
| **CDN 支持** | 可配置 CDN 列表 |
| **流式回退** | 服务器不支持 Range 时回退为单线程流式下载 |

### 工作流程

```
start()
  │
  ├─ 扫描已存在的 .part 文件，恢复进度计数
  ├─ 启动进度报告线程（每秒回调一次）
  │
  └─ 逐任务下载：
       ├─ _download(task)
       │    ├─ _get_size()           # HEAD 请求获取文件大小
       │    ├─ _download_file()      # 分块多线程下载
       │    │    ├─ _split_parts()   # 按 size/threads 分块
       │    │    ├─ ThreadPoolExecutor 并行下载各分块
       │    │    │    └─ worker: Range 请求 + 断点续写 .part 文件
       │    │    └─ 合并所有 .part 为完整文件
       │    └─ SHA256 校验（可选）
       └─ 回调最终状态
```

### 模块组成

| 文件 | 内容 |
|------|------|
| `engine.py` | `DownloadEngine` 类，下载调度核心 |
| `task.py` | `DownloadTask` 数据类（`url`、`save`、`sha256`） |
| `verify.py` | `sha256_file()` 函数，分块读取计算哈希 |
| `__init__.py` | 包导出，`from Downloader import DownloadEngine` |

### 使用示例

```python
from Downloader import DownloadEngine

engine = DownloadEngine(threads=32, retry=3, verify=True)
engine.set_callback(lambda info: print(f"{info['percent']:.1f}%  {info['speed']/1024/1024:.1f} MB/s"))
engine.add_task("https://example.com/file.jar", "./downloads/file.jar", sha256="abc123...")
engine.start()
```

---

## 依赖关系

### Python 依赖（requirements.txt）

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| `PySide6` | 6.11.1 | Qt for Python，GUI 框架 |
| `PySide6_Essentials` | 6.11.1 | PySide6 核心组件 |
| `PySide6_Addons` | 6.11.1 | PySide6 附加组件 |
| `shiboken6` | 6.11.1 | PySide6 的 C++ 绑定生成器 |
| `PySideSix-Frameless-Window` | 0.8.2 | 无边框窗口与 Windows DWM 特效（`WindowEffect`） |
| `pywin32` | 312 | Windows API 访问 |
| `pip` | 26.1.2 | 包管理器 |

### 隐含依赖（未列入 requirements.txt）

| 依赖包 | 用途 | 说明 |
|--------|------|------|
| `requests` | HTTP 请求 | 下载引擎 `engine.py` 使用，需额外安装 |

### 依赖关系图

```
McAUE_Client.py
  ├─ PySide6 (QtCore, QtGui, QtUiTools, QtWidgets)   ← UI 框架
  ├─ qframelesswindow (WindowEffect)                  ← 无边框窗口特效
  └─ ctypes (windll.kernel32)                         ← Windows 内存 API（标准库）

Downloader/engine.py
  ├─ requests                                         ← HTTP 下载（需安装）
  ├─ concurrent.futures (ThreadPoolExecutor)          ← 多线程（标准库）
  ├─ threading                                        ← 线程控制（标准库）
  └─ .task / .verify                                  ← 包内模块
```

### 运行时环境要求

- **Python**：3.14（64 位），项目配置中指定
- **操作系统**：Windows（客户端使用 `ctypes.windll` 调用 Windows API，`pywin32` 与 DWM 特效均为 Windows 专属）
- **.NET / Visual Studio**：开发时使用 Visual Studio + PTVS，运行时不依赖

---

## 项目运行方式

### 环境准备

```bash
# 1. 克隆仓库
git clone https://github.com/CNxiaoyunmiao1322/McAUE.git
cd McAUE/McAUE_Client

# 2. 创建虚拟环境（推荐 Python 3.14）
python -m venv AUEenv_C
# Windows 激活
AUEenv_C\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
pip install requests          # 下载引擎依赖（未列入 requirements.txt）
```

### 运行客户端

```bash
cd McAUE_Client
python McAUE_Client.py
```

程序入口为 `McAUE_Client.py` 的 `main()` 函数，执行后会：
1. 初始化 `QApplication`
2. 创建 `MainWindow`（加载 UI、应用主题、还原设置）
3. 显示窗口并进入 Qt 事件循环

### 使用 Visual Studio 运行

1. 用 Visual Studio 打开 `McAUE.slnx` 解决方案文件
2. 解决方案资源管理器中右键 `McAUE_Client` 项目 → 设为启动项目
3. 按 `F5`（调试）或 `Ctrl+F5`（运行）启动

> 项目文件中配置了虚拟环境 `AUEenv_C`（客户端）和 `AUEenv_S`（服务端），启动文件分别为 `McAUE_Client.py` 和 `McAUE_Server.py`。

### 运行服务端

服务端 `McAUE_Server.py` 当前为空占位文件，暂无可执行内容。

### 注意事项

- 客户端依赖 Windows API，**仅可在 Windows 上运行**
- UI 文件 `UI/untitled.ui` 必须与主程序同级，运行时动态加载
- 首次运行会在 `McAUE_Client/` 目录下自动生成或更新 `settings.json`
- 若 UI 文件缺失，程序会弹出"界面加载失败"错误对话框

---

## 配置文件说明

### settings.json

位于 `McAUE_Client/` 目录下，由客户端自动读写，存储所有启动器设置：

| 字段 | 类型 | 说明 |
|------|------|------|
| `mem_mode` | string | 内存分配模式：`"auto"`（自动）或 `"custom"`（自定义） |
| `mem_value` | int | 自定义模式下内存滑块百分比（0-100） |
| `jvm_para` | string | JVM 启动参数 |
| `game_para` | string | 游戏参数 |
| `cmd_before_launch` | string | 启动游戏前执行的命令 |
| `java_list` | string | 选择的 Java 路径 |
| `ban_jlw` | bool | 是否禁用 Java Loader Wrapper |
| `ban_lwjgl` | bool | 是否禁用 LWJGL |
| `version_isolate` | int | 版本隔离模式索引（0=关闭） |
| `game_title` | string | 自定义游戏窗口标题 |
| `setting_custom_info` | string | 自定义信息（默认 `"PCL"`） |
| `launcher_visble` | int | 启动器可见性模式索引（0=始终显示） |

### .claudiaideconfig

ClaudiaIDE（Visual Studio 编辑器背景图扩展）的配置文件，仅影响开发环境的编辑器外观，与项目运行无关。

---

## 开发指南

### 开发环境搭建

1. 安装 **Visual Studio 2022**（含 Python 开发工作负载）
2. 安装 **ClaudiaIDE 扩展**（可选，编辑器美化）
3. 打开 `McAUE.slnx`，Visual Studio 会自动识别两个 Python 项目
4. 为每个项目创建虚拟环境（`AUEenv_C` / `AUEenv_S`），Python 3.14 (64-bit)

### 修改界面

- 使用 **Qt Designer** 打开 `McAUE_Client/UI/untitled.ui` 进行可视化编辑
- 界面中每个控件的 `objectName` 可在代码中通过 `self.<objectName>` 直接访问
- 样式修改：编辑 `style.qss`（亮色）和 `style_dark.qss`（暗色）

### 代码扩展点

客户端主代码中以 `TODO` 标注的待实现业务逻辑：

```python
# McAUE_Client.py

def on_launch_game_clicked(self) -> None:
    """点击"启动游戏"。"""
    # TODO: 启动游戏业务逻辑
    print("启动游戏（待实现）：", self.username_lineEdit.text())

def on_choose_version_clicked(self) -> None:
    """点击"选择版本"。"""
    # TODO: 选择版本业务逻辑

def _get_auto_game_memory_gb(self) -> float:
    """自动分配时的游戏内存（GB）。"""
    # TODO: 自动分配真实规则
    return 1.0
```

### 接入下载引擎

下载引擎已实现但未接入 UI，接入示例：

```python
from Downloader import DownloadEngine

def start_download(self):
    self.engine = DownloadEngine(threads=32, retry=3, verify=True)
    self.engine.set_callback(self._on_download_progress)
    self.engine.add_task(url, save_path, sha256=expected_hash)
    # 在子线程中启动，避免阻塞 UI
    import threading
    threading.Thread(target=self.engine.start, daemon=True).start()
```

### 编码规范

- 代码注释与文档字符串使用中文
- UI 控件通过 `objectName` 访问，命名采用 `snake_case`
- 设置变更通过信号即时持久化，加载时用 `_loading_settings` 防止循环触发

---

## 项目状态与路线图

### 当前状态

| 模块 | 状态 | 说明 |
|------|------|------|
| 客户端 UI 框架 | ✅ 已完成 | 无边框窗口、主题、动画、页面导航 |
| 设置管理 | ✅ 已完成 | 三段设置页、持久化、内存管理 |
| 下载引擎 | ⚠️ 已实现未接入 | 多线程下载引擎完整，但未在客户端调用 |
| 游戏启动 | ❌ 待实现 | `on_launch_game_clicked` 为占位 |
| 版本选择 | ❌ 待实现 | `on_choose_version_clicked` 为占位 |
| 自动内存分配 | ❌ 待实现 | 固定返回 1GB |
| 服务端 | ❌ 占位 | `McAUE_Server.py` 为空文件 |

### 开发历程

项目始于 2026 年 8 月 7 日，共 23 次提交，2 位贡献者（[CNxiaoyunmiao1322](https://github.com/CNxiaoyunmiao1322)、[NmEV](https://github.com/NmEV)）：

1. **基础搭建**（08-07）：项目文件、许可证、Git 配置
2. **窗口实现**（08-08）：基本窗口、UI 优化、动画、颜色、设置页面
3. **重构优化**（08-09）：主入口迁移、设置页优化、文件重命名
4. **下载模块**（08-09）：添加多线程下载引擎

---

## 许可证

本项目基于 [GPL-3.0](LICENSE.txt) 许可证开源。任何人可自由使用、修改和分发，但衍生作品须同样以 GPL-3.0 许可证开源。
