<p align="center">
  <a href="https://github.com/gitstq/AgentMemory-CLI">
    <img src="https://img.shields.io/badge/version-v1.0.0-blue" alt="Version">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.9+-green" alt="Python 3.9+">
  </a>
  <a href="https://github.com/gitstq/AgentMemory-CLI/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
  </a>
  <a href="https://github.com/gitstq/AgentMemory-CLI/actions">
    <img src="https://img.shields.io/badge/tests-97%20passed-success" alt="Tests">
  </a>
</p>

<p align="center">
  <b>简体中文</b> | <a href="#繁體中文">繁體中文</a> | <a href="#english">English</a>
</p>

---

# 简体中文

<p align="center">
  <b>AgentMemory-CLI</b> — 轻量级终端 AI Agent 有状态记忆管理引擎
</p>

---

## 🎉 项目介绍

在构建 AI Agent 应用时，**会话记忆管理**始终是一个令人头疼的问题：LLM 本身是无状态的，每次对话都需要开发者自行维护上下文。现有的方案要么依赖重量级框架（LangChain、MemGPT），要么缺乏对多会话隔离、自动摘要、上下文窗口裁剪等核心需求的支持。

**AgentMemory-CLI** 正是为了解决这个痛点而生。

它是一个**零外部依赖核心**的轻量级记忆管理引擎，专为终端 AI Agent 场景设计。无论是快速原型验证还是生产环境集成，都能即插即用。你只需要一行 `pip install`，就能获得完整的会话管理、消息存储、全文搜索、自动摘要和上下文窗口管理能力。

### 🎯 核心价值

- **极简主义**：核心代码仅依赖 Python 标准库，零外部依赖即可运行
- **开箱即用**：完整的 CLI 工具 + Python API，5 分钟完成集成
- **灵活可扩展**：三种可插拔存储后端，按需选择
- **生产就绪**：97 个单元测试全部通过，代码质量有保障

### 🔥 差异化亮点

| 特性 | AgentMemory-CLI | LangChain Memory | MemGPT |
|------|:-:|:-:|:-:|
| 零外部依赖核心 | ✅ | ❌ | ❌ |
| 多会话隔离 | ✅ | 部分 | ✅ |
| 自动摘要（无需LLM） | ✅ | ❌ | ❌ |
| 上下文窗口管理 | ✅ | 部分 | ✅ |
| FTS5 全文搜索 | ✅ | ❌ | ❌ |
| 多格式导出 | ✅ | ❌ | ❌ |
| TUI 仪表盘 | ✅ | ❌ | ❌ |
| 安装体积 | < 100KB | > 50MB | > 100MB |

---

## ✨ 核心特性

### 🧱 零外部依赖核心
纯 Python 标准库实现（`sqlite3`、`json`、`dataclasses`、`argparse`），**无需安装任何第三方包**即可使用全部核心功能。极致轻量，部署无忧。

### 💾 三种可插拔存储后端
- **SQLite** — 内置 **FTS5 全文搜索引擎**，支持高效的中文/英文关键词检索，适合生产环境
- **JSON 文件** — 原子写入机制，数据以人类可读格式持久化，适合调试和快速原型
- **内存存储** — 零延迟读写，适合测试和临时场景

通过 `--backend` 参数一行切换，代码无需任何修改。

### 🏷️ 多会话隔离管理
支持创建、切换、搜索、标签化管理多个独立会话。每个会话的消息、摘要完全隔离，互不干扰。适合同时管理多个 Agent 实例或多轮独立对话。

### 📝 自动摘要引擎
基于规则的**提取式摘要**算法，当消息数量超过阈值时自动触发压缩。**无需调用任何 LLM API**，零成本、零延迟、完全离线可用。摘要结果自动融入上下文窗口，确保历史信息不丢失。

### 🪟 上下文窗口管理
智能拼接**最近 N 条消息 + 历史摘要**，自动适配各类 LLM 的上下文长度限制。让你的 Agent 始终拥有"完整记忆"，同时不会超出 Token 预算。

### 📤 多格式导出
一键将会话数据导出为 **JSON / Markdown / CSV** 三种格式，方便数据分析、报告生成或与其他系统集成。

### 🖥️ TUI 交互仪表盘
基于 **Rich** 库打造的终端可视化界面，实时展示会话状态、消息统计和存储信息。在终端中也能拥有直观的数据概览。

### ⌨️ 完整 CLI
提供 `session`、`msg`、`context`、`export`、`summary`、`dashboard` 六大子命令，覆盖记忆管理的全生命周期。

### ✅ 97 个单元测试全部通过
核心模块覆盖率达到生产级标准，每次提交都经过完整测试验证。

---

## 🚀 快速开始

### 环境要求

- **Python** >= 3.9（支持 3.9 / 3.10 / 3.11 / 3.12）
- **操作系统**：Windows / macOS / Linux
- **可选依赖**：`rich >= 13.0.0`（用于 TUI 仪表盘）

### 安装

```bash
# 从 PyPI 安装（推荐）
pip install .

# 或从源码安装
git clone https://github.com/gitstq/AgentMemory-CLI.git
cd AgentMemory-CLI
pip install -e .

# 安装 TUI 可选依赖
pip install ".[tui]"
```

