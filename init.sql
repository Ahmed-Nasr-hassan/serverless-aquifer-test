-- Initialize PostgreSQL database for Aquifer Management System
-- This script runs when the container starts for the first time

-- Create extensions that might be useful
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create a schema for the application (optional, but good practice)
CREATE SCHEMA IF NOT EXISTS aquifer;

-- Grant permissions to the user
GRANT ALL PRIVILEGES ON SCHEMA aquifer TO aquifer_user;
GRANT ALL PRIVILEGES ON DATABASE aquifer_db TO aquifer_user;
