FROM python:3.12-slim as builder

WORKDIR /app

COPY pyproject.toml pdm.lock* /app/
RUN pip install pdm
RUN pdm install --prod

COPY . /app/
RUN pdm run python manage.py collectstatic --noinput

# Stage akhir (lebih ramping)
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /app /app

EXPOSE 8000
CMD ["pdm", "run", "gunicorn", "tga.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
