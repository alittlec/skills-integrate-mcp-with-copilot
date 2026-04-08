# Database Setup and Migration Guide

## Overview
This application now uses SQLModel/SQLAlchemy with SQLite for persistent data storage. Data survives server restarts.

## Architecture

### Database Layer (`src/database.py`)
- Configures SQLAlchemy engine
- Provides session factory via FastAPI dependency injection
- Supports SQLite (default) and PostgreSQL/MySQL via `DATABASE_URL` environment variable
- Automatic table creation on startup

### Data Models (`src/models.py`)
- **Student**: `email` (unique), `created_at`
- **Activity**: `name` (unique), `description`, `schedule`, `max_participants`, timestamps
- **Enrollment**: Many-to-many relationship between Student and Activity, prevents duplicates

### API Integration (`src/app.py`)
- Database session injected into endpoints via FastAPI `Depends()`
- Startup event calls `create_db_and_tables()` and `seed_database()`
- Default activities seeded on first startup with sample participants
- All existing API endpoints remain backward-compatible

## Local Development

### Setup
```bash
pip install -r requirements.txt
cd src
uvicorn app:app --reload
```

The database file `activities.db` will be created in the `src/` directory.

### Database Configuration

**SQLite (default)**
```bash
# No configuration needed - uses ./activities.db
```

**PostgreSQL**

Install a PostgreSQL DBAPI driver first (for example, `psycopg`):
```bash
pip install psycopg
export DATABASE_URL="postgresql+psycopg://user:password@localhost/school_activities"
```

**MySQL**

Install the PyMySQL driver first:
```bash
pip install pymysql
```
```bash
export DATABASE_URL="mysql+pymysql://user:password@localhost/school_activities"
```

Enable SQL query logging:
```bash
export SQL_ECHO=true
```

## Testing the Persistence

1. Sign up a student for an activity via `/activities/{name}/signup`
2. Stop the server (Ctrl+C)
3. Restart the server
4. Query `/activities` - the signup should still exist

## Future Enhancements

- **Migrations**: Use Alembic for schema versioning in production
- **Transactions**: Add savepoint/rollback handling for complex operations
- **Indexing**: Add database indexes on frequently queried fields
- **Constraints**: Add additional database constraints and validation rules as needed beyond the existing enrollment uniqueness constraint

## API Compatibility

All existing endpoints work as before:
- `GET /activities` - returns activities with participant lists
- `POST /activities/{name}/signup?email=...` - creates enrollment
- `DELETE /activities/{name}/unregister?email=...` - removes enrollment

Response format is unchanged for frontend compatibility.
