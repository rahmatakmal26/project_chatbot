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

CMD ["pdm", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
