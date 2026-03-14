FROM python:3.12

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade pip && \
    pip install "poetry==1.7.1" && \
    poetry config virtualenvs.create false && \
    poetry export -f requirements.txt --output requirements.txt && \
    pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/staticfiles

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]