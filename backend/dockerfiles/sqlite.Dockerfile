# Базовый образ
FROM debian:bookworm-slim AS sqlite-builder
#
# Устанавливаем необходимые инструменты для сборки и использования SQLite
RUN apt-get update && apt-get install -y \
  gcc \
  make \
  wget \
  && rm -rf /var/lib/apt/lists/*

# Установка переменных
ENV CFLAGS="-DSQLITE_ENABLE_FTS3 \
  -DSQLITE_ENABLE_FTS3_PARENTHESIS \
  -DSQLITE_ENABLE_FTS4 \
  -DSQLITE_ENABLE_FTS5 \
  -DSQLITE_ENABLE_JSON1 \
  -DSQLITE_ENABLE_LOAD_EXTENSION \
  -DSQLITE_ENABLE_RTREE \
  -DSQLITE_ENABLE_STAT4 \
  -DSQLITE_ENABLE_UPDATE_DELETE_LIMIT \
  -DSQLITE_SOUNDEX \
  -DSQLITE_TEMP_STORE=3 \
  -DSQLITE_USE_URI \
  -O2 \
  -fPIC"
# ENV PREFIX="/usr/lib/x86_64-linux-gnu"

ENV PREFIX="/usr"

# Устанавливаем SQLite
WORKDIR /usr/src/sqlite

RUN wget --progress=dot:mega https://www.sqlite.org/src/tarball/sqlite.tar.gz -O sqlite.tar.gz \
  && tar -xvf sqlite.tar.gz

WORKDIR /usr/src/sqlite/bld

RUN ../sqlite/configure --help

RUN ../sqlite/configure --disable-tcl --enable-shared --prefix="$PREFIX" \
  && make


# Образ питона
FROM python:3.12-slim-bookworm AS py-builder

# Проверяем версию по умолчанию в python
RUN python -c "import sqlite3; print(sqlite3.sqlite_version)"

# Задаем рабочую директорию
WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir poetry \
  && poetry config virtualenvs.in-project true \
  && poetry install --only main --no-interaction --no-ansi \
  && rm -rf $(poetry config cache-dir)/{cache,artifacts}


FROM python:3.12-slim-bookworm

# Копируем SQLite из этапа сборки
COPY --from=sqlite-builder /usr/src/sqlite /usr/src/sqlite

WORKDIR /usr/src/sqlite/bld

# Устанавливаем 
RUN apt-get update && apt-get install -y make binutils \
  && rm -rf /var/lib/apt/lists/* \
  && make install \
  && cp /usr/lib/libsqlite3.so.0 /usr/lib/x86_64-linux-gnu/ \
  && rm * -r

# проверяем
RUN python -c "import sqlite3; print(sqlite3.sqlite_version)"


# копируем само приложение
COPY --from=py-builder /app /app

WORKDIR /app
ENV PATH="/app/.venv/bin:${PATH}"

COPY src/ ./src/

# ENTRYPOINT [ "python" ]
# CMD ["-m",\
#   "uvicorn",\
#   "src.main:app",\
#   "--host", "0.0.0.0",\
#   "--port", "5000" ]
