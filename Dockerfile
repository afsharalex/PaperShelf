# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (without dev dependencies)
RUN poetry install --no-interaction --no-ansi --no-dev --no-root

# Copy the rest of the application
COPY . .

# Install the application
RUN poetry build && pip install dist/*.whl

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Copy installed packages and application from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/papershelf /app/papershelf

# Create a non-root user to run the application
RUN useradd -m appuser
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create directory for database persistence
RUN mkdir -p /app/data/chroma_db
ENV DB_PERSIST_DIRECTORY=/app/data/chroma_db

# Expose the API port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "papershelf.api.app:app", "--host", "0.0.0.0", "--port", "8000"]