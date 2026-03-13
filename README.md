# 三国霸业 (Three Kingdoms)

一款使用 Python + Pygame 开发的策略类三国游戏，画面精美，支持简体中文。

## 游戏介绍

《三国霸业》是一款经典的策略游戏，玩家可以扮演三国时期的各路诸侯，通过内政管理、军事征战、外交谋略来统一华夏大地。

### 游戏特色

- **经典策略玩法**：内政、军事、外交系统一应俱全
- **精美画面**：古典风格UI设计，支持1280x720高清分辨率
- **简体中文**：完整的中文界面和文字支持
- **跨平台**：支持 Windows、Linux、macOS 三大操作系统
- **日志系统**：完善的日志记录，方便问题排查

## 系统要求

- **操作系统**: Windows 10/11, Ubuntu 20.04+, macOS 12+
- **Python**: 3.10 或更高版本
- **显卡**: 支持 OpenGL 的显卡

## 安装与运行

### 方法一：直接运行（推荐开发者）

1. 克隆仓库
```bash
git clone git@github.com:ganecheng-ai/three-kingdoms-k25.git
cd three-kingdoms-k25
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行游戏
```bash
cd src
python main.py
```

### 方法二：下载发行版（推荐普通用户）

1. 访问 [Releases](https://github.com/ganecheng-ai/three-kingdoms-k25/releases) 页面
2. 下载对应平台的版本
3. 解压后运行可执行文件

## 游戏界面

### 主菜单
- 新游戏：开始新的霸业征程
- 载入游戏：读取已保存的游戏进度
- 游戏设置：调整音频、显示等选项
- 退出游戏

### 大地图
- 显示三国时期的中国地图
- 各势力城池分布
- 支持鼠标拖动浏览地图
- 点击城池进入城市管理

### 城市界面
- 查看城池信息（人口、农业、商业等）
- 管理城中武将
- 执行内政操作（开发农业、发展商业、搜索人才等）
- 征兵、出征等军事操作

### 战斗界面
- 回合制战斗系统
- 支持移动、攻击、计策等指令
- 阵型调整、武将技能

## 开发计划

查看 [plan.md](plan.md) 了解详细的开发规划。

### 版本历史

- **v0.3.0** - 核心机制版本
  - 实现武将系统（15名三国武将，包含属性、技能、忠诚度）
  - 实现城池系统（25座城池，包含农业、商业、城防、人口等属性）
  - 实现势力系统（魏、蜀、吴等7个势力）
  - 完整内政系统（开发农业、发展商业、加强城防、搜索人才、征兵）
  - 回合制游戏循环，月度资源收支计算
  - 存档/读档功能

- **v0.2.0** - UI系统版本
  - 主菜单界面
  - 大地图界面（可拖动、点击城池）
  - 城池管理界面
  - 战斗场景基础框架

- **v0.1.0** - 初始版本
  - 项目框架搭建
  - 基础UI系统
  - 日志系统

## 技术栈

- **Python 3.10+**: 编程语言
- **Pygame 2.5+**: 游戏开发框架
- **GitHub Actions**: 持续集成和自动发布

## 项目结构

```
three-kingdoms-k25/
├── src/              # 源代码
│   ├── main.py       # 游戏入口
│   ├── core/         # 核心逻辑
│   ├── ui/           # UI组件
│   ├── scenes/       # 游戏场景
│   └── utils/        # 工具函数
├── tests/            # 测试代码
├── .github/          # GitHub配置
├── requirements.txt  # 依赖清单
├── plan.md           # 开发计划
├── README.md         # 项目说明
└── LICENSE           # 许可证
```

## 日志文件

游戏运行日志保存在程序运行目录的 `logs/` 文件夹中，文件名为 `three_kingdoms_YYYYMMDD.log`。

## 贡献指南

欢迎提交 Issue 和 Pull Request。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

- GitHub Issues: [https://github.com/ganecheng-ai/three-kingdoms-k25/issues](https://github.com/ganecheng-ai/three-kingdoms-k25/issues)

---

**注意**: 本项目仅供学习和娱乐使用。
