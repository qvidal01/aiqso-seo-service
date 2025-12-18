-- Initialize AIQSO SEO Service Database
-- This script runs on first container startup

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE aiqso_seo TO seo_user;

-- Create indexes for common queries (Alembic will handle table creation)
-- These are additional performance indexes

-- Note: Actual table creation is handled by Alembic migrations
-- Run: docker-compose exec backend alembic upgrade head
