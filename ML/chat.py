import datetime
import whisper
import requests
import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import tempfile


GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set")


class Chat:
    def __init__(self, model_name, api_key):
        self.model = model_name
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def chat(self, messages):
        try:
            print(f"Sending request to Groq API with {len(messages)} messages")
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.5
                },
                timeout=30
            )
            print(f"Response status: {response.status_code}")
            if not response.ok:
                print(f"Response content: {response.text}")
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            raise
        except KeyError as e:
            print(f"Response parsing error: {e}, Response: {response.text if 'response' in locals() else 'No response'}")
            raise
        except Exception as e:
            print(f"Unexpected error in chat method: {e}")
            raise

model = Chat("llama3-70b-8192", GROQ_API_KEY)
model_voice = whisper.load_model("tiny")


def format_event(event):
    try:
        # Проверяем наличие обязательных полей
        if not isinstance(event, dict):
            return f"- Invalid event format: {event}"
        
        # Получаем start_time (может быть в разных форматах)
        start_field = event.get("start") or event.get("start_time")
        end_field = event.get("end") or event.get("end_time") 
        summary = event.get("summary") or event.get("title", "Untitled event")
        
        if not start_field or not end_field:
            return f"- {summary} (incomplete event data)"
            
        # Парсим даты
        start = datetime.datetime.fromisoformat(
            start_field.replace("Z", "+00:00")).strftime("%B %d, %Y %I:%M %p")
        end = datetime.datetime.fromisoformat(
            end_field.replace("Z", "+00:00")).strftime("%I:%M %p")
        location = event.get("location", "Unknown location") or "Unknown location"
        
        return f"- {summary} from {start} to {end} at {location}"
    except Exception as e:
        print(f"Error formatting event {event}: {e}")
        summary = event.get("summary") or event.get("title", "Unknown event")
        return f"- {summary} (formatting error)"


def build_system_prompt(calendar_data=None):
    today = datetime.datetime.now().strftime("%B %d, %Y")
    try:
        if calendar_data:
            print(f"Processing {len(calendar_data)} calendar events")
            calendar_context = "\n".join(format_event(e) for e in calendar_data if e)
        else:
            calendar_context = "No calendar events available"
    except Exception as e:
        print(f"Error processing calendar data: {e}")
        calendar_context = "Error loading calendar events"
        
    content = (
        "You are a helpful assistant who answers questions about the user's calendar and gives general productivity tips. "
        "If the user wants to create a calendar event, respond ONLY with a valid JSON object with fields: title, description, start_time, end_time, all_day, location, type. "
        "Otherwise, answer as usual. "
        "If user does not setup type use 'other work'"
        "Only respond based on the provided calendar and general knowledge. "
        f"Today: {today}\n"
        f"Here is the user's calendar:\n\n{calendar_context}"
    )
    return {"role": "system", "content": content}


app = FastAPI(title="ML Calendar Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    calendar: Optional[List[dict]] = None
    history: Optional[List[dict]] = None  # Добавляем поле для истории


class ChatResponse(BaseModel):
    response: str


class VoiceResponse(BaseModel):
    transcription: str
    response: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        print(f"Received chat request: {req.message[:50]}...")
        if req.history:
            print(f"Chat history provided: {len(req.history)} messages")
        
        system_prompt = build_system_prompt(req.calendar)
        
        # Строим полный список сообщений с историей
        messages = [system_prompt]
        
        # Добавляем историю чата если есть
        if req.history:
            for hist_msg in req.history:
                if isinstance(hist_msg, dict) and 'role' in hist_msg and 'content' in hist_msg:
                    # Убеждаемся что роль корректная для Groq API
                    role = hist_msg['role']
                    if role == 'llm':
                        role = 'assistant'  # Groq использует 'assistant' вместо 'llm'
                    messages.append({"role": role, "content": hist_msg['content']})
        
        # Добавляем текущее сообщение пользователя
        messages.append({"role": "user", "content": req.message})
        
        print(f"Built messages with system prompt + history + current, total messages: {len(messages)}")
        reply = model.chat(messages)
        print(f"Got reply from model: {reply[:50] if reply else 'None'}...")
        return ChatResponse(response=reply)
    except Exception as e:
        print(f"Chat endpoint error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"ML Service Error: {str(e)}")


@app.post("/voice", response_model=VoiceResponse)
def voice_chat(file: UploadFile = File(...)):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(file.file.read())
            tmp_path = tmp.name

        result = model_voice.transcribe(tmp_path, language='en', fp16=False)
        text = result["text"].strip()

        system_prompt = build_system_prompt()
        messages = [system_prompt, {"role": "user", "content": text}]
        reply = model.chat(messages)

        return VoiceResponse(transcription=text, response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ML Service Error: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    print(f"Starting ML service with GROQ_API_KEY: {'*' * (len(GROQ_API_KEY) - 4) + GROQ_API_KEY[-4:] if GROQ_API_KEY else 'NOT SET'}")
    uvicorn.run("chat:app", host="0.0.0.0", port=8001, reload=True)