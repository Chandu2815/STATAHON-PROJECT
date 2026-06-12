BEGIN;

CREATE TABLE IF NOT EXISTS survey_ai_activity (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(64) NOT NULL,
    title VARCHAR(255) NOT NULL,
    detail TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_survey_ai_activity_user_created
ON survey_ai_activity (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_survey_ai_activity_user_action_created
ON survey_ai_activity (user_id, action, created_at DESC);

COMMIT;
