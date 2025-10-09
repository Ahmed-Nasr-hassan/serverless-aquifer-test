# Aquifer Management API

A FastAPI-based backend service for managing aquifer data and simulations.

## Project Structure

```
backend/
├── main.py              # FastAPI application entry point
├── database.py          # Database configuration and connection
├── requirements.txt     # Python dependencies
├── models/              # SQLAlchemy database models
│   └── __init__.py
├── schemas/             # Pydantic schemas for request/response validation
│   └── __init__.py
└── routers/             # API route handlers
    └── __init__.py
```

## Features

- **Simulation Management**: Create, read, update, and delete aquifer simulations
- **Data Management**: Store and manage aquifer measurement data
- **Optimization Results**: Track optimization results for simulations
- **RESTful API**: Clean REST endpoints with proper HTTP status codes
- **Data Validation**: Pydantic schemas for request/response validation
- **Database Integration**: SQLAlchemy ORM with support for multiple databases

## API Endpoints

### Simulations
- `POST /api/v1/simulations/` - Create a new simulation
- `GET /api/v1/simulations/` - Get all simulations (paginated)
- `GET /api/v1/simulations/{id}` - Get specific simulation
- `PUT /api/v1/simulations/{id}` - Update simulation
- `DELETE /api/v1/simulations/{id}` - Delete simulation

### Aquifer Data
- `POST /api/v1/data/` - Create new aquifer data
- `GET /api/v1/data/` - Get all aquifer data (paginated)
- `GET /api/v1/data/{id}` - Get specific aquifer data
- `PUT /api/v1/data/{id}` - Update aquifer data
- `DELETE /api/v1/data/{id}` - Delete aquifer data

### Optimization Results
- `POST /api/v1/optimization/` - Create optimization result
- `GET /api/v1/optimization/` - Get all optimization results
- `GET /api/v1/optimization/simulation/{id}` - Get results for specific simulation

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check endpoint

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export DATABASE_URL="postgresql://user:password@localhost/aquifer_db"
```

3. Run the application:
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## Database

The application uses SQLAlchemy ORM and supports multiple database backends:
- SQLite (default)
- PostgreSQL
- MySQL

Database tables are automatically created on application startup.

## Development

The API includes:
- Automatic API documentation at `/docs` (Swagger UI)
- Alternative documentation at `/redoc`
- CORS middleware for frontend integration
- Proper error handling with HTTP status codes
- Input validation using Pydantic schemas