### 30 秒快速体验

```bash
# 1. 创建一个会话
agentmemory session create "my-first-chat"

# 2. 添加几条消息
agentmemory msg add user "你好，我想了解一下这个项目"
agentmemory msg add assistant "你好！AgentMemory-CLI 是一个轻量级的 AI Agent 记忆管理引擎"

# 3. 查看上下文窗口
agentmemory context --limit 5

# 4. 搜索历史消息
agentmemory msg search "项目"

# 5. 导出为 Markdown
agentmemory export markdown --output chat.md
```

---

## 📖 详细使用指南

### CLI 完整命令参考

#### 🔧 全局选项

```bash
# 查看版本
agentmemory --version

# 指定存储后端（sqlite / json / memory）
agentmemory --backend sqlite <command>

# 指定存储路径
agentmemory --backend json --store-path ./my_data <command>
```

#### 📂 会话管理（session）

```bash
# 创建会话（支持标签）
agentmemory session create "customer-support" --tags support v1

# 列出所有会话
agentmemory session list

# 切换活跃会话
agentmemory session switch <session-id>

# 删除会话
agentmemory session delete <session-id>
```

#### 💬 消息操作（msg）

```bash
# 添加消息（角色：user / assistant / system）
agentmemory msg add user "Hello, how are you?"
agentmemory msg add assistant "I'm doing well, thanks!"
agentmemory msg add system "You are a helpful assistant."

# 列出消息
agentmemory msg list                          # 当前会话全部消息
agentmemory msg list --limit 10               # 最近 10 条
agentmemory msg list --role user              # 仅用户消息
agentmemory msg list --session <session-id>   # 指定会话

# 搜索消息
agentmemory msg search "keyword"
agentmemory msg search "订单" --limit 5

# 删除消息
agentmemory msg delete <message-id>
```

#### 🪟 上下文与摘要

```bash
# 获取上下文窗口（最近 N 条消息 + 历史摘要）
agentmemory context --limit 5

# 查看当前会话摘要
agentmemory summary
```

#### 📤 导出

```bash
# 导出为 JSON
agentmemory export json --output chat.json

# 导出为 Markdown
agentmemory export markdown --output chat.md

# 导出为 CSV
agentmemory export csv --output chat.csv

# 导出指定会话
agentmemory export json --session <session-id> --output data.json

# 导出到标准输出（不指定 --output）
agentmemory export markdown
```

#### 🖥️ TUI 仪表盘

```bash
# 启动交互式仪表盘（需要安装 rich）
agentmemory dashboard
```

### Python API 示例

```python
from agentmemory import MemoryStore
from agentmemory.storage import SQLiteBackend

# 创建记忆存储（指定 SQLite 后端）
store = MemoryStore(backend=SQLiteBackend("./my_agent.db"))

# 创建会话（支持标签）
session = store.sessions.create("customer-support", tags=["support", "v1"])

# 添加消息
store.add_message(session.id, role="user", content="I need help with my order #12345")
store.add_message(session.id, role="assistant", content="I'd be happy to help! Let me look into that for you.")

# 获取上下文窗口（最近 5 条消息 + 自动摘要）
context = store.get_context_window(session.id, limit=5)
print(f"Summary: {context['summary']}")
for msg in context['messages']:
    print(f"[{msg.role}] {msg.content}")

# 搜索历史消息
results = store.search_messages("order", session_id=session.id)
for msg in results:
    print(f"Found: {msg.content[:80]}...")

# 导出会话数据
from agentmemory.export import Exporter
exporter = Exporter(store)
exporter.export_markdown("./export.md", session_id=session.id)
exporter.export_json("./export.json", session_id=session.id)
exporter.export_csv("./export.csv", session_id=session.id)

# 关闭存储连接
store.close()
```

### 典型使用场景

#### 场景一：CLI 聊天助手记忆管理

```bash
# 为每个对话主题创建独立会话
agentmemory --backend sqlite session create "技术讨论" --tags tech
agentmemory --backend sqlite session create "产品规划" --tags product

# 在会话中记录对话
agentmemory msg add user "我们讨论一下微服务架构的选型"
agentmemory msg add assistant "好的，目前主流方案有..."

# 切换到另一个会话
agentmemory session switch <product-session-id>

# 随时回顾历史上下文
agentmemory context --limit 10
```

#### 场景二：Python 集成到自有 Agent

```python
from agentmemory import MemoryStore
from agentmemory.storage import SQLiteBackend

store = MemoryStore(backend=SQLiteBackend("./agent.db"))

def chat_with_llm(user_input: str, session_id: str):
    # 保存用户消息
    store.add_message(session_id, role="user", content=user_input)

    # 获取上下文窗口发送给 LLM
    context = store.get_context_window(session_id, limit=10)

    # 构建 prompt...
    # 调用 LLM API...
    llm_response = "LLM 的回复内容"

    # 保存助手回复
    store.add_message(session_id, role="assistant", content=llm_response)
    return llm_response
```

---

## 💡 设计思路与迭代规划

### 技术选型原因

