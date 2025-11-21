# API Documentation

## Base URL
`http://localhost:8000`

## Authentication
Currently, the API is open. Future versions will implement OAuth 2.0.

## Endpoints

### 1. Generate Travel Guide
Generates a comprehensive travel guide for a specific destination.

-   **URL**: `/api/generate`
-   **Method**: `POST`
-   **Content-Type**: `application/json`
-   **Request Body**:
    ```json
    {
        "destination": "Tokyo",
        "language": "en"
    }
    ```
-   **Success Response (200 OK)**:
    ```json
    {
        "status": "success",
        "destination": "Tokyo",
        "data": { ... },
        "timestamp": "2025-01-01T12:00:00"
    }
    ```
-   **Error Response (400 Bad Request)**:
    ```json
    {
        "detail": "Error message"
    }
    ```

### 2. Stream Travel Plan (SSE)
Streams real-time updates as agents work on the travel plan.

-   **URL**: `/api/stream`
-   **Method**: `GET`
-   **Query Parameters**:
    -   `destination` (string): The city or country to visit.
    -   `mother_tongue` (string, optional): Language code (default: "en").
-   **Response**: `text/event-stream`
    -   Events: `start`, `agent_start`, `agent_complete`, `agent_error`, `complete`.

### 3. Get Supported Languages
Returns a list of supported languages for the guides.

-   **URL**: `/api/languages`
-   **Method**: `GET`
-   **Success Response (200 OK)**:
    ```json
    {
        "status": "success",
        "languages": ["en", "es", "fr", "de", "it", "ja", "zh", "hi"],
        "count": 8
    }
    ```

### 4. Health Check
Checks if the API server is running.

-   **URL**: `/health`
-   **Method**: `GET`
-   **Success Response (200 OK)**:
    ```json
    {
        "status": "healthy",
        "service": "Cerebras AI Agent Army",
        "version": "1.0.0",
        "timestamp": "..."
    }
    ```
