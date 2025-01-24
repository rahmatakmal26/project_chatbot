FROM python:3.12

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY pyproject.toml pdm.lock README.md ${APP_HOME}/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir pdm \
    && pdm install --prod \
    && pdm add nltk

ENV PATH="/app/.venv/bin:$PATH"

COPY . ${APP_HOME}

EXPOSE 8000

CMD ["pdm", "run", "python", "manage.py", "runserver", "0.0.0.0:8000","--noreload"]
# CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]




# FROM python:3.12

# ARG APP_HOME=/app
# WORKDIR ${APP_HOME}

# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# COPY pyproject.toml pdm.lock README.md ${APP_HOME}/
# RUN pip install --upgrade pip \
#     && pip install --no-cache-dir pdm \
#     && pdm install --prod 


 
# ENV PATH="/app/.venv/bin:$PATH"

# COPY . ${APP_HOME}

# EXPOSE 8000

#   CMD ["pdm", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]