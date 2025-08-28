FROM python:3.12-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY . .

CMD ["gunicorn", "main:app", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "180"]
