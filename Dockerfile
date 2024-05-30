FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD ["sh", "-c", "uvicorn ${API_SCRIPT} --host 0.0.0.0 --port $API_PORT"]
