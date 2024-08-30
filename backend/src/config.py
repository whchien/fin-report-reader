from pathlib import Path

KEY_METRICS = [
    "Gross Profit Margin",
    "Working Capital",
    "Quick Ratio",
    "Debt to Equity Ratio",
    "Total Asset Turnover",
    "Return on Assets",
    "Operating Cash Flow",
]

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / "./tmp/"
SAVE_DIR = ROOT_DIR / "./tmp/storage/"
DIMENSIONS = 1536

MAX_RETRIES = 5
RETRY_DELAY = 5

OPENAI_MODEL = "gpt-4o"
ASSISTANT_NAME = "Financial Resport Analyst"
ASSISTANT_PROMPT = """You are an expert financial analyst. 
Use your knowledge base to answer questions about financial statements."""
ASSISTANT_QUERY = """What are the key financial highlights of the annual report? 
        Please consider the following: {query}"""