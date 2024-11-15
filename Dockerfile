FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/djangoapp

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
