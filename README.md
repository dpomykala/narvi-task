# Grouping names API

## Quick start

Required dependencies:
- Git
- Docker Compose
- Make

1. Clone the repository:
```
git clone git@github.com:dpomykala/narvi-task.git
```

2. Navigate to the project directory:
```
cd narvi-task
```

3. Run tests:
```
make tests
```

4. Start the application:
```
make up
```

> [!NOTE]
> For demo purposes only: The application starts with a clean database each time.

## Discovering API

To play with the API in a browser you can use:
- DRF Browsable API: http://localhost:8000/api/
- Swagger UI: http://localhost:8000/api/docs/
- Redoc: http://localhost:8000/api/redoc/

> [!WARNING]
> For demo purposes only: API auth and permissions are disabled.

## API endpoints and workflow

To create grouping task use the list endpoint with the POST HTTP method:
```
POST /api/grouping-tasks/ HTTP/1.1

{
    "input_data": {
        "names": [
            "foo",
            "foo-bar",
            "foo-baz",
            "xyz"
        ],
        "word_delimiter": "-"
    }
}
```

- For brevity, HTTP headers are not shown in the examples.
- Optionally, you can specify a custom delimiter for splitting names into words.
- If a delimiter is not specified, default value (`_`) is used.

On success, the API responds with the URL for the created grouping task:
```
HTTP/1.1 201 Created

{
    "url": "http://127.0.0.1:8000/api/grouping-tasks/1/"
}
```

> [!NOTE]
> For simplicity, grouping is run synchronously when creating a new grouping task. In
> a real project it would be run as an asynchronous task (e.g. using Celery). In that
> case, the grouping task may not have been completed yet.

You can list all grouping tasks using the GET HTTP method:
```
GET /api/grouping-tasks/ HTTP/1.1
```

The API returns the following response:
```
HTTP/1.1 200 OK

[
    {
        "url": "http://127.0.0.1:8000/api/grouping-tasks/1/"
    }
]
```

You can now use the detail endpoint with the GET HTTP method to retrieve information
for the created grouping task:
```
GET /api/grouping-tasks/1/ HTTP/1.1
```

The API returns the following response:
```
HTTP/1.1 200 OK

{
    "completed_at": "2024-10-26T10:57:56.940381Z",
    "created_at": "2024-10-26T10:57:56.935820Z",
    "result": {
        "foo": [
            "foo",
            "foo-bar",
            "foo-baz"
        ],
        "xyz": [
            "xyz"
        ]
    },
    "updated_at": "2024-10-26T10:57:56.940424Z",
    "url": "http://127.0.0.1:8000/api/grouping-tasks/4/"
}
```

- The `result` object might be empty if the grouping task has not been completed yet.
- The `completed_at` might be `null` if the grouping task has not been completed yet.
- The front end can periodically retry the request to check if the grouping task is
completed.

Lastly, you can move names between groups using the move-name detail endpoint with the
PATCH HTTP method. E.g. to move the name `xyz` from the group `xyz` to `foo`:
```
PATCH /api/grouping-tasks/4/move-name/ HTTP/1.1

{
    "name": "xyz",
    "source_group": "xyz",
    "target_group": "foo"
}
```

The API responds with the full representation of the updated grouping task:
```
HTTP/1.1 200 OK

{
    "completed_at": "2024-10-26T10:57:56.940381Z",
    "created_at": "2024-10-26T10:57:56.935820Z",
    "result": {
        "foo": [
            "foo",
            "foo-bar",
            "foo-baz",
            "xyz"
        ]
    },
    "updated_at": "2024-10-26T11:21:31.045268Z",
    "url": "http://127.0.0.1:8000/api/grouping-tasks/4/"
}
```

- If the `target_group` does not exist, it will be created. **This allows to create new
groups.**
- Empty groups are not allowed - you can't create a new group without moving some name
into it.
- If the `source_group` is empty after moving the name, it will be deleted.
- If the `source_group` is not found, the error is returned.
- If the `name` is not found inside the `source_group`, the error is returned.

## TODOs and some things to consider for production

- Auth and permissions:
  - Who can create new grouping tasks?
  - Is the API intended only for a frond-end client or will it be used by other
  consumers?
  - We might want to store a relation to the user who created a grouping task.
  - User should only be allowed to see/update the grouping tasks he owns.
- How many grouping tasks are we expecting?
- What is the average size of the input data for a single grouping task? 
- Deployment:
  - Use a complete, production-ready Docker Compose setup:
    - Different environments for local, staging and prod.
    - Add services:
      - postgres
      - celery workers
      - redis (as a message broker and optionally as a cache backend)
      - nginx
    - Add volumes:
      - Persistent data (db)
      - Source code - for local development
    - Use a multi-stage build.
    - Do not run the application as a root inside a container.
  - CI/CD (Jenkins, GitHub Actions)?
  - If there is a need for scaling up, use something like Kubernetes in a cloud?
- Tooling:
  - Use the pre-commit framework for automating common tasks (formatting, linting etc.).
  - Configure more rules for Ruff linting.
  - Use pytest instead of unittest.
  - Configure coverage reports for tests.
  - Use a static type checker (e.g. mypy).
  - Consider using uv instead of Poetry?

## Scaling the application up

- If the bottleneck is the number of new grouping tasks, we can scale up the number
of celery workers used for processing.
- If the processing of a single grouping task is also a problem (large number of names
to be grouped), we can use distributed microservices.
- We can use a separate microservices for receiving input data (names) and splitting
these names into batches (e.g. grouping by the first letter).
- We can use something like Kafka to store batches of names in separate topics.
- Different type of microservices would be responsible for fetching batches of
names from Kafka and processing each batch separately.
- The results from the processed batches (for a single grouping task) can be later
merged together.
- We can scale the number of microservices depending on the load.
- If the size of input data is very large, we probably shouldn't store it in a
database. We could store e.g. a path to a file containing input data.
