FROM python:3.11-slim

# Environment variables for better Python behavior in containers:
# - PYTHONDONTWRITEBYTECODE: prevents creation of .pyc files
# - PYTHONUNBUFFERED: ensures logs are written immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install required system-level dependencies
# Clean up apt cache to reduce final image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libjpeg62-turbo-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy only the requirements file first to cache dependency installation
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create a non-root user before copying app files so we can set ownership on copy
RUN useradd --create-home appuser

# Copy app files and set ownership
COPY --chown=appuser:appuser . /app

# Switch to the non-root user
USER appuser

# Document the port the application listens on
EXPOSE 8000

# Start the application
# Runs the FastAPI app using Uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
