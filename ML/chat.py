import datetime
import requests
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
import os

# нужно соединить чат с информацией о реальном календаре
# желательно передавать в виде json
calendar = [
    {
        "summary": "Team Meeting",
        "start": "2025-06-20T15:00:00Z",
        "end": "2025-06-20T16:00:00Z",
        "location": "Room 108"
    },
    {
        "summary": "Doctor Appointment",
        "start": "2025-06-21T09:00:00Z",
        "end": "2025-06-21T09:30:00Z",
        "location": "Clinic"
    },
    {
        "summary": "Project Deadline",
        "start": "2025-06-30T23:59:59Z",
        "end": "2025-06-30T23:59:59Z",
        "location": ""
    }
]


class GroqChat:
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

def initialize_model():
    # api_key
    groq_api_key = "key"
    groq = GroqChat("llama3-70b-8192", groq_api_key)
    model_voice = whisper.load_model("tiny")
    return groq, model_voice

def format_event(event):
    start = datetime.datetime.fromisoformat(event["start"].replace("Z", "+00:00")).strftime("%B %d, %Y %I:%M %p")
    end = datetime.datetime.fromisoformat(event["end"].replace("Z", "+00:00")).strftime("%I:%M %p")
    location = event.get("location", "Unknown location") or "Unknown location"
    return f"- {event['summary']} from {start} to {end} at {location}"

def get_calendar_context():
    return "\n".join(format_event(e) for e in calendar)

def record_audio(duration=5, fs=16000, filename="audio.wav"):
    print(f"Recording {duration} seconds. Speak now...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    filepath = os.path.join("ML/audio", filename)
    wav.write(filepath, fs, recording)
    return filename

def transcribe_audio(filename, model_voice):
    result = model_voice.transcribe(filename, language='en', fp16=False)
    text = result["text"].strip()
    print("You said:", text)
    return text


def build_system_prompt():
    today = datetime.datetime.now().strftime("%B %d, %Y")
    calendar_context = get_calendar_context()
    content = (
        "You are a helpful assistant who answers questions about the user's calendar and gives general productivity tips. "
        "Only respond based on the provided calendar and general knowledge. "
        f"Today: {today}\n"
        f"Here is the user's calendar:\n\n{calendar_context}"
    )
    return {"role": "system", "content": content}

# инициализация чата и моделей
def chat():
    groq, model_voice = initialize_model()
    print("Chat started. Type your message or 'voice' to speak. Type 'exit' to quit.")
    system_prompt = build_system_prompt()
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        if user_input.lower() == "voice":
            audio_file = record_audio()
            user_input = transcribe_audio(audio_file, model_voice)

        messages = [system_prompt, {"role": "user", "content": user_input}]
        try:
            reply = groq.chat(messages)
            print("Assistant:", reply)
        except Exception as e:
            print("Error:", e)

