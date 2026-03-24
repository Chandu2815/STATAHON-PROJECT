-- PostgreSQL Setup Script for Survey Data API
-- Run this script as postgres user to initialize the database

-- Step 1: Create the survey_db database
CREATE DATABASE survey_db
    WITH
    ENCODING 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Step 2: Connect to the new database and create tables
-- (You'll need to run: \c survey_db)

-- Create survey_data table
CREATE TABLE IF NOT EXISTS survey_data (
    id BIGSERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for created_at (for sorting/filtering)
CREATE INDEX IF NOT EXISTS idx_survey_data_created_at 
ON survey_data(created_at DESC);

-- Create index for JSONB queries (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_survey_data_gin 
ON survey_data USING gin(data);

-- Step 3: Grant permissions to postgres user
GRANT ALL PRIVILEGES ON DATABASE survey_db TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Verify tables were created
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM 
    information_schema.columns
WHERE 
    table_name = 'survey_data'
ORDER BY 
    ordinal_position;
