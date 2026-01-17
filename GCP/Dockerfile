# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Copy the uv binary from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Allow statements and errors to be immediately logged to the Cloud Run logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME

# Install production dependencies using uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project --no-cache

# Copy the rest of the application
COPY . ./
RUN uv sync --no-dev --no-cache

# Run the web service on container startup using uv run to use the venv
CMD ["uv", "run", "python", "src/main.py"]
