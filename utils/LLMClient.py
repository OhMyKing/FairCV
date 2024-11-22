import logging
import time
from typing import Dict, List, Optional
import requests


class ZhipuAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'

    def chat_completion(self, messages: List[Dict]) -> Dict:
        try:
            url = self.api_url
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            data = {
                'model': 'glm-4-plus',
                'messages': messages,
                'temperature': 0.5,
                'top_p': 0.7,
                'request_id': f'resume_process_{int(time.time())}'
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise Exception(f"Error in chat completion: {str(e)}")


class OllamaClient:
    """Ollama API客户端"""

    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model_name = model_name

    def generate(self, prompt: str, temperature: float = 0.2) -> Optional[str]:
        """调用Ollama生成回复"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logging.error(f"Ollama API error: {str(e)}")
            return None
