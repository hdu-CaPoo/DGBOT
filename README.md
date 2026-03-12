# DGBOT (DGLab 郊狼 x LLM 赛博调教机器人) 🕹️

基于 **NoneBot2** 和 **DeepSeek 大语言模型**，结合 **DGLab（郊狼）虚拟触觉设备** 构建的实体交互式 BDSM 角色扮演项目。
赋予了大模型“4i 强势大姐姐”的人设，通过 QQ 聊天指令直接与远端或本地的物理设备进行即时震动/波形反馈，并能实时感知用户的硬件强度状态，根据玩家的反应动态做出惩罚或安抚（加高电击或降低电击强度）。

## ✨ 核心特性 (Features)

- 🧠 **AI 硬件控制感知**：DeepSeek 原生 JSON 格式输出，精准解析大模型指令。代码层具备极强的鲁棒性（已修复大模型偶发输出小数或异常字符导致硬件闪退的问题）。
- ⚡ **本地/远程穿透**：通过 WebSocket 直连 DGLab 手机 APP，终端自动打印二维码，扫码瞬间映射信道。
- 🌊 **智能连续波形下发**：提供预设波形 (`呼吸`, `潮汐`, `连击`, `按捏渐强`, `挑逗1`, `挑逗2`, `高频过载`)。由于郊狼App具备队列限制，系统底层的异步池会自动循环下发所选波形，实现**持续不断的电击**直到收到下一个指令。
- 🛡️ **安全隔离与鉴权**：系统深度绑定 `.env`，屏蔽一切闲杂人等，只响应配置好的超级主人 (SUPERUSERS) 账号。
- 🐍 **现代化框架兼容**：全面兼容 Python 3.13 与最新的底层异步并发限制，使用更稳定的 `aiohttp` 替代极易引发版本冲突的老版 `websockets` 驱动器。

---

## ⚙️ 环境依赖

* **运行环境:** `Python >= 3.13` (支持 Windows 与 Linux 云服务器)
* **包管理器:** 推荐使用极速构建工具 `uv`
* **服务端框架:** `nonebot2` (配置使用 FastAPI + aiohttp 底层驱动)
* **硬件交互:** `pydglab-ws` 1.1.0

---

## 🛠️ 安装与部署指南

### 1. 拉取代码 & 安装依赖
本项目采用标准的 `pyproject.toml` 现代依赖管理。建议使用 `uv` 一键安装所有锁定的版本环境：
```bash
# 自动创建虚拟环境并同步所有的依赖到 .venv 下
uv sync
```
*(注：如果云端环境遇到网络或权限问题，确保已使用上述命令将库安装在项目私有的 `.venv` 下)*

### 2. 配置环境变量
在项目根目录下，将 `.env.example` 复制并重命名为 `.env`，按照以下说明填入你的专属配置：
```dotenv
HOST=0.0.0.0
PORT=64000
COMMAND_START=["", "/"]
DRIVER=~fastapi+~aiohttp          # Python 3.13 强烈建议使用 aiohttp 驱动，不要改动
ONEBOT_ACCESS_TOKEN="你的鉴权密码"  # 与 NapCat / Go-CQHTTP 侧设置的密码保持完全一致
ONEBOT_WS_URLS=["ws://<你的云服务器或本地QQ端IP>:3001/"]
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxx"
SUPERUSERS=["你的QQ号"]             # 数组格式，允许控制该机器人的QQ号
```

### 3. 指定 IP
打开 `src/plugins/master_bot.py`，定位到 `start_dglab()` 函数：
```python
# 将这里的 IP 替换为你跑机器人的电脑当前的局域网 IPv4 地址 (例如 192.168.1.x) 或者云服务器上
# 这是为了让同一个 WiFi 下的手机 App 能直接扫码连接上
YOUR_LOCAL_IP = "192.168.144.102"
```

---

## 🚀 启动与运行测试

### 💻 方式一：Windows 本地运行
无需担心编码问题，直接激活环境运行：
```powershell
.venv\Scripts\activate
python bot.py
# 或使用 uv： uv run python bot.py
```

### ☁️ 方式二：Linux 云服务器部署运行（⚠️ 关键警告）
如果在 Linux 系统下部署遭遇 `UnicodeEncodeError: 'ascii' codec can't encode characters` 错误，这是因为云服务器的默认控制台未开启 UTF-8 支持，无法打印大模型的中文回复。
请使用以下携带环境变量的命令启动代码：
```bash
PYTHONIOENCODING=utf-8 LANG=C.UTF-8 uv run python bot.py
```
*(建议写进开机启动脚本或 tmux 会话中)*

---

### 🎮 开始游玩
1. **扫码配对**：程序启动成功后，控制台会用 ASCII 码打印出一个巨大的二维码。打开你手机上关联设备的 **DGLab APP**，选择扫码连接。
2. **硬件绑定**：手机端通过 WebSocket 连接后，控制台会显示 `DGLab App 连接成功！`。
3. **QQ 调教**：用你设定在 `SUPERUSERS` 里的 QQ 账号，直接向机器人发起私聊对话。机器人将自行向大模型传递你的话与郊狼当下的强度通道数据，并下发动作到物理设备！

---

## 📝 常见排错 (FAQ)

- **为什么我在云端启动报 `ModuleNotFoundError: No module named 'nonebot'`？**
  这是由于你使用了全局的 `python3 bot.py`。请使用 `uv run python bot.py` 或先 `source .venv/bin/activate`。
- **连接到 QQ 端报 `TypeError: BaseEventLoop.create_connection() got an unexpected keyword...`？**
  Python 3.13 移除了旧 `websockets` 的部分参数支持。请确保 `.env` 中的 `DRIVER` 已经设为了 `~fastapi+~aiohttp`。
- **大模型聊着聊着设备闪退了怎么回事？**
  已经在最新版修复了。原因是此前大模型产生了幻象返回了小数型的强度（如 `10.5`）。目前代码已添加了 `int(float(strength))` 的兜底策略。

---

> ⚠️ **警告与免责声明 (Disclaimer)** 
> 游玩或使用本软件造成的任何身体不适或相关风险与本开源开发者无关，游玩请必须设定并牢记你个人的**安全红灯词**，必要时直接扯掉贴片。请遵守所在地区的网络法律法规。
