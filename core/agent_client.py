import os
from typing import Dict, List
from openai import OpenAI

class AgentClient:
    '''
    调用LLM的基类
    仅支持使用OpenAI格式的LLM
    '''

    def __init__(self, model: str = None, api_key: str = None, base_url: str = None, timeout: int = None):
        self.model = model or os.getenv("MODEL")
        self.api_key = api_key or os.getenv("API_KEY")
        self.base_url = base_url or os.getenv("BASE_URL")
        self.timeout = timeout or int(os.getenv("TIMEOUT", "60"))

        if not all([self.model, self.api_key, self.base_url]):
            raise ValueError("模型ID、密钥和服务地址必须提供或者在.env中定义")
        
        self.client = OpenAI(api_key = self.api_key, base_url = self.base_url, timeout=self.timeout)

    def think(self, message: List[Dict[str, str]], temperature: float = 0):
        '''
        调用大模型，获取响应结果
        '''
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=message, 
                temperature=temperature, 
                stream=True
            )
            print("✅ 大模型响应成功")

            collect_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collect_content.append(content)
            print()
            return "".join(collect_content)
        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None