| 决策 | 原因 |
|------|------|
| 纯标准库核心 | 最大化降低依赖风险，确保在任何 Python 环境中都能运行 |
| SQLite + FTS5 | 嵌入式数据库零运维，FTS5 提供专业级全文搜索能力 |
| JSON 文件后端 | 人类可读，方便调试和版本控制，原子写入保证数据安全 |
| 提取式摘要 | 零成本、零延迟、完全离线，不依赖任何外部 API |
| argparse CLI | 标准库自带，无需额外依赖，兼容所有 Python 环境 |
| Rich TUI | Python 生态中最成熟的终端 UI 库，渲染效果出色 |

### 架构设计理念

```
┌─────────────────────────────────────────┐
│              CLI / Python API           │
├─────────────────────────────────────────┤
│            MemoryStore (核心层)          │
│  ┌───────────┬──────────┬────────────┐  │
│  │  Session  │  Message │  Summary   │  │
│  │  Manager  │  Store   │  Engine    │  │
│  └───────────┴──────────┴────────────┘  │
├─────────────────────────────────────────┤
│        Storage Backend (存储层)          │
│  ┌───────────┬──────────┬────────────┐  │
│  │  SQLite   │   JSON   │   Memory   │  │
│  │  (FTS5)   │  (Atomic)│  (In-Mem)  │  │
│  └───────────┴──────────┴────────────┘  │
├─────────────────────────────────────────┤
│        Export / TUI (扩展层)             │
└─────────────────────────────────────────┘
```

- **分层解耦**：核心层、存储层、扩展层职责清晰，可独立替换
- **接口抽象**：所有存储后端实现统一接口，切换零成本
- **渐进增强**：核心功能零依赖，TUI 等增强功能按需安装

### 后续迭代计划

- [ ] **向量存储后端** — 支持 Embedding + 向量相似度搜索
- [ ] **LLM 摘要引擎** — 可选接入 OpenAI / 本地模型生成摘要
- [ ] **会话导入** — 支持从 JSON / Markdown 文件导入历史会话
- [ ] **Web UI** — 基于 FastAPI + WebSocket 的浏览器端管理界面
- [ ] **插件系统** — 支持自定义存储后端、摘要策略、导出格式
- [ ] **多用户支持** — 增加用户维度，支持多用户隔离

---

## 📦 安装与部署

### pip 安装（推荐）

```bash
pip install .
```

### 从源码安装

```bash
git clone https://github.com/gitstq/AgentMemory-CLI.git
cd AgentMemory-CLI
pip install -e .
```

### 可选依赖

```bash
# TUI 仪表盘（需要 rich 库）
pip install ".[tui]"

# 或手动安装
pip install rich>=13.0.0
```

### 验证安装

```bash
agentmemory --version
# 输出: agentmemory 1.0.0
```

---

## 🤝 贡献指南

我们欢迎并感谢所有形式的贡献！无论是提交 Bug、改进文档还是贡献代码。

### 提交 PR

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feature/your-feature-name`
3. 确保所有测试通过：`python -m pytest tests/`
4. 提交变更：`git commit -m "feat: 描述你的改动"`
5. 推送分支：`git push origin feature/your-feature-name`
6. 提交 **Pull Request**

### Commit 规范

请使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 新增向量存储后端
fix: 修复 JSON 后端并发写入问题
docs: 更新 API 使用文档
test: 增加摘要引擎边界测试
refactor: 重构存储层接口抽象
```

### 提交 Issue

- 使用清晰的标题描述问题
- 附上复现步骤和期望行为
- 标注相关标签（bug / feature / question）

---

## 📄 开源协议

