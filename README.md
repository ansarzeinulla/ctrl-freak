# ctrl-freak

This project contains a backend service, a frontend widget, and an AI text generation service.

## Project Structure
```
ctrl-freak/
├── backend/
│   ├── db.py         # Script for direct database interaction
│   └── main.py       # Main backend application (e.g., Flask/FastAPI)
├── frontend/
│   └── index.html    # Host page for the frontend widget
├── ai_service/
│   └── gemini.py     # Service for interacting with Google Gemini
├── venv/             # Python virtual environment
├── .env              # Environment variables (e.g., API keys)
└── readme.md         # This file
```

## Setup

1.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    ```
    *   On macOS/Linux:
        ```bash
        source venv/bin/activate
        ```
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Running the Application

1.  **Run the Backend Server:**
    Open a terminal, navigate to the project root, and run:
    ```bash
    uvicorn backend.main:app --reload --port 8000

    newer version: PYTHONIOENCODING=UTF-8 uvicorn backend.main:app --reload --port 8000
    ```
    This will start the FastAPI backend server on `http://127.0.0.1:8000`.

2.  **Serve the Frontend:**
    Open a *second* terminal, navigate to the `frontend` directory, and run a simple HTTP server:
    ```bash

    python -m http.server 8080
    ```
    You can now access the `index.html` page at `http://localhost:8080`.


just docker-compose up --build