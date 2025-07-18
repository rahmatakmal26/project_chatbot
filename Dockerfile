FROM python:3.12-slim

WORKDIR /app

# Salin file dependencies
COPY pyproject.toml pdm.lock* /app/

# Install dependencies menggunakan pdm atau pip
RUN pip install pdm
RUN pdm install --prod

# Salin kode aplikasi setelah dependencies diinstall
COPY . /app/

# Jalankan collectstatic setelah semua siap
RUN pdm run python manage.py collectstatic --noinput

# Jalankan aplikasi dengan gunicorn
CMD ["pdm", "run", "gunicorn", "tga.wsgi:application", "--bind", "0.0.0.0:8000"]
