## 基于 LangGraph 和 Google Gemini LLM 的多 Agent 协作股票分析系统

# Stock Analysis Multi-Agent

基于 **LangGraph**、**LangChain** 与 **Google Gemini 2.5** 开发的自动化股票研报生成系统。系统通过编排四个不同分工的 AI Agent，依次完成技术面、基本面与市场情绪分析，最终汇总生成现代化 UI 的 HTML 格式深度股票研究报告。

---

## 系统架构与核心逻辑

应用采用了顺序链式（Sequential Graph）的工作流结构，确保各环节按逻辑依赖推进：

[START] ➔ 1. 技术分析 Agent ➔ 2. 基本面 Agent ➔ 3. 情绪分析 Agent ➔ 4. 总编主管 Agent ➔ [END]
➔  自动跳转浏览器打开 HTML 研报。

为了应对免费 API 的 Rate Limit（频率限制），节点间加入了硬性延迟处理（8秒），保证流控平稳。

---

## 核心模块说明

### 1. 状态定义 (`StockState`)
使用 `TypedDict` 定义图（Graph）在节点间流转的全局状态：
* `ticker`: 目标股票代码（如 `mu` 代表美光科技）。
* `technical_report`: 技术分析文本。
* `fundamental_report`: 基本面分析文本。
* `sentiment_report`: 市场情绪分析文本。
* `final_report`: 汇总生成的 HTML 格式终版报告。

---

### 2. Agent 节点设计

| 节点名称 | 处理函数 | 数据来源 | 职责 |
| :--- | :--- | :--- | :--- |
| **技术分析 Agent** | `technical_agent` | `yfinance` 近 30 天收盘价 | 分析 K 线趋势、寻找支撑位与阻力位。 |
| **基本面 Agent** | `fundamental_agent` | `yfinance.info` (PE, PB, 当前股价) | 评估公司财务数据与估值合理性。 |
| **情绪分析 Agent** | `sentiment_agent` | `yfinance.news` 最新 5 条新闻 | 分析媒体舆情与市场情绪偏向。 |
| **总编/主管 Agent** | `reporter_agent` | 整合前三个 Agent 的分析报告 | 融合多方意见，利用 Tailwind CSS 渲染精美 HTML 研报。 |

---

### 3. 网络与代理配置 (Network Protocol)

为了解决 API 连接稳定性及访问限制问题，代码做了以下优化：
* **`yfinance` 隔离**：使用独立的 `requests.Session()` 并禁用环境变量继承 (`trust_env = False`)，使用标准的 User-Agent 头，规避底层 HTTP/2 协议冲突。
* **LLM 局部代理**：避免在全局设置 `os.environ` 代理，而是在实例化 `ChatGoogleGenerativeAI` 时通过 `client_args` 显式指定代理（端口需匹配本地代理软件设置，如 `http://127.0.0.1:7897`）。

---

## 环境依赖与配置

### 1. 安装依赖包
运行以下命令安装所需依赖库：
```bash
  pip install yfinance langchain-google-genai langgraph python-dotenv requests "httpx[socks]"
```

### 2. 环境变量 (.env)
在项目根目录下创建 .env 文件，并填入你的 Gemini API Key：
```bash
  GOOGLE_API_KEY=your_gemini_api_key_here
```
### 3. 本地代理配置
如果通过代理访问 Google API，请确保代码中的端口配置与 Clash Verge 等客户端的端口保持一致：
``` bash
    PROXY_ARGS = {
        "proxy": "[http://127.0.0.1:7897](http://127.0.0.1:7897)"  # 根据代理软件实际端口修改
    }
```
## 运行与输出结果
直接运行脚本：

```Bash
  python multi_agent.py
```
运行输出：

a.控制台实时打印各个 Agent 的执行进度与冷却等待提示。

b.自动在项目根目录下生成 stock_analysis_report.html。

c.脚本使用 Python 的 webbrowser 模块自动调用默认浏览器打开该 HTML 研报页面。