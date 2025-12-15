FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY bot/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY bot/ ./bot/
COPY core/ ./core/
COPY api/ ./api/

# Environment variables (will be set by docker-compose)
ENV PYTHONUNBUFFERED=1

CMD ["python", "bot/telegram_bot.py"]
