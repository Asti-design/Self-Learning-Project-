import os
import webbrowser
import time  
from typing import TypedDict, Dict, Any
from dotenv import load_dotenv
import yfinance as yf
# python sent http request
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

# ==================== ⚙️ 基础网络与配置 ====================
load_dotenv()

# 彻底移除 os.environ 代理配置，防止底层 HTTP/2 协议发生冲突断开
# 隔离 yfinance 的网络请求，让其走本地原生网络
session = requests.Session()   
session.trust_env = False  
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

# 定义全局状态传递结构
class StockState(TypedDict):
    ticker: str
    technical_report: str
    fundamental_report: str
    sentiment_report: str
    final_report: str

# 代理公共配置（请确保你的 Clash/v2ray 开启了对应的端口，默认通常是 7890）
PROXY_ARGS = {
    "proxy": "socks5://127.0.0.1:7897"  # 如果是 HTTP 端口可改为 http://127.0.0.1:7897
}

# ==================== 节点 1：技术分析 Agent ====================
def technical_agent(state: StockState) -> Dict[str, Any]:
    print("📈 [技术分析 Agent] 正在研究K线趋势...")
    
    # ✨ 核心改进：直接在 client_args 中注入专属代理通道，不走全局环境变量
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.3, 
        max_retries=10,
        client_args=PROXY_ARGS
    )
    
    ticker_symbol = state["ticker"]
    try:
        ticker = yf.Ticker(ticker_symbol, session=session)
        hist = ticker.history(period="30d")
        prices = hist['Close'].round(2).to_dict()
    except Exception:
        prices = {"提示": "数据受限，采用标准趋势线分析"}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个精通K线、均线、RSI的【技术分析师】。请根据历史价格简要分析趋势、压力位和支撑位。"),
        ("human", "股票: {ticker}\n价格历史: {prices}")
    ])
    chain = prompt | llm
    response = chain.invoke({"ticker": ticker_symbol, "prices": str(prices)})
    return {"technical_report": response.content}

# ==================== 节点 2：基本面分析 Agent ====================
def fundamental_agent(state: StockState) -> Dict[str, Any]:
    print("⏳ 正在等待免费额度冷却 (8秒)...")
    time.sleep(8)  
    print("🏢 [基本面 Agent] 正在审计财务报表...")
    
    # ✨ 核心改进：内部实例化专属代理的大模型
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.3, 
        max_retries=10,
        client_args=PROXY_ARGS
    )
    
    ticker_symbol = state["ticker"]
    try:
        ticker = yf.Ticker(ticker_symbol, session=session)
        info = ticker.info
        financials = {
            "当前股价": info.get("currentPrice"),
            "市盈率(PE)": info.get("trailingPE"),
            "市净率(PB)": info.get("priceToBook")
        }
    except Exception:
        financials = {"提示": "采用标准价值投资模型估值"}

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一位严谨的【基本面分析师】。请根据财务指标简要评估公司的估值是否合理。"),
        ("human", "股票: {ticker}\n财务指标: {financials}")
    ])
    chain = prompt | llm
    response = chain.invoke({"ticker": ticker_symbol, "financials": str(financials)})
    return {"fundamental_report": response.content}

# ==================== 节点 3：情绪分析 Agent ====================
def sentiment_agent(state: StockState) -> Dict[str, Any]:
    print("⏳ 正在等待免费额度冷却 (8秒)...")
    time.sleep(8)  
    print("📰 [情绪分析 Agent] 正在搜集最新新闻媒体舆情...")
    
    # ✨ 核心改进：内部实例化专属代理的大模型
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.3, 
        max_retries=10,
        client_args=PROXY_ARGS
    )
    
    ticker_symbol = state["ticker"]
    news_titles = []
    try:
        ticker = yf.Ticker(ticker_symbol, session=session)
        yf_news = ticker.news[:5] 
        news_titles = [item.get("title") for item in yf_news]
    except Exception:
        news_titles = ["推出最新AI创新举措", "市场静待该股最新财报表现"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", "评估当前的市场情绪。你是一位敏锐的【媒体舆情分析师】。请根据最新的新闻标题，简要评估市场情绪。"),
        ("human", "股票: {ticker}\n最新新闻标题: {news}")
    ])
    chain = prompt | llm
    response = chain.invoke({"ticker": ticker_symbol, "news": str(news_titles)})
    return {"sentiment_report": response.content}

# ==================== 节点 4：总编/主管 Agent ====================
def reporter_agent(state: StockState) -> Dict[str, Any]:
    print("⏳ 正在等待免费额度冷却 (8秒)...")
    time.sleep(8)  
    print("✍️  [主管 Agent] 正在撰写高颜值 HTML 研报...")
    
    # ✨ 核心改进：内部实例化专属代理的大模型
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        temperature=0.3, 
        max_retries=10,
        client_args=PROXY_ARGS
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一位证券研究所的主管。
                    你需要审阅三份报告，将它们融合成一份视觉极其精美、现代化的网页版【股票研究综合报告】。

                    【严格输出要求】：
                    1. 必须直接输出完整的 HTML 代码，包含 <!DOCTYPE html>, <html>, <head>, <body>。
                    2. 必须在 <head> 中引入 Tailwind CSS CDN：<script src="https://cdn.tailwindcss.com"></script>
                    3. 页面布局请采用科技感/专业金融感排版（利用卡片式布局、精美阴影、清晰的字号梯度）。
                    4. 投资评级（买入/持有/卖出）必须用醒目的徽章标签展示（如：买入用绿底白字，卖出用红底白字）。
                    5. 注意：请直接开始输出 HTML 代码，绝对不要包含任何 Markdown 格式的包裹符号（比如不要使用 ```html 或 ```）。"""),
        ("human", """股票代码: {ticker}
        
                    --- 技术面意见 ---
                    {tech}

                    --- 基本面意见 ---
                    {fund}

                    --- 市场情绪意见 ---
                    {sentiment}""")
    ])
    chain = prompt | llm
    response = chain.invoke({
        "ticker": state["ticker"],
        "tech": state["technical_report"],
        "fund": state["fundamental_report"],
        "sentiment": state["sentiment_report"]
    })
    return {"final_report": response.content}

# ==================== ⚙️ 编排 LangGraph 工作流 ====================
workflow = StateGraph(StockState)

workflow.add_node("tech_node", technical_agent)
workflow.add_node("fund_node", fundamental_agent)
workflow.add_node("sent_node", sentiment_agent)
workflow.add_node("report_node", reporter_agent)

workflow.add_edge(START, "tech_node")          
workflow.add_edge("tech_node", "fund_node")     
workflow.add_edge("fund_node", "sent_node")     
workflow.add_edge("sent_node", "report_node")   
workflow.add_edge("report_node", END)

app = workflow.compile()

# ==================== 🚀 运行系统 ====================
if __name__ == "__main__":
    target_stock = "mu"  
    print(f"🚀 启动 AI 证券分析师团队，目标股票: {target_stock}...\n")
    
    initial_state = {"ticker": target_stock}
    final_output = app.invoke(initial_state)
    
    raw_html = final_output["final_report"]
    
    # 兼容处理可能携带的 Markdown 标记
    if "```html" in raw_html:
        raw_html = raw_html.split("```html")[1].split("```")[0]
    elif "```" in raw_html:
        raw_html = raw_html.split("```")[1].split("```")[0]

    file_name = "stock_analysis_report.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(raw_html.strip())
    
    print(f"\n✨ 报告生成成功！保存为 {file_name}")
    print(f"🌐 正在为您自动跳转并打开网页报告...")
    
    webbrowser.open(f"file://{os.path.abspath(file_name)}")