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


class Chat:
    def __init__(self, model_name, api_key):
        self.model = model_name
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def chat(self, messages):
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
            }
        )
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()


model = Chat("llama3-70b-8192", "key")
model_voice = whisper.load_model("tiny")


def format_event(event):
    start = datetime.datetime.fromisoformat(
        event["start"].replace("Z", "+00:00")).strftime("%B %d, %Y %I:%M %p")
    end = datetime.datetime.fromisoformat(
        event["end"].replace("Z", "+00:00")).strftime("%I:%M %p")
    location = event.get("location", "Unknown location") or "Unknown location"
    return f"- {event['summary']} from {start} to {end} at {location}"


def build_system_prompt(calendar_data=None):
    today = datetime.datetime.now().strftime("%B %d, %Y")
    calendar_context = "\n".join(format_event(e) for e in calendar_data)
    content = (
        "You are a helpful assistant who answers questions about the user's calendar and gives general productivity tips. "
        "Only respond based on the provided calendar and general knowledge. "
        f"Today: {today}\n"
        f"Here is the user's calendar:\n\n{calendar_context}"
    )
    return {"role": "system", "content": content}


app = FastAPI(title="ML Calendar Chat API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    calendar: Optional[List[dict]] = None


class ChatResponse(BaseModel):
    response: str


class VoiceResponse(BaseModel):
    transcription: str
    response: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        system_prompt = build_system_prompt(req.calendar)
        messages = [system_prompt, {"role": "user", "content": req.message}]
        reply = model.chat(messages)
        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


if __name__ == "__main__":
    uvicorn.run("ml_calendar_chat_api:app",
                host="0.0.0.0", port=8001, reload=True)
