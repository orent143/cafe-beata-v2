FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads/avatars

EXPOSE 8000

# Use a shell form command instead of exec form
CMD python -m uvicorn backend.main:app --host=0.0.0.0 --port=8000