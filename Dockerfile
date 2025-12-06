FROM python:3.12-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache gcc postgresql-client musl-dev postgresql-dev

# Install Poetry
RUN pip install poetry

# Copy pyproject.toml, poetry.lock, and README.md
COPY pyproject.toml poetry.lock README.md ./

# Install Python dependencies
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copy the entire project
COPY . .

# Expose the port
EXPOSE 5001

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Run the application
CMD ["python", "src/index.py"]
