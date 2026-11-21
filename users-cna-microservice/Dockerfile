FROM python:3.12-slim

WORKDIR /app

COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv && pipenv sync --system

COPY . .

EXPOSE 9090

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "9090"]