本项目基于 [MIT License](https://opensource.org/licenses/MIT) 开源。

```
MIT License

Copyright (c) 2024 AgentMemory Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq/AgentMemory-CLI">AgentMemory Team</a>
</p>

---
---

<a id="繁體中文"></a>

<p align="center">
  <a href="#簡體中文">簡體中文</a> | <b>繁體中文</b> | <a href="#english">English</a>
</p>

---

# 繁體中文

<p align="center">
  <b>AgentMemory-CLI</b> — 輕量級終端 AI Agent 有狀態記憶管理引擎
</p>

---

## 🎉 專案介紹

在構建 AI Agent 應用時，**會話記憶管理**始終是一個令人頭痛的問題：LLM 本身是無狀態的，每次對話都需要開發者自行維護上下文。現有的方案要麼依賴重量級框架（LangChain、MemGPT），要麼缺乏對多會話隔離、自動摘要、上下文視窗裁剪等核心需求的支援。

**AgentMemory-CLI** 正是為了解決這個痛點而生。

它是一個**零外部依賴核心**的輕量級記憶管理引擎，專為終端 AI Agent 場景設計。無論是快速原型驗證還是生產環境整合，都能即插即用。你只需要一行 `pip install`，就能獲得完整的會話管理、訊息儲存、全文搜尋、自動摘要和上下文視窗管理能力。

### 🎯 核心價值

- **極簡主義**：核心程式碼僅依賴 Python 標準庫，零外部依賴即可運行
- **開箱即用**：完整的 CLI 工具 + Python API，5 分鐘完成整合
- **靈活可擴展**：三種可插拔儲存後端，按需選擇
- **生產就緒**：97 個單元測試全部通過，程式碼品質有保障

### 🔥 差異化亮點

| 特性 | AgentMemory-CLI | LangChain Memory | MemGPT |
|------|:-:|:-:|:-:|
| 零外部依賴核心 | ✅ | ❌ | ❌ |
| 多會話隔離 | ✅ | 部分 | ✅ |
| 自動摘要（無需LLM） | ✅ | ❌ | ❌ |
| 上下文視窗管理 | ✅ | 部分 | ✅ |
| FTS5 全文搜尋 | ✅ | ❌ | ❌ |
| 多格式匯出 | ✅ | ❌ | ❌ |
| TUI 儀表板 | ✅ | ❌ | ❌ |
| 安裝體積 | < 100KB | > 50MB | > 100MB |

---

## ✨ 核心特性

### 🧱 零外部依賴核心
純 Python 標準庫實作（`sqlite3`、`json`、`dataclasses`、`argparse`），**無需安裝任何第三方套件**即可使用全部核心功能。極致輕量，部署無憂。

### 💾 三種可插拔儲存後端
- **SQLite** — 內建 **FTS5 全文搜尋引擎**，支援高效的中英文關鍵字檢索，適合生產環境
- **JSON 檔案** — 原子寫入機制，資料以人類可讀格式持久化，適合除錯和快速原型
- **記憶體儲存** — 零延遲讀寫，適合測試和臨時場景

透過 `--backend` 參數一行切換，程式碼無需任何修改。

### 🏷️ 多會話隔離管理
支援建立、切換、搜尋、標籤化管理多個獨立會話。每個會話的訊息、摘要完全隔離，互不干擾。適合同時管理多個 Agent 實例或多輪獨立對話。

### 📝 自動摘要引擎
基於規則的**提取式摘要**演算法，當訊息數量超過閾值時自動觸發壓縮。**無需呼叫任何 LLM API**，零成本、零延遲、完全離線可用。摘要結果自動融入上下文視窗，確保歷史資訊不丟失。

### 🪟 上下文視窗管理
智慧拼接**最近 N 條訊息 + 歷史摘要**，自動適配各類 LLM 的上下文長度限制。讓你的 Agent 始終擁有「完整記憶」，同時不會超出 Token 預算。

### 📤 多格式匯出
一鍵將會話資料匯出為 **JSON / Markdown / CSV** 三種格式，方便資料分析、報告生成或與其他系統整合。

### 🖥️ TUI 互動儀表板
基於 **Rich** 函式庫打造的終端視覺化介面，即時展示會話狀態、訊息統計和儲存資訊。在終端中也能擁有直觀的資料概覽。

### ⌨️ 完整 CLI
提供 `session`、`msg`、`context`、`export`、`summary`、`dashboard` 六大子命令，覆蓋記憶管理的全生命週期。

### ✅ 97 個單元測試全部通過
核心模組覆蓋率達到生產級標準，每次提交都經過完整測試驗證。

---

## 🚀 快速開始

### 環境需求

- **Python** >= 3.9（支援 3.9 / 3.10 / 3.11 / 3.12）
- **作業系統**：Windows / macOS / Linux
- **可選依賴**：`rich >= 13.0.0`（用於 TUI 儀表板）

### 安裝

```bash
# 從 PyPI 安裝（推薦）
pip install .

# 或從原始碼安裝
git clone https://github.com/gitstq/AgentMemory-CLI.git
cd AgentMemory-CLI
pip install -e .

# 安裝 TUI 可選依賴
pip install ".[tui]"
```

### 30 秒快速體驗

```bash
# 1. 建立一個會話
agentmemory session create "my-first-chat"

# 2. 新增幾條訊息
agentmemory msg add user "你好，我想了解一下這個專案"
agentmemory msg add assistant "你好！AgentMemory-CLI 是一個輕量級的 AI Agent 記憶管理引擎"

# 3. 查看上下文視窗
agentmemory context --limit 5

# 4. 搜尋歷史訊息
agentmemory msg search "專案"

# 5. 匯出為 Markdown
agentmemory export markdown --output chat.md
```

---

## 📖 詳細使用指南

### CLI 完整命令參考

#### 🔧 全域選項

```bash
# 查看版本
agentmemory --version

# 指定儲存後端（sqlite / json / memory）
agentmemory --backend sqlite <command>

# 指定儲存路徑
agentmemory --backend json --store-path ./my_data <command>
```

#### 📂 會話管理（session）

```bash
# 建立會話（支援標籤）
agentmemory session create "customer-support" --tags support v1

# 列出所有會話
agentmemory session list

# 切換活躍會話
agentmemory session switch <session-id>

# 刪除會話
agentmemory session delete <session-id>
```

#### 💬 訊息操作（msg）

```bash
# 新增訊息（角色：user / assistant / system）
agentmemory msg add user "Hello, how are you?"
agentmemory msg add assistant "I'm doing well, thanks!"
agentmemory msg add system "You are a helpful assistant."

# 列出訊息
agentmemory msg list                          # 當前會話全部訊息
agentmemory msg list --limit 10               # 最近 10 條
agentmemory msg list --role user              # 僅使用者訊息
agentmemory msg list --session <session-id>   # 指定會話

# 搜尋訊息
agentmemory msg search "keyword"
agentmemory msg search "訂單" --limit 5

# 刪除訊息
agentmemory msg delete <message-id>
```

#### 🪟 上下文與摘要

```bash
# 取得上下文視窗（最近 N 條訊息 + 歷史摘要）
agentmemory context --limit 5

# 查看當前會話摘要
agentmemory summary
```

#### 📤 匯出

```bash
# 匯出為 JSON
agentmemory export json --output chat.json

# 匯出為 Markdown
agentmemory export markdown --output chat.md

# 匯出為 CSV
agentmemory export csv --output chat.csv

# 匯出指定會話
agentmemory export json --session <session-id> --output data.json

# 匯出到標準輸出（不指定 --output）
agentmemory export markdown
```

#### 🖥️ TUI 儀表板

```bash
# 啟動互動式儀表板（需要安裝 rich）
agentmemory dashboard
```

### Python API 範例

```python
from agentmemory import MemoryStore
from agentmemory.storage import SQLiteBackend

# 建立記憶儲存（指定 SQLite 後端）
store = MemoryStore(backend=SQLiteBackend("./my_agent.db"))

# 建立會話（支援標籤）
session = store.sessions.create("customer-support", tags=["support", "v1"])

# 新增訊息
store.add_message(session.id, role="user", content="I need help with my order #12345")
store.add_message(session.id, role="assistant", content="I'd be happy to help! Let me look into that for you.")

# 取得上下文視窗（最近 5 條訊息 + 自動摘要）
context = store.get_context_window(session.id, limit=5)
print(f"Summary: {context['summary']}")
for msg in context['messages']:
    print(f"[{msg.role}] {msg.content}")

# 搜尋歷史訊息
results = store.search_messages("order", session_id=session.id)
for msg in results:
    print(f"Found: {msg.content[:80]}...")

# 匯出會話資料
from agentmemory.export import Exporter
exporter = Exporter(store)
exporter.export_markdown("./export.md", session_id=session.id)
exporter.export_json("./export.json", session_id=session.id)
exporter.export_csv("./export.csv", session_id=session.id)

# 關閉儲存連線
store.close()
```

### 典型使用場景

#### 場景一：CLI 聊天助手記憶管理

```bash
# 為每個對話主題建立獨立會話
agentmemory --backend sqlite session create "技術討論" --tags tech
agentmemory --backend sqlite session create "產品規劃" --tags product

# 在會話中記錄對話
agentmemory msg add user "我們討論一下微服務架構的選型"
agentmemory msg add assistant "好的，目前主流方案有..."

# 切換到另一個會話
agentmemory session switch <product-session-id>

# 隨時回顧歷史上下文
agentmemory context --limit 10
```

#### 場景二：Python 整合到自有 Agent

```python
from agentmemory import MemoryStore
from agentmemory.storage import SQLiteBackend

store = MemoryStore(backend=SQLiteBackend("./agent.db"))

def chat_with_llm(user_input: str, session_id: str):
    # 儲存使用者訊息
    store.add_message(session_id, role="user", content=user_input)

    # 取得上下文視窗發送給 LLM
    context = store.get_context_window(session_id, limit=10)

    # 建立 prompt...
    # 呼叫 LLM API...
    llm_response = "LLM 的回覆內容"

    # 儲存助手回覆
    store.add_message(session_id, role="assistant", content=llm_response)
    return llm_response
```

---

## 💡 設計思路與迭代規劃

### 技術選型原因

| 決策 | 原因 |
|------|------|
| 純標準庫核心 | 最大化降低依賴風險，確保在任何 Python 環境中都能運行 |
| SQLite + FTS5 | 嵌入式資料庫零維運，FTS5 提供專業級全文搜尋能力 |
| JSON 檔案後端 | 人類可讀，方便除錯和版本控制，原子寫入保證資料安全 |
| 提取式摘要 | 零成本、零延遲、完全離線，不依賴任何外部 API |
| argparse CLI | 標準庫自帶，無需額外依賴，相容所有 Python 環境 |
| Rich TUI | Python 生態中最成熟的終端 UI 函式庫，渲染效果出色 |

### 架構設計理念

```
┌─────────────────────────────────────────┐
│              CLI / Python API           │
├─────────────────────────────────────────┤
│            MemoryStore (核心層)          │
│  ┌───────────┬──────────┬────────────┐  │
│  │  Session  │  Message │  Summary   │  │
│  │  Manager  │  Store   │  Engine    │  │
│  └───────────┴──────────┴────────────┘  │
├─────────────────────────────────────────┤
│        Storage Backend (儲存層)          │
│  ┌───────────┬──────────┬────────────┐  │
│  │  SQLite   │   JSON   │   Memory   │  │
│  │  (FTS5)   │  (Atomic)│  (In-Mem)  │  │
│  └───────────┴──────────┴────────────┘  │
├─────────────────────────────────────────┤
│        Export / TUI (擴展層)             │
└─────────────────────────────────────────┘
```

- **分層解耦**：核心層、儲存層、擴展層職責清晰，可獨立替換
- **介面抽象**：所有儲存後端實作統一介面，切換零成本
- **漸進增強**：核心功能零依賴，TUI 等增強功能按需安裝

### 後續迭代計畫

- [ ] **向量儲存後端** — 支援 Embedding + 向量相似度搜尋
- [ ] **LLM 摘要引擎** — 可選接入 OpenAI / 本地模型生成摘要
- [ ] **會話匯入** — 支援從 JSON / Markdown 檔案匯入歷史會話
- [ ] **Web UI** — 基於 FastAPI + WebSocket 的瀏覽器端管理介面
- [ ] **外掛系統** — 支援自訂儲存後端、摘要策略、匯出格式
- [ ] **多用戶支援** — 增加用戶維度，支援多用戶隔離

---

## 📦 安裝與部署

### pip 安裝（推薦）

```bash
pip install .
```

### 從原始碼安裝

```bash
git clone https://github.com/gitstq/AgentMemory-CLI.git
cd AgentMemory-CLI
pip install -e .
```

### 可選依賴

```bash
# TUI 儀表板（需要 rich 函式庫）
pip install ".[tui]"

# 或手動安裝
pip install rich>=13.0.0
```

### 驗證安裝

```bash
agentmemory --version
# 輸出: agentmemory 1.0.0
```

---

## 🤝 貢獻指南

我們歡迎並感謝所有形式的貢獻！無論是提交 Bug、改進文件還是貢獻程式碼。

### 提交 PR

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feature/your-feature-name`
3. 確保所有測試通過：`python -m pytest tests/`
4. 提交變更：`git commit -m "feat: 描述你的變更"`
5. 推送分支：`git push origin feature/your-feature-name`
6. 提交 **Pull Request**

### Commit 規範

請使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
feat: 新增向量儲存後端
fix: 修復 JSON 後端並行寫入問題
docs: 更新 API 使用文件
test: 增加摘要引擎邊界測試
refactor: 重構儲存層介面抽象
```

### 提交 Issue

- 使用清晰的標題描述問題
- 附上重現步驟和期望行為
- 標註相關標籤（bug / feature / question）

---

## 📄 開源協議

本專案基於 [MIT License](https://opensource.org/licenses/MIT) 開源。

```
MIT License

Copyright (c) 2024 AgentMemory Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq/AgentMemory-CLI">AgentMemory Team</a>
</p>

---
---

<a id="english"></a>

<p align="center">
  <a href="#简体中文">简体中文</a> | <a href="#繁體中文">繁體中文</a> | <b>English</b>
</p>

---

# English

<p align="center">
  <b>AgentMemory-CLI</b> — Lightweight Terminal AI Agent Stateful Memory Management Engine
</p>

---

## 🎉 About

Building AI Agent applications comes with a persistent challenge: **LLMs are stateless**, and developers must manually manage conversation context at every turn. Existing solutions either depend on heavyweight frameworks (LangChain, MemGPT) or lack essential features like multi-session isolation, automatic summarization, and context window management.

**AgentMemory-CLI** was built to solve exactly this problem.

It is a **zero-external-dependency** lightweight memory management engine designed specifically for terminal-based AI Agent workflows. Whether you're rapidly prototyping or deploying to production, it plugs right in. A single `pip install` gives you full session management, message storage, full-text search, automatic summarization, and context window management.

### 🎯 Core Value

- **Minimalism** — Core functionality relies exclusively on the Python standard library; zero third-party dependencies required
- **Ready to Use** — Complete CLI tool + Python API; integrate in under 5 minutes
- **Flexible & Extensible** — Three pluggable storage backends; choose what fits your needs
- **Production-Ready** — 97 unit tests, all passing; code quality you can trust

### 🔥 What Sets Us Apart

| Feature | AgentMemory-CLI | LangChain Memory | MemGPT |
|---------|:-:|:-:|:-:|
| Zero external dependency core | ✅ | ❌ | ❌ |
| Multi-session isolation | ✅ | Partial | ✅ |
| Auto-summarization (no LLM needed) | ✅ | ❌ | ❌ |
| Context window management | ✅ | Partial | ✅ |
| FTS5 full-text search | ✅ | ❌ | ❌ |
| Multi-format export | ✅ | ❌ | ❌ |
| TUI dashboard | ✅ | ❌ | ❌ |
| Installation footprint | < 100KB | > 50MB | > 100MB |

---

## ✨ Key Features

### 🧱 Zero External Dependency Core
Built entirely with Python standard library modules (`sqlite3`, `json`, `dataclasses`, `argparse`). **No third-party packages needed** for full core functionality. Ultra-lightweight, deployment-friendly.

### 💾 Three Pluggable Storage Backends
- **SQLite** — Built-in **FTS5 full-text search engine** for efficient keyword retrieval in both English and Chinese. Ideal for production.
- **JSON File** — Atomic write mechanism with human-readable persistence. Great for debugging and rapid prototyping.
- **In-Memory** — Zero-latency reads and writes. Perfect for testing and ephemeral use cases.

Switch backends with a single `--backend` flag — no code changes required.

### 🏷️ Multi-Session Isolation
Create, switch, search, and tag multiple independent sessions. Messages and summaries are fully isolated per session. Ideal for managing multiple Agent instances or concurrent conversation threads.

### 📝 Automatic Summarization Engine
A rule-based **extractive summarization** algorithm that automatically compresses history when message count exceeds a configurable threshold. **No LLM API calls required** — zero cost, zero latency, fully offline. Summaries are seamlessly woven into the context window so no historical information is lost.

### 🪟 Context Window Management
Intelligently assembles the **most recent N messages + historical summaries**, automatically adapting to the context length limits of any LLM. Your Agent always has "complete memory" without exceeding token budgets.

### 📤 Multi-Format Export
Export session data to **JSON / Markdown / CSV** in a single command. Perfect for data analysis, report generation, or integration with other systems.

### 🖥️ TUI Interactive Dashboard
A terminal visualization interface powered by the **Rich** library. View session status, message statistics, and storage information in real time — all from your terminal.

### ⌨️ Complete CLI
Six major subcommands — `session`, `msg`, `context`, `export`, `summary`, `dashboard` — covering the full lifecycle of memory management.

### ✅ 97 Unit Tests — All Passing
Production-grade test coverage across all core modules. Every commit is validated against the full test suite.

---

## 🚀 Quick Start

### Prerequisites

- **Python** >= 3.9 (supports 3.9 / 3.10 / 3.11 / 3.12)
- **OS**: Windows / macOS / Linux
- **Optional**: `rich >= 13.0.0` (for the TUI dashboard)

### Installation

```bash
# Install from PyPI (recommended)
pip install .

# Or install from source
git clone https://github.com/gitstq/AgentMemory-CLI.git
cd AgentMemory-CLI
pip install -e .

# Install TUI optional dependency
pip install ".[tui]"
```

### 30-Second Quick Tour

```bash
# 1. Create a session
agentmemory session create "my-first-chat"

# 2. Add some messages
agentmemory msg add user "Hi, I'd like to learn about this project"
agentmemory msg add assistant "Hello! AgentMemory-CLI is a lightweight memory management engine for AI Agents"

# 3. View the context window
agentmemory context --limit 5

# 4. Search message history
agentmemory msg search "project"

# 5. Export to Markdown
agentmemory export markdown --output chat.md
```

---

## 📖 Detailed Usage Guide

### Complete CLI Reference

#### 🔧 Global Options

```bash
# Check version
agentmemory --version

# Specify storage backend (sqlite / json / memory)
agentmemory --backend sqlite <command>

# Specify storage path
agentmemory --backend json --store-path ./my_data <command>
```

#### 📂 Session Management

```bash
# Create a session (with tags)
agentmemory session create "customer-support" --tags support v1

# List all sessions
agentmemory session list

# Switch active session
agentmemory session switch <session-id>

# Delete a session
agentmemory session delete <session-id>
```

#### 💬 Message Operations

```bash
# Add a message (roles: user / assistant / system)
agentmemory msg add user "Hello, how are you?"
agentmemory msg add assistant "I'm doing well, thanks!"
agentmemory msg add system "You are a helpful assistant."

# List messages
agentmemory msg list                          # All messages in current session
agentmemory msg list --limit 10               # Most recent 10
agentmemory msg list --role user              # User messages only
agentmemory msg list --session <session-id>   # Specific session

# Search messages
agentmemory msg search "keyword"
agentmemory msg search "order" --limit 5

# Delete a message
agentmemory msg delete <message-id>
```

#### 🪟 Context & Summary

```bash
# Get context window (most recent N messages + historical summary)
agentmemory context --limit 5

# View current session summary
agentmemory summary
```

#### 📤 Export

```bash
# Export as JSON
agentmemory export json --output chat.json

# Export as Markdown
agentmemory export markdown --output chat.md

# Export as CSV
agentmemory export csv --output chat.csv

# Export a specific session
agentmemory export json --session <session-id> --output data.json

# Export to stdout (omit --output)
agentmemory export markdown
```

#### 🖥️ TUI Dashboard

```bash
# Launch the interactive dashboard (requires rich)
agentmemory dashboard
```

### Python API Examples

```python
from agentmemory import MemoryStore
from agentmemory.storage import SQLiteBackend

# Create a memory store (SQLite backend)
store = MemoryStore(backend=SQLiteBackend("./my_agent.db"))

# Create a session (with tags)
session = store.sessions.create("customer-support", tags=["support", "v1"])

# Add messages
store.add_message(session.id, role="user", content="I need help with my order #12345")
store.add_message(session.id, role="assistant", content="I'd be happy to help! Let me look into that for you.")

# Get context window (most recent 5 messages + auto-summary)
context = store.get_context_window(session.id, limit=5)
print(f"Summary: {context['summary']}")
for msg in context['messages']:
    print(f"[{msg.role}] {msg.content}")

# Search message history
results = store.search_messages("order", session_id=session.id)
for msg in results:
    print(f"Found: {msg.content[:80]}...")

# Export session data
from agentmemory.export import Exporter
exporter = Exporter(store)
exporter.export_markdown("./export.md", session_id=session.id)
exporter.export_json("./export.json", session_id=session.id)
exporter.export_csv("./export.csv", session_id=session.id)

# Close the store connection
store.close()
```

### Typical Use Cases

#### Use Case 1: CLI Chat Assistant Memory Management

```bash
# Create independent sessions for each conversation topic
agentmemory --backend sqlite session create "tech-discussion" --tags tech
agentmemory --backend sqlite session create "product-planning" --tags product

# Record conversations within a session
agentmemory msg add user "Let's discuss microservice architecture options"
agentmemory msg add assistant "Sure, the mainstream approaches include..."

# Switch to another session
agentmemory session switch <product-session-id>

# Review historical context at any time
agentmemory context --limit 10
```

#### Use Case 2: Python Integration with Your Own Agent

```python
from agentmemory import MemoryStore
from agentmemory.storage import SQLiteBackend

store = MemoryStore(backend=SQLiteBackend("./agent.db"))

def chat_with_llm(user_input: str, session_id: str):
    # Save the user's message
    store.add_message(session_id, role="user", content=user_input)

    # Get the context window to send to the LLM
    context = store.get_context_window(session_id, limit=10)

    # Build the prompt...
    # Call the LLM API...
    llm_response = "The LLM's response content"

    # Save the assistant's reply
    store.add_message(session_id, role="assistant", content=llm_response)
    return llm_response
```

---

## 💡 Design Philosophy & Roadmap

### Technical Decisions

| Decision | Rationale |
|----------|-----------|
| Pure standard library core | Minimizes dependency risk; runs in any Python environment |
| SQLite + FTS5 | Zero-maintenance embedded database; FTS5 provides professional-grade full-text search |
| JSON file backend | Human-readable for debugging and version control; atomic writes ensure data safety |
| Extractive summarization | Zero cost, zero latency, fully offline; no external API dependency |
| argparse CLI | Ships with the standard library; compatible with all Python environments |
| Rich TUI | The most mature terminal UI library in the Python ecosystem; excellent rendering |

### Architecture

```
┌─────────────────────────────────────────┐
│              CLI / Python API           │
├─────────────────────────────────────────┤
│          MemoryStore (Core Layer)        │
│  ┌───────────┬──────────┬────────────┐  │
│  │  Session  │  Message │  Summary   │  │
│  │  Manager  │  Store   │  Engine    │  │
│  └───────────┴──────────┴────────────┘  │
├─────────────────────────────────────────┤
│       Storage Backend (Storage Layer)    │
│  ┌───────────┬──────────┬────────────┐  │
│  │  SQLite   │   JSON   │   Memory   │  │
│  │  (FTS5)   │  (Atomic)│  (In-Mem)  │  │
│  └───────────┴──────────┴────────────┘  │
├─────────────────────────────────────────┤
│        Export / TUI (Extension Layer)    │
└─────────────────────────────────────────┘
```

- **Layered Decoupling** — Core, storage, and extension layers have clearly defined responsibilities and can be replaced independently
- **Interface Abstraction** — All storage backends implement a unified interface; switching is seamless
- **Progressive Enhancement** — Core features require zero dependencies; enhancements like TUI are installed on demand

### Roadmap

- [ ] **Vector Storage Backend** — Support for Embedding + vector similarity search
- [ ] **LLM Summarization Engine** — Optional integration with OpenAI / local models for summary generation
- [ ] **Session Import** — Import historical sessions from JSON / Markdown files
- [ ] **Web UI** — Browser-based management interface built with FastAPI + WebSocket
- [ ] **Plugin System** — Support for custom storage backends, summarization strategies, and export formats
- [ ] **Multi-User Support** — Add user dimensions for multi-user isolation

---

## 📦 Installation & Deployment

### pip Install (Recommended)

```bash
pip install .
```

### Install from Source

```bash
git clone https://github.com/gitstq/AgentMemory-CLI.git
cd AgentMemory-CLI
pip install -e .
```

### Optional Dependencies

```bash
# TUI dashboard (requires rich)
pip install ".[tui]"

# Or install manually
pip install rich>=13.0.0
```

### Verify Installation

```bash
agentmemory --version
# Output: agentmemory 1.0.0
```

---

## 🤝 Contributing

We welcome and appreciate contributions of all kinds — bug reports, documentation improvements, and code contributions alike.

### Submitting a PR

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Ensure all tests pass: `python -m pytest tests/`
4. Commit your changes: `git commit -m "feat: describe your changes"`
5. Push the branch: `git push origin feature/your-feature-name`
6. Open a **Pull Request**

### Commit Convention

Please follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add vector storage backend
fix: resolve JSON backend concurrent write issue
docs: update API usage documentation
test: add summarization engine edge case tests
refactor: refactor storage layer interface abstraction
```

### Submitting an Issue

- Use a clear, descriptive title
- Include reproduction steps and expected behavior
- Apply relevant labels (bug / feature / question)

---

## 📄 License

This project is released under the [MIT License](https://opensource.org/licenses/MIT).

```
MIT License

Copyright (c) 2024 AgentMemory Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/gitstq/AgentMemory-CLI">AgentMemory Team</a>
</p>
