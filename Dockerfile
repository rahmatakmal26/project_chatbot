FROM python:3.12-slim

WORKDIR /app

# Install pdm
RUN pip install pdm

# Copy file dependency dulu
COPY pyproject.toml pdm.lock* /app/

# Install dependencies
RUN pdm install --prod

# Copy seluruh kode aplikasi
COPY . /app/

# Kumpulkan file statis
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Jalankan aplikasi dengan gunicorn
CMD ["pdm", "run", "gunicorn", "tga.wsgi:application", "--bind", "0.0.0.0:8000"]
