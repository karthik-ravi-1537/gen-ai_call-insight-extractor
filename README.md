# GenAI-Powered Conversation Insights Extraction

## Overview

This project processes debt collection conversation transcripts using an LLM to extract insights and generate summaries.
The repository contains both the backend and frontend code, making it a full-stack application.

- **Backend:** A FastAPI application that processes transcripts, generates insights, and exposes API endpoints.
- **Frontend:** A React application that provides a user interface for uploading transcripts and viewing call summaries.

## Summary

- The **backend** (FastAPI) and **frontend** (React) are organized under `/backend` and `/frontend`, respectively.
- Local development is facilitated by running the backend with Uvicorn and the frontend with npm.
- Deployment options include AWS for the backend and Vercel for the frontend, both of which offer free tiers up to a
  certain usage limit.

For further details or modifications, please refer to the individual documentation in each folder. Happy coding!

## Project Structure

gen-ai_call-insight-extractor/
├── backend/
│ ├── api/
│ │ ├── __init__.py
│ │ ├── call_api.py
│ │ └── transcript_api.py
│ ├── models/
│ │ ├── __init__.py
│ │ ├── base.py
│ │ ├── enums.py
│ │ ├── call.py
│ │ ├── transcript.py
│ │ └── insight.py
│ ├── services/
│ │ ├── __init__.py
│ │ ├── call_service.py
│ │ └── transcript_service.py
│ ├── __init__.py
│ ├── config.py
│ ├── database.py
│ ├── Dockerfile
│ ├── llm_client.py
│ ├── main.py
│ └── requirements.txt
├── frontend/
│ ├── public/
│ │ └── index.html
│ ├── src/
│ │ ├── App.js
│ │ └── index.js
│ ├── package.json
│ └── package-lock.json
├── README.md
└── run.sh

## Running the Application Locally

### Backend

1. **Set Up Your Environment:**
    - Create and activate a virtual environment:
      `python -m venv [name_of_venv]` # Replace [name_of_venv] with your desired name
      `source [name_of_venv]/bin/activate` # On Windows: `[name_of_venv]\Scripts\activate`

2. **Database Setup:**
    - The project uses SQLite by default (configured in `/backend/database.py`).
    - For Local development and testing, we allow the app to create a new database and/or load a pre-populated snapshot.
    - For Production, we will use a more robust database (PostgreSQL).

3. **Navigate to the Backend Directory:**
   `cd backend`

4. **Install Python dependencies:**
   `pip install -r requirements.txt`

4. **Run the Server:**
    - From the backend directory, run:
      `uvicorn main:app --reload`

    - The backend API will be available at `http://127.0.0.1:8000`

### Frontend

1. **Navigate to the Frontend Directory:**
   `cd frontend`

2. **Install Dependencies:**
   `npm install`

3. **Configure Environment Variables:**
    - In the frontend `.env` file, set the backend URLs:
      `REACT_APP_BACKEND_URL=http://localhost:8000`
      `REACT_APP_API_PREFIX=/api/v1`

4. **Run the Frontend:**
   `npm start`

    - The frontend application will launch at `http://localhost:3000`

## Deployment

### Backend Deployment on AWS

- **Containerization:**  
  Create a Dockerfile in the `/backend` directory and containerize your FastAPI application.

- **Deployment Options:**  
  Use AWS Elastic Beanstalk, AWS Lambda/API Gateway (with a container image), or AWS Fargate. Make sure to configure
  environment variables and set up CORS properly so that your frontend can access the backend API.

- **Database:**  
  Consider using a managed database (e.g., Amazon RDS) for production or provide a snapshot for testing purposes.

### Frontend Deployment on Vercel

- **Repository Integration:**  
  Push your frontend code (contents of `/frontend`) to GitHub.

- **Vercel Setup:**  
  Sign up on Vercel, import your repository, and set the environment variables to the public URL of
  your deployed backend.

- **Automatic Deployment:**  
  Vercel will automatically deploy your frontend on every push to the connected repository.

## Development Setup

### Reference Files

For convenience, reference versions of files that are normally git-ignored are stored in the `/backend/setup/` and
`/frontend/setup/` directory
with a `_setup` suffix:

- `/backend/setup/.env_setup` - Template for environment variables
    - Intended Location: `/backend/.env`

- `/backend/setup/call_insights.db_setup` - Sample database file
    - Intended Location: `/backend/call_insights.db`

- `/frontend/setup/.env_setup` - Template for environment variables
    - Intended Location: `/frontend/.env`

To use these files:

1. Copy the file from `/setup/` folder to the appropriate location.
2. Remove the `_setup` suffix.
3. Update any placeholder values as needed.

#### Example Setup

```
# Set up environment variables
cp backend/setup/.env_setup backend/.env # Then edit .env to add your actual API keys (especially LLM_API_KEY)
cp frontend/setup/.env_setup frontend/.env

# Set up database (if using the sample)
cp backend/setup/call_insights.db_setup backend/call_insights.db
```