FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -- no-cache-dir -r requirements.txt

# копируем весь проект
COPY . .

EXPOSE 8000