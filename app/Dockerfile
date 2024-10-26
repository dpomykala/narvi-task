# A simple Dockerfile for demo purposes - not suitable for production

FROM --platform=linux/amd64 python:3.13-slim

ARG POETRY_VERSION
ARG POETRY_VIRTUALENVS_IN_PROJECT
ARG POETRY_NO_INTERACTION
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app

COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root

COPY /src /app

COPY entrypoint.sh /bin/entrypoint.sh
RUN chmod +x /bin/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/bin/entrypoint.sh"]

CMD ["poetry", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
