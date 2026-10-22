import os
from dotenv import load_dotenv
import yfinance as yf
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# 加载环境变量
load_dotenv()

# 初始化 Gemini 模型
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2
)

# 创建一个会话，并添加浏览器请求头
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

def get_stock_data(ticker_symbol: str):
    """获取股票的技术面和基本面原始数据"""
    try:
        ticker = yf.Ticker(ticker_symbol, session=session)
        hist = ticker.history(period="30d")
        if hist.empty:
            return None, "未获取到历史数据，可能被限流了。"
            
        close_prices = hist['Close'].round(2).to_dict()
        info = ticker.info
        fundamental_data = {
            "公司名称": info.get("longName", "未知"),
            "行业": info.get("sector", "未知"),
            "当前股价": info.get("currentPrice", "未知"),
            "市盈率(PE)": info.get("trailingPE", "未知"),
            "市净率(PB)": info.get("priceToBook", "未知"),
            "52周最高价": info.get("fiftyTwoWeekHigh", "未知"),
            "52周最低价": info.get("fiftyTwoWeekLow", "未知")
        }
        return close_prices, fundamental_data
    except Exception as e:
        return None, f"数据获取失败: {str(e)}"

def save_to_styled_report(ticker_symbol, financials, ai_analysis):
    """【新增函数】将AI分析结果和基本面数据,渲染成精美的专业报告页面"""
    
    # 替换 AI 文本中的换行符，防止在 HTML 中排版缩成一团
    formatted_analysis = ai_analysis.replace("\n", "<br>")
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{ticker_symbol} 投资分析报告</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif, "Microsoft YaHei"; color: #1e293b; padding: 30px; max-width: 800px; margin: auto; line-height: 1.6; }}
            .header {{ border-bottom: 3px solid #0f172a; padding-bottom: 10px; margin-bottom: 30px; }}
            .title {{ font-size: 24pt; font-weight: bold; color: #0f172a; margin: 0; }}
            .meta {{ color: #64748b; font-size: 10pt; margin-top: 5px; }}
            h2 {{ font-size: 14pt; color: #0f172a; border-left: 4px solid #2563eb; padding-left: 10px; margin-top: 30px; }}
            .data-table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            .data-table th {{ background-color: #f8fafc; text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; }}
            .data-table td {{ padding: 10px; border-bottom: 1px solid #edf2f7; color: #475569; }}
            .analysis-box {{ background-color: #fafafa; border: 1px solid #e2e8f0; padding: 20px; border-radius: 6px; font-size: 11pt; text-align: justify; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">{ticker_symbol} 个股量化智能分析报告</div>
            <div class="meta">生成机构:Gemini Stock Agent • 数据源:yfinance</div>
        </div>

        <h2>一、 核心基本面指标</h2>
        <table class="data-table">
            <thead>
                <tr><th>指标名称</th><th>数据表现</th></tr>
            </thead>
            <tbody>
                {"".join([f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in financials.items()])}
            </tbody>
        </table>

        <h2>二、 华尔街专家系统分析报告</h2>
        <div class="analysis-box">
            {formatted_analysis}
        </div>
    </body>
    </html>
    """
    
    file_name = f"{ticker_symbol}_analysis_report.html"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(html_template)
    print(f"✨ HTML 报告已生成: {file_name}")
    
    # 🚀 自动唤醒 Windows 默认浏览器并跳转打开它！
    os.startfile(file_name) 
    print("🚀 成功！已自动为你跳转到浏览器查看精美可视化报告！")

def run_stock_agent(ticker_symbol: str):
    print(f"📡 正在获取 {ticker_symbol} 的实时市场数据...")
    prices, financials = get_stock_data(ticker_symbol)
    
    if prices is None:
        print("⚠️ 真实数据获取受限，已启动【内置模拟数据】供 Agent 演示：")
        prices = {"2026-06-01": 180.5, "2026-06-15": 185.2, "2026-06-30": 192.3}
        financials = {"公司名称": "Apple Inc. (模拟)", "行业": "科技", "当前股价": 192.3, "市盈率(PE)": 30.5, "市净率(PB)": 45.2}

    prompt = ChatPromptTemplate.from_messages([
        ("system", """你是一位资深的华尔街证券分析师。
        请结合用户提供的【历史价格数据】进行技术面分析（判断趋势、支撑位），
        并结合【基本面数据】评估该股票的估值是否合理。
        最后给出一个简短的投资决策建议（买入/卖出/观望）及原因。"""),
        ("human", "股票代码: {ticker}\n\n【历史价格(30天收盘价)】:\n{prices}\n\n【基本面指标】:\n{financials}")
    ])

    chain = prompt | llm

    print(f"🤖 Gemini 智能体正在分析并生成报告...\n" + "="*40)
    
    response = chain.invoke({
        "ticker": ticker_symbol,
        "prices": str(prices),
        "financials": str(financials)
    })
    
    
    # 2. 【新增】调用报告生成函数
    save_to_styled_report(ticker_symbol, financials, response.content)

if __name__ == "__main__":
    run_stock_agent("nok")