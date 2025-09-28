# Certify Backend

This is the backend for the Certify project, built with FastAPI and MongoDB.

## Prerequisites

- Python 3.10+
- pip
- MongoDB (local or remote)

## Setup

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Create a `.env` file with your MongoDB URI:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   PORT=8000
   ```
3. Start the development server:
   ```sh
   uvicorn src.main:app --reload --port 8000
   ```
4. The API will be available at `http://localhost:8000` by default.

## Deploying to Vercel

- See `vercel.json` for configuration. The entry point is `main.py`.
