from dataclasses import dataclass, field
from typing import DefaultDict
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma  
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_community.vectorstores.utils import filter_complex_metadata
import datetime
import re
import sounddevice as sd
import scipy.io.wavfile as wav
import whisper # Need install ffmpeg
import os
import time
import uuid
import json



# Настройки моделей 
model_voice = whisper.load_model("tiny")
llm_model = "deepseek-r1:1.5b"
embedding_model = "mxbai-embed-large"
model = ChatOllama(model=llm_model)
embeddings = OllamaEmbeddings(model=embedding_model)

# Фиктивный календарь
calendar = {
    "events": [
        {
            "id": "1",
            "summary": "Team Meeting",
            "start": "2025-06-20T15:00:00Z",
            "end": "2025-06-20T16:00:00Z",
            "location": "room 108",
            "attendees": ["Stepa", "Oleg"]
        },
        {
            "id": "2",
            "summary": "Doctor Appointment",
            "start": "2025-06-21T09:00:00Z",
            "end": "2025-06-21T09:30:00Z",
            "location": "Clinic",
            "attendees": []
        },
        {
            "id": "3",
            "summary": "Project Deadline",
            "start": "2025-06-30T23:59:59Z",
            "end": "2025-06-30T23:59:59Z",
            "location": "",
            "attendees": []
        }
    ]
}

# Обработка событий как документ 
@dataclass
class Document:
    page_content: str
    metadata: DefaultDict[str, str] = field(default_factory=dict)

# Обработка формата времени
def format_time(dt_str):
    dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    time_str = dt.strftime("%I:%M %p")  
    if time_str.startswith("0"):
        time_str = time_str[1:]
    return time_str  


# need fix dates
# vector database
def refresh_vectorstore():
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50)
    calendar_docs = []

    for event in calendar["events"]:
        start_fmt = format_time(event['start'])
        end_fmt = format_time(event['end'])
        desc = f"{event['summary']} from {start_fmt} to {end_fmt} at {event.get('location') or 'Unknown Location'}"
        doc = Document(page_content=desc)
        calendar_docs.append(doc)

    chunks = text_splitter.split_documents(calendar_docs)
    chunks = filter_complex_metadata(chunks)

  
    global vector_store
    if 'vector_store' in globals() and vector_store is not None:
        vector_store = None
 
    time.sleep(0.5)

    if os.path.exists("chroma_calendar"):
        import shutil
        retries = 3
        for i in range(retries):
            try:
                shutil.rmtree("chroma_calendar")
                break
            except PermissionError:
                time.sleep(1)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="chroma_calendar",
    )
    return vector_store


vector_store = refresh_vectorstore()
retriever = vector_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"k": 3, "score_threshold": 0.2},
)

# Промпт для ответов Ассистента  
prompt = ChatPromptTemplate.from_template(
    """
    You are a concise and practical productivity assistant focused on calendar management.
    Respond shortly and clearly. No extra explanations or questions.
    - Provide short, clear answers focused on the user's calendar events.
    - If the user asks about events on a specific date, only list all matching events with their time, summary, and location. if no event on this date say something like "no event".
    - Show times in a human-readable 12-hour format with AM/PM (e.g., "5 PM", "9:30 AM").
    - If no events match, respond with: "No events found for that date."
    - For general calendar-related questions, answer briefly and clearly.
    - Do not add extra explanations or questions.
    - Do not invent or assume information not present in the context.

    Context:
    {context}

    Question:
    {question}
    """
)

chain = (
    RunnablePassthrough()
    | prompt
    | model
    | StrOutputParser()
)

# Промпт для распознавания действий
intent_prompt = ChatPromptTemplate.from_template("""
Today is {today}.
You are a calendar assistant.
If the user wants to add a calendar event, return a JSON object like:
{{
  "action": "add",
  "summary": "...",
  "start": "...",   // ISO8601 format
  "end": "..."
}}
If the user is just asking questions or making statements without intent to add events, return exactly "no_action".

Do NOT interpret the user as wanting to meet with the assistant.
Only respond with the JSON or "no_action", no explanations or other text.

User input:
{user_input}

""")

# Распознавание просит ли что нибуть пользователь сделать с колендарем
def parse_intent(user_input: str):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    intent_input = intent_prompt.format_prompt(today=today, user_input=user_input)
    response = model.invoke(intent_input)
    cleaned_response = re.sub(r"<think>.*?</think>\n?", "", response.content, flags=re.DOTALL)
    content = cleaned_response.strip()
    if content.lower().startswith("no_action"):
        return None
    try:
        return json.loads(content)
    except Exception:
        print("Ошибка парсинга JSON:", content)
        return None

# запись голоса пользователя
def record_audio(duration=10, fs=16000, filename="audio.wav"):
    print(f"Recording {duration} seconds. Speak")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    wav.write(filename, fs, recording)
    return filename

# преобразования аудио в текст
def transcribe_audio(filename):
    result = model_voice.transcribe(filename, language='en', fp16=False)
    text = result["text"].strip()
    print("You say:", text)
    return text

# Добавление ивентов в календарь
def add_event(event_data):
    new_event = {
        "id": str(uuid.uuid4()),
        "summary": event_data["summary"],
        "start": event_data["start"],
        "end": event_data["end"],
        "location": "",
        "attendees": []
    }
    calendar["events"].append(new_event)
    return new_event

# Чат
print("chat: \nType voice to say or exit to quit\n")

while True:
    user_input = input("You: ").strip()
    # выход из чата
    if user_input.lower() in ["exit", "quit"]:
        break
    # начала записи голоса
    if user_input.lower() in ["voice"]:
        audio_file = record_audio(duration=5)
        user_input = transcribe_audio(audio_file)
        
    # распознавание намерений пользователя
    intent = parse_intent(user_input)
    if intent and intent.get("action") == "add":
        event = add_event(intent)
        print(f"Added event: {event['summary']} from {event['start']} to {event['end']}")
        vector_store = refresh_vectorstore()
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 3, "score_threshold": 0.2},
        )
        continue

    retrieved_docs = retriever.invoke(user_input)
    formatted_input = {
        "context": "\n".join(doc.page_content for doc in retrieved_docs),
        "question": user_input
    }

    response = chain.invoke(formatted_input)
    response = re.sub(r"<think>.*?</think>\n?", "", response, flags=re.DOTALL)
    print(f"Assistant: {response}")
