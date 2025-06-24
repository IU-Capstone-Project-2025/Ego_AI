# EgoAI Backend Developer Guide

Welcome to the team! This document is your "map" to the backend architecture. It will help you quickly understand not only **how** to write code but also **why** it's structured this way.

## 1. Key Philosophy: "Thin Controllers, Fat Services"

Our backend follows the **"Thin Controllers, Fat Services"** principle. This is our main law, ensuring code cleanliness, testability, and scalability.

*   **API Endpoints (`app/api/endpoints/`)**: Their sole purpose is to receive HTTP requests, validate input data using Pydantic, and call the corresponding service method. **They should contain no business logic.** They don't know how users or events are structured.
*   **Services (`app/services/`)**: **The heart of our application.** All business logic lives here. Access rights checks ("can this user edit this event?"), data processing, calling multiple CRUD operations for a single business task — all of this happens here.
*   **CRUD (`app/database/crud/`)**: Dumb as a hammer. This layer is responsible for only one thing — direct interaction with the database (Create, Read, Update, Delete). It knows nothing about business logic or HTTP requests.

## 2. Deep Dive into Architecture

### 2.1. Dependency Injection (DI) in FastAPI

You'll constantly see `... = Depends(...)` in endpoint functions. This is FastAPI's most powerful feature. It allows "injecting" dependencies (like DB session or current user) into your code.

*   **`db: AsyncSession = Depends(get_db)`**: Before executing the endpoint code, FastAPI calls the `get_db` function from `app/database/session.py`. It creates a new database session, "gives" it to the endpoint through `yield`, and after the endpoint finishes, **automatically closes this session**. This ensures each request has its isolated session, and we don't leave any "hanging" connections.
*   **`current_user: User = Depends(deps.get_current_user)`**: Similarly, FastAPI first calls `get_current_user` from `app/utils/deps.py`. This function extracts the JWT token from the `Authorization` header, validates it, finds the user in the DB, and returns their model. If the token is invalid or missing, this function throws an exception, and the request **doesn't even reach** our endpoint. This is our main API protection mechanism.

### 2.2. Asynchronicity (Async/Await)

All code is written using `async` and `await`. This allows our server to efficiently handle hundreds of simultaneous requests without blocking on I/O operations (like waiting for database responses).

**Golden Rule:** Any function that works with network or database (i.e., all functions in `services` and `crud` layers) must be asynchronous (`async def`), and all its internal DB calls must use `await` (`await db.execute(...)`). A missed `await` is a common cause of hard-to-catch bugs.

### 2.3. Centralized Error Handling

Notice that in services, we often throw `HTTPException` (`raise HTTPException(status_code=404, ...)`). We don't wrap this in `try...except` in endpoints. Why?

Because in `app/core/exception_handlers.py`, we've configured global exception handlers. FastAPI automatically catches these exceptions and converts them into proper HTTP responses. This allows us to keep endpoint code absolutely clean and focused on the main task.

## 3. Request Lifecycle (by Example)

Let's trace the path of a simple request to get an event: `GET /api/v1/events/{event_id}`.

1.  **Routing (`app/api/router.py`):** Request hits the main router, which directs it to `app.api.endpoints.v1.event.router`.
2.  **Endpoint (`app/api/endpoints/v1/event.py`):**
    *   Dependencies `Depends(get_current_user)` and `Depends(get_db)` trigger. We get the current user and DB session.
    *   An instance of `EventService(db)` is created and its method `await event_service.get_event_by_id(...)` is called.
3.  **Service Layer (`app/services/event.py`):**
    *   `await crud.event.get(db, id=event_id)` is called to get the event from the database.
    *   **Access Check:** `if event.owner_id != current_user.id: raise HTTPException(403, ...)`
    *   If everything is okay, the service returns the event object.
4.  **Response Return:** The endpoint receives the data, Pydantic automatically converts it to JSON, and the HTTP response is sent to the client.

## 4. How to Add New Functionality (Checklist)

Let's say you need to add a new entity "Tasks". Here are your steps:

1.  **DB Model:** Add `Task` to `app/database/models/models.py`.
2.  **Migration:** Create a new Alembic migration (`alembic revision --autogenerate -m "..."`) and apply it (`alembic upgrade head`).
3.  **Pydantic Schemas:** Define `TaskCreate`, `TaskUpdate`, `TaskInDB` schemas in `app/database/schemas/schemas.py`.
4.  **CRUD:** Create `app/database/crud/task.py` with basic functions.
5.  **Service:** Create `app/services/task.py` with `TaskService` class for business logic.
6.  **Endpoints:** Create `app/api/endpoints/v1/task.py` with a "thin" router.
7.  **Router:** Connect the new router in `app/api/router.py`.
8.  **Tests:** Write tests for `TaskService` and for the endpoint.

## 5. Testing Philosophy

*   **Test logic, not framework.** Our main goal is tests for the **service layer**. This is where all business logic and checks that can break are concentrated.
*   Tests for **API endpoints** are also needed, but their purpose is to verify that routing works, dependencies are injected, and Pydantic schemas validate data correctly. They are more like integration "smoke tests".
*   Use fixtures from `tests/conftest.py` to create test data (users, events) to keep your tests independent from each other.

## 6. Key Files to Study

*   `main.py`: Entry point, Middleware setup.
*   `app/core/config.py`: All application settings.
*   `app/utils/deps.py`: How dependencies work (especially `get_current_user`).
*   `app/services/event.py`: Good example of service layer implementation.
*   `app/api/endpoints/v1/event.py`: Example of a "thin" controller.

---

For detailed information about installation and launch commands, please refer to the main [README.md](./README.md). 