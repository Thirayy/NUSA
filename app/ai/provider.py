import os
import httpx
from app.core.config import settings

class AIProvider:
    def __init__(self):
        self.api_key = settings.AI_API_KEY
        self.model = settings.LLM_MODEL
        # Menggunakan endpoint OpenRouter
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    def generate_chat_response(self, system_prompt: str, user_message: str) -> str:
        if not self.api_key :
            return "[Mode Non-AI / Simulasi]: Kredensial AI belum dikonfigurasi. Berikut adalah analisis deterministik dari data backend Anda."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000", # Opsional untuk OpenRouter rankings
            "X-Title": "NUSA Ecosystem"              # Opsional untuk OpenRouter rankings
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": 0.3
        }

        try:
            with httpx.Client(timeout=45.0) as client:
                response = client.post(self.base_url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return f"Gagal menghasilkan respons AI (Status: {response.status_code}, Detail: {response.text})"
        except Exception as e:
            return f"Terjadi kesalahan koneksi ke provider AI: {str(e)}"

ai_provider = AIProvider()