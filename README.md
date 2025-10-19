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

## Building and Running the Project

### The Old Way (Not Recommended)

These instructions are for running the services directly on your host machine. This method is less portable and can lead to environment inconsistencies.

1.  **Create and activate a virtual environment:**
    A virtual environment isolates the project's Python dependencies.
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

3.  **Run the Backend Server:**
    Open a terminal, navigate to the project root, and run:
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    For newer versions, you might need to specify the encoding:
    ```bash
    PYTHONIOENCODING=UTF-8 uvicorn backend.main:app --reload --port 8000
    ```
    This will start the FastAPI backend server on `http://127.0.0.1:8000`.

4.  **Serve the Frontend:**
    Open a *second* terminal and run:
    ```bash
    python -m http.server 8080
    ```    You can now access the `index.html` page at `http://localhost:8080/frontend/`.

### The Modern Way with Docker

This is the recommended method for building and running the application. It uses Docker to create a consistent and isolated environment for each service.

1.  **Build and run the services:**

ATTENTOIN: in .env of parent directory you must have # Your Google API Key for the AI service
GOOGLE_API_KEY="Your Google API Key from ai.studio "

    ```bash
    docker-compose up --build
    ```
    This command will:
    *   Read the `docker-compose.yml` file.
    *   Build a Docker image for each service defined in the file, based on its respective `Dockerfile`.
    *   Create and start containers for each service.

### DockerFile Roles

*   `backend/Dockerfile`: This builds the image for the Python backend service, installing its dependencies and defining the command to start the Uvicorn server.
*   `frontend/Dockerfile`: This builds the image for the frontend, typically using a lightweight web server like Nginx to serve the static `index.html` file and other assets.
*   `ai_service/Dockerfile`: This builds the image for the AI text generation service, setting up its environment and dependencies to interact with Google Gemini.

## Additional Checks

### Health Check

To verify that the backend service is running correctly, you can perform a health check:

```bash
python health/main.py
```

```bash
curl http://localhost:8000/health
```
Alternatively, if the health check is exposed through the `main.py` script, you can run:



### Dashboard Check-up

To see the employer dashboard, navigate to the `employer` directory and run the dashboard application. This procedure is not part of the Docker setup.
```bash
cd employer
python app.py
```
This will open a dashboard on another page.