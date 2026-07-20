# LibStream

LibStream is a library management API built with FastAPI and SQLAlchemy. It helps users register, log in, browse books, request new books, borrow books, and return them. Admin users can manage users, books, book requests, and overdue returns.

## What this application includes

- User authentication and authorization with JWT
- Book search by name or ID
- View available books and book details
- Request new books
- Borrow and return books
- Admin tools for managing books, users, requests, and overdue items
- Interactive API docs via Swagger UI and ReDoc

## Tech stack

- Python 3.13
- FastAPI
- SQLAlchemy (async)
- Pydantic
- JWT authentication
- PostgreSQL-compatible database via SQLAlchemy

## Project structure

- app/main.py: application entry point and router registration
- app/db/auth.py: user registration and login
- app/db/non_user_operation.py: public book search and availability endpoints
- app/db/user_operation.py: authenticated user actions such as borrow/return and requests
- app/admin_operations.py: admin management endpoints
- app/api/dependencies.py: authentication and authorization helpers

## Environment variables

Create a .env file in the project root with values like the following:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=your_database_url
PROJECT_URL=http://127.0.0.1:8000 (localhost yet)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=LibStream
VERSION=1.2.0
DEBUG=False
```

## How to run the project

1. Create and activate a virtual environment

   ```bash
   python3 -m venv LibStreamenv
   source LibStreamenv/bin/activate
   ```
2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```
3. Start the application

   ```bash
   uvicorn app.main:app --reload
   ```
4. Open the API documentation

   - Swagger UI: http://127.0.0.1:8000/docs
   - ReDoc: http://127.0.0.1:8000/redoc

## How to use the API properly

1. Register a new user using the registration endpoint.
2. Log in to receive a JWT access token.
3. Use the token in the Authorization header as a Bearer token for protected endpoints.
4. For admin actions, use an account that has admin privileges.

> If you receive a 401 or 403 response, your token is missing, expired, or you do not have the required permissions.

## Endpoint guide

### Authentication

| Endpoint            | Method | Description                       | What you get                     | How to use                                                |
| ------------------- | ------ | --------------------------------- | -------------------------------- | --------------------------------------------------------- |
| /api/auth/register  | POST   | Register a new user account       | Returns the created user profile | Send name, username, email, and password in the JSON body |
| /api/auth/login     | POST   | Log in with username and password | Returns an access token          | Use form-data with username and password                  |
| /api/protected-data | GET    | Check that a JWT token is valid   | Returns a protected message      | Send the Bearer token in the Authorization header         |

### Public book operations

| Endpoint                           | Method | Description                             | What you get                          | How to use                                              |
| ---------------------------------- | ------ | --------------------------------------- | ------------------------------------- | ------------------------------------------------------- |
| /operation/books/search-by-name    | GET    | Search books by name                    | A list of matching books              | Pass bookname as a query parameter, optionally category |
| /operation/books/search-by-id/{id} | GET    | Get a single book by ID                 | One book object                       | Replace {id} with the book ID                           |
| /operation/books/available-books   | GET    | View books that are currently available | A list of unassigned books            | Call the endpoint without extra parameters              |
| /                                  | GET    | Home page / welcome route               | A welcome message and available books | Requires authentication                                 |

### User operations

| Endpoint                 | Method | Description                                 | What you get                                    | How to use                                  |
| ------------------------ | ------ | ------------------------------------------- | ----------------------------------------------- | ------------------------------------------- |
| /user/my-requested-books | GET    | View books the current user has requested   | A list of requested books                       | Requires a valid Bearer token               |
| /user/my-all-books       | GET    | View all books assigned to the current user | A list of borrowed books                        | Requires a valid Bearer token               |
| /user/requrest-new-book  | POST   | Request a new book                          | Creates a new book request record               | Send name, author, edition, and description |
| /user/book-return/{id}   | PUT    | Return a borrowed book                      | A success message after the return is processed | Replace {id} with the book ID               |
| /user/take-book/{id}     | PATCH  | Borrow an available book                    | Marks the book as assigned to the current user  | Replace {id} with the book ID               |

### Admin operations

| Endpoint                        | Method | Description                                            | What you get                               | How to use                                                         |
| ------------------------------- | ------ | ------------------------------------------------------ | ------------------------------------------ | ------------------------------------------------------------------ |
| /admin/get-all-user             | GET    | List all users                                         | A list of users                            | Requires admin privileges                                          |
| /admin/get-ban-user             | GET    | List banned users                                      | A list of inactive users                   | Requires admin privileges                                          |
| /admin/all-requested-books      | GET    | List all pending book requests                         | A list of requests                         | Requires admin privileges                                          |
| /admin/requested-books/{status} | GET    | Filter requested books by status                       | A list of requests for the provided status | Use values such as pending, approved, rejected, ordered, completed |
| /admin/not-returned-books       | GET    | Find books that were not returned after their due date | A list of overdue assignments              | Requires admin privileges                                          |
| /admin/add-book                 | POST   | Add a new book to the library                          | The created book object                    | Requires admin privileges                                          |
| /admin/create-admin-user        | POST   | Create another admin user                              | A success message and admin user details   | Requires admin privileges                                          |
| /admin/update-book/{id}         | PATCH  | Update book information                                | Updated book details                       | Requires admin privileges                                          |
| /admin/ban-user/{username}      | PATCH  | Ban a user account                                     | A success message and user details         | Requires admin privileges                                          |
| /admin/unban-user/{username}    | PATCH  | Unban a user account                                   | A success message and user details         | Requires admin privileges                                          |
| /admin/delete-book/{id}         | DELETE | Delete a book                                          | A success message                          | Requires admin privileges                                          |
| /admin/delete-user/{username}   | DELETE | Delete a user account                                  | A success message                          | Requires admin privileges                                          |

## Notes

- The application uses a JWT-based session model, so login is required before using most endpoints.
- The API documentation is the easiest place to explore the available endpoints interactively.
- For production deployments, use strong secret keys and a secure database configuration.
