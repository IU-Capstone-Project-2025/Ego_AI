import os
import requests
from typing import List, Dict, Any

from app.core.config import settings
from fastapi import HTTPException

class LLMChatService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model_name = "llama3-70b-8192"

    def chat(self, messages: List[Dict[str, str]]) -> str:
        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not set in the .env")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        json_data = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.5
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=json_data)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            return response.json()['choices'][0]['message']['content'].strip()
        except requests.exceptions.RequestException as e:
            # Log the error and re-raise or handle as appropriate for your application
            print(f"Error interacting with Groq API: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get response from LLM: {e}")
        except KeyError as e:
            print(f"KeyError in parsing LLM response: {e}. Full response: {response.json()}")
            raise HTTPException(status_code=500, detail=f"Unexpected LLM response format: {e}") 
