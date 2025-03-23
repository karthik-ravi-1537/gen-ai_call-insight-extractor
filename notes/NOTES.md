# Notes

## Index

- [Technical Overview](#technical-overview)
- [Architecture Decisions](#architecture-decisions)
- [Database Design](#database-design)
- [Infrastructure](#infrastructure)
- [Code Organization](#code-organization)
- [LLM Integration](#llm-integration)
- [User Experience](#user-experience)
- [Development Experience](#development-experience)
- [Notes of Data](#notes-of-data)
- [Approach](#approach)
- [Enhancement List](#enhancement-list)
- [ToDo](#todo)

## Technical Overview

The Call Insight Extractor is a Modular (between Monolithic and Microservices) codebase designed to process call
transcripts, extract insights, and provide a
simple user interface for interaction. The system is built using FastAPI for the backend and Streamlit for the frontend,
with a focus on ease of use, rapid development, and deployment.

## Architecture Decisions

1. **Modular Architecture** - Backend and frontend are separated to enable independent development and scaling. Modules
   within the Backend are structured in a way that they can be made into individual microservices if needed in the
   future.
    - **Monolithic vs Microservices** - The current architecture is a hybrid, allowing for easy refactoring into
      microservices if needed later.
2. **API-First Design** - Backend exposes RESTful APIs to enable multiple frontend options (both Streamlit and React).
3. **FastAPI Backend** - Chosen for high performance, ease of usage, automatic OpenAPI docs, and type validation.
4. **Streamlit Frontend** - Simple, Python-based UI for rapid development of data-focused applications.

## Database Design

1. **SQLite for Development, PostgreSQL for Production** - Evident from commented-out connection strings, supports easy
   local development with production readiness.
2. **Domain-Driven Design** - Database schema is designed around the domain of call transcripts and insights, with clear
   relationships
   between entities.
    - **Call** - Represents a single call, with a unique ID and associated metadata.
    - **Transcript** - Each call can have multiple transcripts, allowing for flexibility in processing different parts
      of
      the call.
    - **Insight** - Each transcript has one insight, representing the extracted information from that transcript.
3. **Status Tracking** - Call status field allows tracking progress through the processing pipeline.
4. **Enum for Call Status** - Use of enumerations for call status (e.g., "pending", "processed") to ensure consistency
   and clarity in the database schema.
5. **Audit Mixin** - Use of an audit mixin to track creation and update timestamps for all database entities, ensuring
   accountability and traceability.
6. **History Tracking** - A simple version is implemented to track additions/modifications to Insights, allowing for
   historical analysis of changes over time. The same can be extended to track changes to other entities if needed with
   the use of dedicated 'history' tables.

## Infrastructure

1. **Ease of Backend Deployment** - Use of Railway for deployment simplifies setup and CI/CD processes, allowing for
   quick iterations and updates.
    1. **Backend on Railway** - Modern PaaS that simplifies CI/CD compared to more complex alternatives like AWS.
        1. **PostgreSQL on Railway** - Chosen for production database, ensuring compatibility with local SQLite
           development.
        2. **Environment Variables for Configuration** - Use of environment variables for sensitive data (e.g., database
           connection strings) to enhance security and flexibility.
    2. **Frontend of Streamlit** - Deployed on Streamlit Cloud for rapid deployment and easy access to/sharing of the
       application.
2. **Environment Configuration** - Extensive use of environment variables across Backend and Frontend to minimize the
   need for deployments, with setup templates for quick local development.
3. **Docker Support** - Dockerfile indicates containerization for consistent deployment.

## Code Organization

1. **Clear Module Separation** - API, models, and services layers are separated to maintain clear responsibility
   boundaries.
2. **Setup Directory** - Contains templates for configuration files to simplify onboarding for new developers.
3. **Enums for Standardization** - Using enumerations for statuses and other categorical data to ensure consistency.

## LLM Integration

1. **OpenAI Integration** - Using GPT-4 for text processing with temperature 0.0 for highly deterministic results.
2. **Configurable LLM Parameters** - Model type and temperature are configurable via environment variables.
    1. Model type can be changed to other models (e.g., GPT-3.5) by modifying the environment variable `LLM_MODEL_TYPE`.
    2. Temperature can also be adjusted via the environment variable `LLM_TEMPERATURE` for different levels of
       creativity in responses.
3. **Fallback Handling** - Graceful handling of LLM failures by returning a default message instead of crashing the
   application.

## User Experience

1. **Transcript Upload UI** - Simple interface for uploading transcript files.
2. **Downloadable Transcripts** - Backend serves transcript files for download via Frontend for easy testing and
   demonstration.
3. **Call Summary(s) Listing** - Display of extracted insights and summaries for each call, allowing users to review and
   edit as
   needed.
4. **Insight Display** - Structured extraction of payment information and summaries from call transcripts.
5. **Health Check Endpoint** - Simple way to verify backend availability from frontend.

## Development Experience

1. **Local Development Focus** - Setup instructions and configuration templates emphasize ease of local development.
2. **Comprehensive README** - Detailed documentation for setup, structure, and deployment.
3. **Sample Data** - Provision of sample transcripts and database for testing.
4. **Hot Reload** - Backend uses `--reload` flag for faster development cycles.

## Notes of Data

1. Customer can deny payments as well. That isn't covered.
2. Ignoring unhappy and ignored paths, to focus on the core development.

## Approach

1. Handle functional requirements first, ensuring the core functionality of the system is robust and reliable.
2. Focus on user experience, making the interface intuitive and easy to navigate.
3. Iterate on the design and functionality based on user feedback and testing, ensuring continuous improvement.
4. Document all changes and decisions made during the development process to maintain clarity and facilitate future
   enhancements.
5. Ensure that the system is modular and extensible, allowing for easy integration of new features and improvements
   as needed.
6. Prioritize maintainability and readability of the codebase, following best practices and design patterns to ensure
   long-term sustainability of the project.
7. Consider scalability from the outset (but not be limited too much by it), ensuring that the architecture can handle
   increased load and complexity as the system evolves.

## Enhancement List

- [X] Fix the issue of call processing with multiple transcripts. The summaries outputs are not as expected.
- [X] Address the problem with the download link for transcripts not functioning as expected.
- [X] Resolve the issue with the health check endpoint not returning the expected status when the backend is down.
- [X] Make the Call ID on the UI human-readable.
- [X] Make all API layer code not call the DB directly. Instead, use the Service layer to handle all database
  interactions to maintain a clear separation of concerns and improve code maintainability.
    - [X] Refactor the API layer to call the Service layer for all database interactions, ensuring a consistent approach
      across the application.
    - [X] Perhaps consider introducing Repository layer as well.
- [ ] Implement thorough logging across the application to capture important events and errors for easier
  debugging and monitoring.
- [ ] Add a retry mechanism with exponential backoff for the LLM calls to handle transient errors and improve
  resilience. Perhaps extend that to all API calls as well.
- [X] Have upload_call API call process_call, and have that call process_transcript to ensure a clear flow of
  processing from upload to insight extraction.
    - [X] API -> Service -> Repository flow for all API calls to ensure a consistent approach across the application.
    - [X] Background Tasks are queues in the API Layer after all Service calls are made to ensure that the processing
      is done in the background and does not block the API response.
    - [X] Have the Background Tasks handled in the Service layer to maintain a clear separation of concerns and improve
      code maintainability.
- [ ] Have service layer return responses in a consistent format, including success/failure status and any relevant
  messages or data. Currently, it returns objects directly, which can lead to confusions with actual API responses.
    - Example: /generate_refined_summary flow. Service returns Insight, but can return a dict with status and message.
        - { "status": "success", "message": "Success message", "data": Insight }
        - { "status": "error", "message": "Error message", "data": None }

## ToDo

- [X] Showcase V1, V2, V3, and so on.
    - [X] V1: Basic functionality with transcript upload and insight extraction.
        - Basic UI.
        - Basic API endpoints for uploading transcripts and retrieving insights.
    - [X] V2: Enhanced user interface with better navigation and usability.
        - Modern UI based out of Streamlit.
        - AWS Elastic Beanstalk deployment for the backend.
    - [X] V3: Full deployment with Docker and Railway.
        - Opted for Railway for ease of deployment and CI/CD.
    - [X] V4: Enhancing Streamlit UI to be more user-friendly and visually appealing.
        - Improved layout and design for better user experience.
        - Added Sample Transcripts for testing and demonstration purposes.
        - Added a health check endpoint to verify backend availability.
        - Added a download link for transcripts to allow users to retrieve their uploaded files.
    - [X] V4: Advanced features like user summaries.
    - [X] V5: Domain based Data Model refinements.
    - [X] V6: Minor tweaks and bug-fixes.
    - [ ] V7: Integration of additional LLMs and hot-swapping capabilities.
- [X] Review and refine the notes on data to ensure clarity and completeness.
- [X] Ensure that all sections are well-organized and easy to navigate for future reference.
- [X] Implement the User Summary feature to allow users to edit the extracted summaries for better accuracy and
  relevance.
- [ ] Update the README to reflect any changes made in this document.
- [ ] Add a flowchart to visualize the different paths (Happy Path, Semi-Happy Path, Unhappy Path, Ignored Path).
- [ ] Complete System Design diagram.
- [ ] [Stretch Goal] Add Diarization and Transcription features to add prior pieces of the pipeline to the system for a
  more complete
  solution.
- [ ] Consider implementing a more robust error handling and logging mechanism to capture and analyze failures in the
  insight extraction process.
- [ ] Add LLM hot-swapping capabilities to allow for easy switching between different models or configurations without
  downtime.
- [ ] Tweaks the LLM Prompts to improve the quality of the extracted insights and summaries.
    - [ ] If payment is collected on call, or if the commitment is made for today.