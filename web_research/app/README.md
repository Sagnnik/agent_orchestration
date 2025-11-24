# Web Research Agent Backend (FastAPI)

This directory contains the FastAPI backend for the Web Research Agent application. It exposes a set of RESTful APIs that allow the frontend (or any client) to initiate research tasks, track their progress, stream results, and manage the underlying AI agents.

## 🚀 Key Features

*   **Asynchronous Research:** Initiate long-running research tasks in the background without blocking the client.
*   **Real-time Streaming:** Receive research progress and LLM generated tokens in real-time via Server-Sent Events (SSE).
*   **Task Management:** Check the status and retrieve results of asynchronous research tasks.
*   **Research Cancellation:** Ability to cancel ongoing research tasks.
*   **Configurable Agents:** Dynamic configuration of LLM models and providers for research agents.
*   **Redis Integration:** Utilizes Redis for caching task statuses and check-pointing LangGraph states.

## 🗺️ Architecture Overview

The FastAPI application acts as an orchestrator, receiving requests from the frontend and coordinating with various backend services:

*   **API Endpoints (`app/api/routes.py`):** Defines all the exposed API endpoints for interacting with the research agent.
*   **Core Research Logic (`app/core/`):** Integrates with the LangGraph-based research agent (details in `app/core/README.md`). The backend calls the `run_agent` or `run_agent_streaming` functions from `app/core/agent.py`.
*   **Service Layer (`app/services/`):** Manages interactions with external services like Redis for caching (`app/services/cache.py`) and LangGraph check-pointing (`app/services/checkpointer.py`).
*   **Utilities (`app/utils/`):** Provides common utilities such as configuration loading (`app/utils/config.py`) and logging (`app/utils/logger.py`).

## ⚙️ Configuration

The backend uses environment variables for configuration, loaded from a `.env` file at the project root. Key configurations include:

*   `REDIS_URL`: Connection string for the Redis instance (e.g., `redis://localhost:6379/0`).
*   `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`, `TAVILY_API_KEY`: API keys for various LLM providers and search tools.
*   `LANGSMITH_TRACING`, `LANGSMITH_ENDPOINT`, `LANGSMITH_PROJECT`, `LANGSMITH_API_KEY`: Settings for LangSmith integration for tracing.
*   `DEBUG`: Boolean flag for debug mode.

## ⚡️ API Endpoints

All API endpoints are prefixed with `/api/v1`.

### `POST /api/v1/research`

Initiates a synchronous research task. This endpoint blocks until the research is complete. **Primarily for internal testing or specific use cases where blocking is acceptable.**

*   **Request Body:** `SearchRequest` model (see `app/models/models.py`)
    ```json
    {
        "query": "What are the recent advancements in AI?",
        "max_iteration": 5,
        "depth": "moderate",
        "model_provider": "openai",
        "model_name": "gpt-4o-mini",
        "api_key": "sk-..."
    }
    ```
*   **Response:**
    *   `200 OK`: Returns the final research report, citations, and metadata.
    *   `500 Internal Server Error`: If an error occurs during the research process.

### `POST /api/v1/research/async`

Initiates an asynchronous research task as a background process. The API returns immediately with a `task_id`, which can be used to poll for status and results.

*   **Request Body:** `SearchRequest` model
*   **Response:**
    *   `200 OK`:
        ```json
        {
            "task_id": "unique-task-id",
            "thread_id": "unique-thread-id",
            "status": "pending",
            "message": "Research task started. Use GET /research/status/{task_id} to check progress"
        }
        ```
    *   `500 Internal Server Error`: If an error occurs while starting the background task.

### `GET /api/v1/research/status/{task_id}`

Retrieves the current status and results (if completed) of an asynchronous research task.

*   **Path Parameter:** `task_id` (the ID returned by `/research/async`)
*   **Response:** `TaskStatusResponse` model (see `app/models/models.py`)
    *   `200 OK`:
        ```json
        {
            "task_id": "unique-task-id",
            "status": "completed", // or "pending", "processing", "failed"
            "created_at": "ISO-formatted datetime",
            "completed_at": "ISO-formatted datetime",
            "result": { ... final report data ... },
            "error": null
        }
        ```
    *   `404 Not Found`: If the `task_id` does not exist.
    *   `500 Internal Server Error`: If an error occurs while retrieving status.

### `POST /api/v1/research/stream`

Initiates a research task and streams progress events and LLM tokens using Server-Sent Events (SSE). This is ideal for real-time updates in a web UI.

*   **Request Body:** `SearchRequest` model
*   **Response:** `text/event-stream`
    *   Events will be JSON-formatted and include `type` (e.g., `started`, `node_start`, `node_end`, `token`, `completed`, `error`, `cancelled`).
    *   Example events:
        ```
        data: {"type": "started", "thread_id": "...", "query": "..."}

        data: {"type": "node_start", "node": "planner"}

        data: {"type": "token", "content": "..."}

        data: {"type": "node_end", "node": "synthesis_cite"}

        data: {"type": "completed", "thread_id": "..."}
        ```
    *   `500 Internal Server Error`: If an error occurs during stream initialization.

### `POST /api/v1/research/cancel/{thread_id}`

Requests the cancellation of an ongoing streaming research task.

*   **Path Parameter:** `thread_id` (the ID of the streaming task)
*   **Response:**
    *   `200 OK`:
        ```json
        {"status": "cancelled_requested", "thread_id": "..."}
        ```
    *   `404 Not Found`: If the `thread_id` does not exist.

### `GET /health`

Provides a simple health check endpoint to verify the backend and its connection to Redis are operational.

*   **Response:**
    *   `200 OK`:
        ```json
        {"status": "healthy", "redis": "connected"}
        ```
    *   `500 Internal Server Error`: If Redis connection fails.

### `GET /info`

Returns basic information about the application.

*   **Response:**
    *   `200 OK`:
        ```json
        {"app_name": "Web Researcher", "debug": true}
        ```

## 🛠️ Development

To run the FastAPI backend locally for development:

1.  **Ensure dependencies are installed:** `uv pip install -r requirements.txt` (or `pip install -r requirements.txt`)
2.  **Create a `.env` file** in the project root with your configuration.
3.  **Run the server:** `uvicorn app.main:app --reload`

The API documentation (Swagger UI) will be available at `http://localhost:8000/docs`.
