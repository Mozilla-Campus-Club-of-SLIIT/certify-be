FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy only the requirements file first to cache dependency installation
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application src
COPY src ./src

# Document the port the application listens on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]