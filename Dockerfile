FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:0.8.11-debian-slim
LABEL authors="forestcat"

WORKDIR /app

# Copy project files
COPY . .

# Install dependencies from pyproject.toml/uv.lock
RUN uv sync
RUN apt-get update && apt-get install ca-certificates -y

# Create data volume
VOLUME ["/data"]
ENV DATABASE_FILENAME="/data/zitate_database.sqlite"

ENTRYPOINT ["uv", "run", "app/main.py"]