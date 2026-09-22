import os
from pathlib import Path

import requests
from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

BASE_URL = os.getenv("LLM_BASE_URL")
API_KEY = os.getenv("LLM_API_KEY")
MODEL = os.getenv("LLM_MODEL")

if not BASE_URL:
    raise RuntimeError("LLM_BASE_URL belum diisi")

if not API_KEY:
    raise RuntimeError("LLM_API_KEY belum diisi")

if not MODEL:
    raise RuntimeError("LLM_MODEL belum diisi")


url = f"{BASE_URL}/chat/completions"

payload = {
    "model": MODEL,
    "messages": [
        {
            "role": "user",
            "content": "Jawab singkat: sebutkan ibu kota Jawa Timur.",
        }
    ],
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

response = requests.post(
    url,
    headers=headers,
    json=payload,
    timeout=60,
)

response.raise_for_status()

data = response.json()

print("Model:", MODEL)
print("Response:")
print(data["choices"][0]["message"]["content"])