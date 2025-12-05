"""
配置文件：LLM API配置
"""

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-78c61c5b0f1347ccb4508f7bb6cb216d"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# OpenAI API 配置（如果需要）
OPENAI_API_KEY = None  # 如果需要使用OpenAI，请设置此值
OPENAI_BASE_URL = "https://api.openai.com/v1"
OPENAI_MODEL = "gpt-3.5-turbo"

# 默认使用 DeepSeek
DEFAULT_API_KEY = DEEPSEEK_API_KEY
DEFAULT_BASE_URL = DEEPSEEK_BASE_URL
DEFAULT_MODEL = DEEPSEEK_MODEL

