# Образ питона
FROM python:3.12-slim-bookworm AS py-builder

# Задаем рабочую директорию
WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry \
  && poetry config virtualenvs.in-project true \
  && poetry install --only main --no-interaction --no-ansi \
  && rm -rf $(poetry config cache-dir)/{cache,artifacts}



FROM python:3.12-slim-bookworm

# копируем само приложение
COPY --from=py-builder /app /app

WORKDIR /app
ENV PATH="/app/.venv/bin:${PATH}"

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.bot"]
