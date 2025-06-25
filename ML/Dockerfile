FROM python:3.11-slim-buster

WORKDIR /app/ML

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY chat.py .

EXPOSE 8001

CMD ["uvicorn", "chat:app", "--host", "0.0.0.0", "--port", "8001"]
