# User Management REST API

A REST API built with Flask and SQLite for managing user data. Seed data is loaded from a JSON file on first run.

---

## Setup

```bash
git clone <your-repo-url>
cd API_Flask
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
python app.py
```

The server starts at **http://127.0.0.1:5000**

---

## API Endpoints

| Method | Endpoint            | Description                              |
|--------|---------------------|------------------------------------------|
| GET    | /                   | Welcome message with endpoint list       |
| GET    | /api/users          | List users (pagination, search, sort)    |
| POST   | /api/users          | Create a new user                        |
| GET    | /api/users/{id}     | Get a user by ID                         |
| PUT    | /api/users/{id}     | Full update of a user                    |
| PATCH  | /api/users/{id}     | Partial update of a user                 |
| DELETE | /api/users/{id}     | Delete a user                            |
| GET    | /api/users/summary  | Statistics (total count, avg age, cities)|

### Query Parameters (GET /api/users)

| Parameter | Default | Description                                 | Example        |
|-----------|---------|---------------------------------------------|----------------|
| page      | 1       | Page number                                 | ?page=2        |
| limit     | 5       | Items per page                              | ?limit=10      |
| search    |         | Case-insensitive search on first/last name  | ?search=James  |
| sort      |         | Sort field (prefix `-` for descending)      | ?sort=-age     |

**Example:** `/api/users?page=1&limit=10&search=James&sort=-age`

---

## Running Tests

```bash
pytest test_app.py -v
```

---

## Project Structure

```
API_Flask/
├── app.py              Entry point, creates Flask app and registers routes
├── config.py           Database and logging settings
├── db.py               Database connection, table creation, seed loader
├── routes/
│   ├── __init__.py     Makes routes a Python package
│   └── users.py        All user API endpoints (Blueprint)
├── users.json          Sample user data (loaded on first run)
├── users.db            SQLite database (auto-created)
├── test_app.py         Automated tests
├── requirements.txt    Python dependencies
└── README.md           This file
```

---

## Tools Used

- **Python 3.10+**
- **Flask** — Web framework
- **SQLite** — File-based database
- **pytest** — Testing framework
