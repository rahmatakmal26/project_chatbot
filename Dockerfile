FROM python:3.12-slim as builder

WORKDIR /app

COPY pyproject.toml pdm.lock* /app/
RUN pip install pdm
RUN pdm install --prod --no-editable

COPY . /app/
RUN pdm run python manage.py collectstatic --noinput

FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH="/app"

COPY --from=builder /app /app

RUN pip install pdm  



EXPOSE 8000
CMD ["pdm", "run", "gunicorn", "chatbot.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
