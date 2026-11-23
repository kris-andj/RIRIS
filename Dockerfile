FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY schema.sql seed.py init_db.py ./

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "python init_db.py && uvicorn backend.app:app --host 0.0.0.0 --port $PORT"]