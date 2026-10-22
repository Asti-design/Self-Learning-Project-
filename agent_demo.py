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
    
    # 提取公司名称
    company_name = financials.get("公司名称", ticker_symbol)

    html_template = f"""
    <!DOCTYPE html>
    <html>
   <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{ticker_symbol} 深度研究报告</title>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap">
        <style>
            :root {{
                --primary: #0f172a;
                --secondary: #2563eb;
                --background: #f8fafc;
                --card-bg: #ffffff;
                --text-main: #1e293b;
                --text-muted: #64748b;
                --border: #e2e8f0;
            }}
            
            body {{
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
                background-color: var(--background);
                color: var(--text-main);
                line-height: 1.7;
                padding: 40px 20px;
                margin: 0;
            }}
            
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: var(--card-bg);
                padding: 40px;
                border-radius: 16px;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.02);
                border: 1px solid var(--border);
            }}
            
            /* 页眉设计 */
            .header {{
                position: relative;
                border-bottom: 2px solid var(--primary);
                padding-bottom: 20px;
                margin-bottom: 35px;
            }}
            .badge {{
                position: absolute;
                top: 0;
                right: 0;
                background: rgba(37, 99, 235, 0.08);
                color: var(--secondary);
                padding: 4px 14px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .title {{
                font-size: 1.85rem;
                font-weight: 800;
                color: var(--primary);
                margin: 0 0 8px 0;
                letter-spacing: -0.5px;
            }}
            .meta {{
                display: flex;
                gap: 20px;
                color: var(--text-muted);
                font-size: 0.85rem;
            }}
            
            h2 {{
                font-size: 1.25rem;
                color: var(--primary);
                font-weight: 700;
                border-left: 4px solid var(--secondary);
                padding-left: 12px;
                margin-top: 40px;
                margin-bottom: 20px;
            }}
            
            /* 财务看板表格美化 */
            .table-container {{
                overflow-x: auto;
                border-radius: 8px;
                border: 1px solid var(--border);
                margin: 20px 0 35px 0;
            }}
            .data-table {{
                width: 100%;
                border-collapse: collapse;
                text-align: left;
                font-size: 0.95rem;
            }}
            .data-table th {{
                background-color: #f1f5f9;
                color: var(--primary);
                font-weight: 600;
                padding: 14px 16px;
                border-bottom: 1px solid var(--border);
            }}
            .data-table td {{
                padding: 14px 16px;
                border-bottom: 1px solid var(--border);
                color: #334155;
            }}
            .data-table tr:last-child td {{ border-bottom: none; }}
            .data-table tr:hover {{ background-color: #f8fafc; }}
            
            /* AI 深度报告区域排版优化 */
            .analysis-render {{
                font-size: 1rem;
                color: #334155;
                text-align: justify;
            }}
            /* 清除 Markdown 转化后的标签原生丑陋样式 */
            .analysis-render h3 {{
                font-size: 1.15rem;
                color: var(--primary);
                margin-top: 30px;
                margin-bottom: 12px;
                font-weight: 700;
            }}
            .analysis-render p {{ margin-bottom: 16px; }}
            .analysis-render strong {{ color: var(--primary); font-weight: 600; }}
            .analysis-render ul {{ padding-left: 20px; margin-bottom: 20px; }}
            .analysis-render li {{ margin-bottom: 8px; }}
            .analysis-render hr {{ border: 0; border-top: 1px dashed var(--border); margin: 30px 0; }}
            
            .footer {{
                margin-top: 60px;
                border-top: 1px solid var(--border);
                padding-top: 20px;
                text-align: center;
                font-size: 0.8rem;
                color: var(--text-muted);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <span class="badge">Institutional Research</span>
                <div class="title">{company_name} ({ticker_symbol}) 智能投研深度权益报告</div>
                <div class="meta">
                    <span>📊 数据源：Yahoo Finance</span>
                    <span>⚡ 编译核心：Gemini 2.5 Flash</span>
                </div>
            </div>

            <h2>一、 核心财务与基本面看板</h2>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>核心监控指标 (Key Metrics)</th>
                            <th>当前市况表现 (Value)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([f"<tr><td><strong>{k}</strong></td><td>{v}</td></tr>" for k, v in financials.items()])}
                    </tbody>
                </table>
            </div>

            <h2>二、 华尔街专家系统独立评级报告</h2>
            <script id="markdown-raw" type="text/template">{ai_analysis}</script>
            
            <div id="analysis-render" class="analysis-render">正在进行投行标准排版美化...</div>
        </div>

        <div class="footer">
            © 2026 Gemini Stock Agent System. 本报告由大模型全自动量化编译，不作为直接投资依据。
        </div>

        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
            try {{
                const rawMarkdown = document.getElementById('markdown-raw').innerHTML;
                // 解析并优雅地灌入盒子
                document.getElementById('analysis-render').innerHTML = marked.parse(rawMarkdown);
            }} catch (e) {{
                document.getElementById('analysis-render').innerHTML = `<p style="color:red;">排版引擎渲染失败: ${{e.message}}</p>`;
            }}
        </script>
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
    
    
    # 调用报告生成函数
    save_to_styled_report(ticker_symbol, financials, response.content)

if __name__ == "__main__":
    run_stock_agent("南方两倍做多海力士")