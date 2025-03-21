# GenAI-Powered Conversation Insights Extraction

## Overview

This project processes debt collection conversation transcripts using an LLM to extract insights and generate summaries.
The repository contains both backend and frontend components, making it a full-stack application.

- **Backend:**
    - A FastAPI application that processes transcripts, generates insights, and exposes API endpoints.
- **Frontend:**
    - A Streamlit application that provides a user interface for uploading transcripts and viewing call
      summaries.
    - [Obsolete] A React application that provides a user interface for uploading transcripts and viewing call
      summaries.

## Project Structure (w/o Git-ignored Files)

```
gen-ai_call-insight-extractor/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── call_api.py
│   │   └── transcript_api.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── enums.py
│   │   ├── call.py
│   │   ├── transcript.py
│   │   └── insight.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── call_service.py
│   │   └── transcript_service.py
│   ├── setup/
│   │   ├── .env_setup
│   │   └── call_insights.db_setup
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── Dockerfile
│   ├── llm_client.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.js
│   │   └── index.js
│   ├── setup/
│   │   └── .env_setup
│   ├── package.json
│   └── package-lock.json
├── streamlit/
│   ├── .streamlit/
│   │   └── secrets.toml
│   ├── setup/
│   │   ├── sample_transcripts/
│   │   │   └── ...
│   │   └── secrets.toml_setup
│   └── streamlit_app.py
├── .gitignore
└── README.md
```

## Running the Application Locally

### Backend

1. **Set Up Your Environment:**
    - Create and activate a virtual environment:
        - `python -m venv [name_of_venv]`  # Replace [name_of_venv] with your desired name
        - `source [name_of_venv]/bin/activate`  (Windows: `[name_of_venv]\Scripts\activate`)

2. **Database Setup:**
    - The project uses SQLite by default (configured in `/backend/database.py`).
    - For local development and testing, the app can create a new database and/or load a pre-populated snapshot.
    - For production, a more robust database like PostgreSQL is recommended.

3. **Navigate to the Backend Directory:**
    - `cd backend`

4. **Install Python dependencies:**
    - `pip install -r requirements.txt`

5. **Run the Server:**
    - From the backend directory, run:
        - `uvicorn main:app --reload`
    - The backend API will be available at `http://127.0.0.1:8000`

### Frontend (Streamlit)

1. **Install Streamlit:**
    - `pip install streamlit`

2. **Run the Streamlit App:**
    - `cd streamlit`
    - `streamlit run streamlit_app.py`

    - The Streamlit interface will be available at `http://localhost:8501`

### Frontend (React) [Obsolete] [Ignore]

1. **Navigate to the Frontend Directory:**
    - `cd frontend`

2. **Install Dependencies:**
    - `npm install`

3. **Configure Environment Variables:**
    - In the frontend `.env` file, set the backend URLs:
        - `REACT_APP_BACKEND_URL=http://localhost:8000`
        - `REACT_APP_API_PREFIX=/api/v1`

4. **Run the Frontend:**
    - `npm start`
    - The React application will launch at `http://localhost:3000`

## Deployment

### [Backend] Railway Deployment (railway.app)

- **Railway Setup:**
    - Create a new project on Railway and connect it to your GitHub repository containing the backend code.
    - Set the root directory to `/backend` in the Railway project settings.
    - Railway will automatically detect the `Dockerfile` in the `/backend` directory and build the application.

- **Database:**
    - Railway provides a PostgreSQL database option, which is easy to set up and manage.
    - We can set up one for Production usage, and optionally another one for development/testing.

- **Environment Variables:**
    - Set up the environment variables in the Railway service, including...
        - `LLM_API_KEY`
        - `DATABASE_URL` (pointing to your PostgreSQL database)
        - `FRONTEND_URL` (pointing to your deployed frontend)
        - and any other necessary keys mentioned in the `.env_setup` file in the `/setup` directory.

### [Frontend] Streamlit Deployment (streamlit.io)

- **Streamlit Cloud:**
  Deploy the Streamlit application using Streamlit Cloud for a simple, managed solution.

- **GitHub Integration:**
  Connect your GitHub repository containing the Streamlit app to Streamlit Cloud.

- **Environment Variables:**
    - Set up the environment variables (known as Secrets) in the Streamlit Cloud service, including...
        - `BACKEND_URL` (pointing to your deployed backend)
        - `API_PREFIX`
        - and any other necessary keys mentioned in the `secrets.toml_setup` file in the `/setup` directory.

- **Alternative Deployment:**
  The Streamlit app can also be deployed on AWS, Heroku, or other cloud platforms that support Python applications.

### [Backend] Deployment on AWS [Obsolete] [Ignore]

- **Note:**
    - This section is obsolete and should be ignored. The recommended deployment method is now Railway.
    - However, if you wish to deploy on AWS, you can follow the instructions below.

- **Containerization:**
  Create a Dockerfile in the `/backend` directory and containerize your FastAPI application.

- **Deployment Options:**
  Use AWS Elastic Beanstalk, AWS Lambda/API Gateway (with a container image), or AWS Fargate. Make sure to configure
  environment variables and set up CORS properly so that your frontend can access the backend API.

- **Database:**
  Consider using a managed database (e.g., Amazon RDS) for production or provide a snapshot for testing purposes.

### [Frontend] React Deployment on Vercel [Obsolete] [Ignore]

- **Note:**
    - This section is obsolete and should be ignored. The recommended deployment method is now Streamlit Cloud.
    - The React frontend code is no longer actively maintained, but if you wish to deploy it, you can follow the
      instructions below.

- **Repository Integration:**
  Push your frontend code (contents of `/frontend`) to GitHub.

- **Vercel Setup:**
  Sign-up on (or sign-in to) Vercel, import your repository, and set the environment variables to the public URL of
  your deployed backend.

- **Automatic Deployment:**
  Vercel will automatically deploy your frontend on every push to the connected repository.

## Development Setup

### Reference Files

For convenience, reference versions of files that are normally git-ignored are stored in the `/setup/` directories of
respective codebases with a `_setup` suffix:

- `/backend/setup/.env_setup` - Template for environment variables
    - Intended Location: `/backend/.env`

- `/backend/setup/call_insights.db_setup` - Sample database file
    - Intended Location: `/backend/call_insights.db`

- `/streamlit/setup/secrets.toml_setup` - Template for Streamlit secrets
    - Intended Location: `/streamlit/.streamlit/secrets.toml`

- `/frontend/setup/.env_setup` - Template for environment variables
    - Intended Location: `/frontend/.env`

To use these files:

1. Copy the file from `/setup/` folder to the appropriate location.
2. Remove the `_setup` suffix.
3. Update any placeholder values as needed.

### Example Setup

**Set up environment variables**

- `cp backend/setup/.env_setup backend/.env` # Then edit .env to add your actual API keys (especially LLM_API_KEY)
- `cp streamlit/setup/secrets.toml_setup streamlit/.streamlit/secrets.toml`
- `cp frontend/setup/.env_setup frontend/.env`

**Set up database (if using the sample)**

- `cp backend/setup/call_insights.db_setup backend/call_insights.db`
