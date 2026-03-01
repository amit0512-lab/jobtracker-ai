FROM python:3.11-slim

# Working directory
WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# spaCy model download
RUN python -m spacy download en_core_web_sm

# App code copy karo
COPY . .

# Local storage folder banao
RUN mkdir -p local_storage/resumes

# Non-root user — security best practice
RUN adduser --disabled-password --gecos "" appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]